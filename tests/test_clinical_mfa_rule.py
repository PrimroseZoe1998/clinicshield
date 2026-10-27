from pathlib import Path

import pytest

from clinicshield.ingest import read_csv
from clinicshield.input_limits import InputError
from clinicshield.rule_engine import evaluate_software_rule
from clinicshield.rule_handlers import clinical_system_mfa
from clinicshield.rule_loader import load_rule
from clinicshield.schemas import Software


ROOT = Path(__file__).resolve().parents[1]


def make_software(**changes):
    data = {
        "asset_id": "CLOUD",
        "vendor": "Example Vendor",
        "product": "Example Clinical System",
        "version": "Unknown",
        "purpose": "ehr",
        "deployment": "cloud",
        "touches_phi": "Y",
        "mfa_enabled": "N",
    }
    data.update(changes)
    return Software(**data)


@pytest.mark.parametrize(
    "purpose",
    ["ehr", "practice_management", "billing", "telehealth"],
)
@pytest.mark.parametrize(
    "mfa,expected",
    [
        ("Y", None),
        ("N", "confirmed"),
        ("Unknown", "needs_review"),
        ("NA", "needs_review"),
    ],
)
def test_clinical_purposes_and_mfa_statuses(purpose, mfa, expected):
    result = clinical_system_mfa(
        make_software(purpose=purpose, mfa_enabled=mfa),
        entity_id="software:1",
    )

    if expected is None:
        assert result is None
    else:
        assert result is not None
        assert result.rule_id == "R13"
        assert result.entity_id == "software:1"
        assert result.status == expected
        assert dict(result.evidence)["purpose"] == purpose
        assert dict(result.evidence)["mfa_enabled"] == mfa


@pytest.mark.parametrize(
    "purpose",
    ["email", "remote_access", "backup", "messaging", "other"],
)
def test_other_purposes_are_outside_scope(purpose):
    assert clinical_system_mfa(
        make_software(purpose=purpose),
        entity_id="software:1",
    ) is None


def test_local_clinical_software_is_assessed():
    result = clinical_system_mfa(
        make_software(asset_id="TEST-SRV01", deployment="local"),
        entity_id="software:1",
    )

    assert result is not None
    assert result.status == "confirmed"
    assert dict(result.evidence)["deployment"] == "local"


@pytest.mark.parametrize("entity_id", ["", "   ", None, 123])
def test_requires_entry_identifier(entity_id):
    with pytest.raises(InputError, match="entry identifier"):
        clinical_system_mfa(make_software(), entity_id=entity_id)


@pytest.mark.parametrize(
    "mfa,status,severity",
    [
        ("N", "confirmed", "High"),
        ("Unknown", "needs_review", "Info"),
        ("NA", "needs_review", "Info"),
    ],
)
def test_yaml_rule_runs_through_engine(mfa, status, severity):
    rule = load_rule(ROOT / "rules" / "R13.yaml")

    finding = evaluate_software_rule(
        rule,
        make_software(mfa_enabled=mfa),
        entity_id="software:1",
    )

    assert finding is not None
    assert finding.observation.status == status
    assert finding.severity == severity
    assert finding.rule.review_status == "draft"
    assert dict(finding.observation.evidence) == {
        "asset_id": "CLOUD",
        "vendor": "Example Vendor",
        "product": "Example Clinical System",
        "purpose": "ehr",
        "deployment": "cloud",
        "mfa_enabled": mfa,
    }


def test_does_not_modify_software():
    software = make_software()
    original = software.model_dump()

    clinical_system_mfa(software, entity_id="software:1")

    assert software.model_dump() == original


@pytest.mark.parametrize(
    "clinic,expected",
    [
        (
            "lakeview_dental",
            {"Practice Manager": ("needs_review", "Info")},
        ),
        ("southside_counseling", {}),
        ("westside_health", {}),
    ],
)
def test_matches_sample_software(clinic, expected):
    rule = load_rule(ROOT / "rules" / "R13.yaml")
    entries = read_csv(
        (ROOT / "samples" / clinic / "software.csv").read_bytes(),
        "software",
    )
    actual = {}
    finding_count = 0

    for index, software in enumerate(entries, start=1):
        finding = evaluate_software_rule(
            rule, software, entity_id=f"software:{index}"
        )
        if finding is not None:
            finding_count += 1
            actual[software.product] = (
                finding.observation.status,
                finding.severity,
            )

    assert actual == expected
    assert finding_count == len(expected)