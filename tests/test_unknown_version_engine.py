from pathlib import Path

import pytest

from clinicshield import rule_engine
from clinicshield.ingest import read_csv
from clinicshield.rule_engine import evaluate_software_rule
from clinicshield.rule_handlers import RuleObservation
from clinicshield.rule_loader import load_rule
from clinicshield.rule_models import RuleDefinition
from clinicshield.schemas import Software


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def rule():
    return load_rule(ROOT / "rules" / "R24.yaml")


def make_software(**changes):
    data = {
        "asset_id": "TEST-WS01",
        "vendor": "Example Vendor",
        "product": "Example Product",
        "version": "Unknown",
        "purpose": "ehr",
        "deployment": "local",
        "touches_phi": "Y",
        "mfa_enabled": "Unknown",
    }
    data.update(changes)
    return Software(**data)


def change_rule(rule, **changes):
    data = rule.model_dump()
    data.update(changes)
    return RuleDefinition.model_validate(data)


def test_unknown_version_produces_review_finding(rule):
    finding = evaluate_software_rule(
        rule, make_software(), entity_id="software:1"
    )

    assert finding is not None
    assert finding.observation.rule_id == "R24"
    assert finding.observation.entity_id == "software:1"
    assert finding.observation.status == "needs_review"
    assert finding.severity == "Info"
    assert finding.rule.review_status == "draft"


@pytest.mark.parametrize(
    "changes",
    [{"version": "1.2.3"}, {"touches_phi": "N"}],
)
def test_nontrigger_returns_no_finding(rule, changes):
    assert evaluate_software_rule(
        rule, make_software(**changes), entity_id="software:1"
    ) is None


def test_uses_configured_unknown_severity(rule):
    configured = change_rule(rule, unknown_severity="Low")

    finding = evaluate_software_rule(
        configured, make_software(), entity_id="software:1"
    )

    assert finding is not None
    assert finding.severity == "Low"


@pytest.mark.parametrize(
    "changes",
    [
        {"rule_id": "R04"},
        {"handler": "unregistered_handler"},
        {"kind": "checklist"},
    ],
)
def test_rejects_unregistered_combinations(rule, changes):
    with pytest.raises(ValueError, match="registration"):
        evaluate_software_rule(
            change_rule(rule, **changes),
            make_software(),
            entity_id="software:1",
        )


def test_rejects_missing_evidence(rule):
    configured = change_rule(
        rule,
        evidence_fields=(*rule.evidence_fields, "missing_field"),
    )

    with pytest.raises(ValueError, match="required evidence"):
        evaluate_software_rule(
            configured, make_software(), entity_id="software:1"
        )


@pytest.mark.parametrize(
    "returned_rule,returned_entity,message",
    [
        ("R04", "software:1", "different rule ID"),
        ("R24", "software:other", "different software entry ID"),
    ],
)
def test_rejects_incorrect_handler_identity(
    rule, monkeypatch, returned_rule, returned_entity, message
):
    def incorrect_handler(software, *, entity_id):
        return RuleObservation(
            rule_id=returned_rule,
            entity_id=returned_entity,
            status="needs_review",
            evidence=(),
        )

    monkeypatch.setitem(
        rule_engine.SOFTWARE_HANDLERS,
        ("R24", "unknown_software_version", "technical"),
        incorrect_handler,
    )

    with pytest.raises(ValueError, match=message):
        evaluate_software_rule(
            rule, make_software(), entity_id="software:1"
        )


@pytest.mark.parametrize(
    "clinic,expected_products",
    [
        (
            "lakeview_dental",
            {
                "Practice Manager",
                "Clinic Email",
                "Clinic Backup",
                "Remote Support",
            },
        ),
        (
            "southside_counseling",
            {
                "Counseling EHR",
                "Video Care",
                "Consumer Texting",
                "Work Email",
                "Personal Cloud Drive",
            },
        ),
        (
            "westside_health",
            {
                "Community EHR",
                "Work Email",
                "Clinic Billing",
                "Clinic Backup",
                "Site Management",
            },
        ),
    ],
)
def test_matches_sample_software(rule, clinic, expected_products):
    entries = read_csv(
        (ROOT / "samples" / clinic / "software.csv").read_bytes(),
        "software",
    )
    findings = []

    for index, software in enumerate(entries, start=1):
        finding = evaluate_software_rule(
            rule, software, entity_id=f"software:{index}"
        )
        if finding is not None:
            findings.append(finding)

    assert len(findings) == len(expected_products)
    assert {
        dict(f.observation.evidence)["product"] for f in findings
    } == expected_products
    assert len({
        f.observation.entity_id for f in findings
    }) == len(findings)
    assert all(
        f.observation.status == "needs_review"
        and f.severity == "Info"
        for f in findings
    )