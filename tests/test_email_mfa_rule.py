from pathlib import Path

import pytest

from clinicshield.ingest import read_csv
from clinicshield.input_limits import InputError
from clinicshield.rule_engine import evaluate_software_rule
from clinicshield.rule_handlers import email_mfa
from clinicshield.rule_loader import load_rule
from clinicshield.schemas import Software


ROOT = Path(__file__).resolve().parents[1]


def make_software(**changes):
    data = {
        "asset_id": "CLOUD",
        "vendor": "Example Mail Vendor",
        "product": "Example Email",
        "version": "Unknown",
        "purpose": "email",
        "deployment": "cloud",
        "touches_phi": "Y",
        "mfa_enabled": "N",
    }
    data.update(changes)
    return Software(**data)


@pytest.mark.parametrize(
    "mfa,status",
    [
        ("N", "confirmed"),
        ("Unknown", "needs_review"),
        ("NA", "needs_review"),
    ],
)
def test_reports_mfa_gap_or_uncertainty(mfa, status):
    result = email_mfa(
        make_software(mfa_enabled=mfa),
        entity_id="software:1",
    )

    assert result is not None
    assert result.rule_id == "R12"
    assert result.entity_id == "software:1"
    assert result.status == status
    assert dict(result.evidence) == {
        "asset_id": "CLOUD",
        "vendor": "Example Mail Vendor",
        "product": "Example Email",
        "purpose": "email",
        "deployment": "cloud",
        "mfa_enabled": mfa,
    }


def test_enabled_mfa_does_not_trigger():
    assert email_mfa(
        make_software(mfa_enabled="Y"),
        entity_id="software:1",
    ) is None


@pytest.mark.parametrize(
    "purpose",
    ["ehr", "backup", "telehealth", "remote_access", "other"],
)
def test_other_software_purposes_do_not_trigger(purpose):
    assert email_mfa(
        make_software(purpose=purpose),
        entity_id="software:1",
    ) is None


def test_local_email_is_assessed():
    result = email_mfa(
        make_software(asset_id="TEST-SRV01", deployment="local"),
        entity_id="software:1",
    )

    assert result is not None
    assert result.status == "confirmed"


@pytest.mark.parametrize("touches_phi", ["Y", "N", "Unknown"])
def test_detection_does_not_depend_on_phi_flag(touches_phi):
    result = email_mfa(
        make_software(touches_phi=touches_phi),
        entity_id="software:1",
    )

    assert result is not None


@pytest.mark.parametrize("entity_id", ["", "   ", None, 123])
def test_requires_entry_identifier(entity_id):
    with pytest.raises(InputError, match="entry identifier"):
        email_mfa(make_software(), entity_id=entity_id)


@pytest.mark.parametrize(
    "mfa,severity",
    [("N", "High"), ("Unknown", "Info"), ("NA", "Info")],
)
def test_yaml_rule_runs_through_engine(mfa, severity):
    rule = load_rule(ROOT / "rules" / "R12.yaml")

    finding = evaluate_software_rule(
        rule,
        make_software(mfa_enabled=mfa),
        entity_id="software:1",
    )

    assert finding is not None
    assert finding.severity == severity
    assert finding.rule.review_status == "draft"


def test_does_not_modify_software():
    software = make_software()
    original = software.model_dump()

    email_mfa(software, entity_id="software:1")

    assert software.model_dump() == original


@pytest.mark.parametrize(
    "clinic,expected_products",
    [
        ("lakeview_dental", {"Clinic Email"}),
        ("southside_counseling", {"Work Email"}),
        ("westside_health", set()),
    ],
)
def test_matches_sample_software(clinic, expected_products):
    rule = load_rule(ROOT / "rules" / "R12.yaml")
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
    assert all(
        f.observation.status == "confirmed"
        and f.severity == "High"
        for f in findings
    )