from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from clinicshield import rule_engine
from clinicshield.application_evidence import ApplicationSupportEvidence
from clinicshield.ingest import read_csv
from clinicshield.rule_engine import evaluate_software_support_rule
from clinicshield.rule_handlers import RuleObservation
from clinicshield.rule_loader import load_rule
from clinicshield.rule_models import RuleDefinition
from clinicshield.schemas import Software


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 27, 12, tzinfo=timezone.utc)


@pytest.fixture
def rule():
    return load_rule(ROOT / "rules" / "R04.yaml")


def make_software():
    return Software(
        asset_id="TEST-WS01",
        vendor="Example Vendor",
        product="Example Application",
        version="1.0",
        purpose="ehr",
        deployment="local",
        touches_phi="Y",
        mfa_enabled="Y",
    )


def make_evidence(**changes):
    data = {
        "software_entry_id": "software:1",
        "vendor": "Example Vendor",
        "product": "Example Application",
        "version": "1.0",
        "deployment": "local",
        "support_status": "unsupported",
        "support_basis": "Fictional vendor support statement.",
        "extended_support": "confirmed_absent",
        "source_url": "https://example.org/support",
        "retrieved_at": NOW,
        "source_generated_at": NOW,
    }
    data.update(changes)
    return ApplicationSupportEvidence(**data)


def evaluate(rule, software, evidence, entity_id="software:1"):
    return evaluate_software_support_rule(
        rule,
        software,
        evidence,
        entity_id=entity_id,
        now=NOW,
        max_age=timedelta(days=8),
    )


def change_rule(rule, **changes):
    data = rule.model_dump()
    data.update(changes)
    return RuleDefinition.model_validate(data)


def test_yaml_rule_produces_confirmed_finding(rule):
    finding = evaluate(rule, make_software(), make_evidence())

    assert finding is not None
    assert finding.observation.rule_id == "R04"
    assert finding.observation.entity_id == "software:1"
    assert finding.observation.status == "confirmed"
    assert finding.severity == "High"
    assert finding.rule.review_status == "draft"


def test_missing_evidence_requires_review(rule):
    finding = evaluate(rule, make_software(), None)

    assert finding is not None
    assert finding.observation.status == "needs_review"
    assert finding.severity == "Info"


def test_supported_release_produces_no_finding(rule):
    assert evaluate(
        rule,
        make_software(),
        make_evidence(support_status="supported"),
    ) is None


def test_stale_evidence_requires_review(rule):
    finding = evaluate(
        rule,
        make_software(),
        make_evidence(
            source_generated_at=NOW - timedelta(days=9)
        ),
    )

    assert finding is not None
    assert finding.observation.status == "needs_review"


def test_severity_comes_from_definition(rule):
    configured = change_rule(rule, severity="Medium")

    finding = evaluate(configured, make_software(), make_evidence())

    assert finding is not None
    assert finding.severity == "Medium"


@pytest.mark.parametrize(
    "changes",
    [
        {"rule_id": "R03"},
        {"handler": "unregistered_handler"},
        {"kind": "checklist"},
    ],
)
def test_rejects_unregistered_combinations(rule, changes):
    with pytest.raises(ValueError, match="registration"):
        evaluate(
            change_rule(rule, **changes),
            make_software(),
            make_evidence(),
        )


def test_rejects_missing_required_evidence(rule):
    configured = change_rule(
        rule,
        evidence_fields=(*rule.evidence_fields, "missing_field"),
    )

    with pytest.raises(ValueError, match="required evidence"):
        evaluate(configured, make_software(), make_evidence())


@pytest.mark.parametrize(
    "returned_rule,returned_entity,message",
    [
        ("R03", "software:1", "different rule ID"),
        ("R04", "software:other", "different software entry ID"),
    ],
)
def test_rejects_incorrect_handler_identity(
    rule, monkeypatch, returned_rule, returned_entity, message
):
    def incorrect_handler(
        software, evidence, *, entity_id, now, max_age
    ):
        return RuleObservation(
            rule_id=returned_rule,
            entity_id=returned_entity,
            status="confirmed",
            evidence=(),
        )

    monkeypatch.setitem(
        rule_engine.APPLICATION_SUPPORT_HANDLERS,
        ("R04", "application_support", "technical"),
        incorrect_handler,
    )

    with pytest.raises(ValueError, match=message):
        evaluate(rule, make_software(), make_evidence())


@pytest.mark.parametrize(
    "clinic",
    [
        "lakeview_dental",
        "southside_counseling",
        "westside_health",
    ],
)
def test_samples_without_support_evidence_require_review(rule, clinic):
    entries = read_csv(
        (ROOT / "samples" / clinic / "software.csv").read_bytes(),
        "software",
    )
    findings = []

    for index, software in enumerate(entries, start=1):
        finding = evaluate(
            rule, software, None, entity_id=f"software:{index}"
        )
        assert finding is not None
        findings.append(finding)

    assert len(findings) == len(entries)
    assert all(
        finding.observation.status == "needs_review"
        and finding.severity == "Info"
        for finding in findings
    )
    assert len({
        finding.observation.entity_id for finding in findings
    }) == len(entries)