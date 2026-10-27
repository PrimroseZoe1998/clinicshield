from pathlib import Path

import pytest

from clinicshield.ingest import read_csv
from clinicshield.input_limits import InputError
from clinicshield.rule_engine import evaluate_software_rule
from clinicshield.rule_handlers import cloud_baa_status
from clinicshield.rule_loader import load_rule
from clinicshield.schemas import Software


ROOT = Path(__file__).resolve().parents[1]


def make_software(**changes):
    data = {
        "asset_id": "CLOUD",
        "vendor": "Example Vendor",
        "product": "Example Service",
        "version": "Unknown",
        "purpose": "ehr",
        "deployment": "cloud",
        "touches_phi": "Y",
        "mfa_enabled": "Y",
        "baa_signed": "N",
    }
    data.update(changes)
    return Software(**data)


@pytest.mark.parametrize(
    "touches_phi,baa_signed,expected",
    [
        ("Y", "Y", None),
        ("Y", "N", "confirmed"),
        ("Y", "Unknown", "needs_review"),
        ("Y", "NA", "needs_review"),
        ("Unknown", "Y", "needs_review"),
        ("Unknown", "N", "needs_review"),
        ("Unknown", "Unknown", "needs_review"),
        ("Unknown", "NA", "needs_review"),
        ("N", "Y", None),
        ("N", "N", None),
        ("N", "Unknown", None),
        ("N", "NA", None),
    ],
)
def test_cloud_status_combinations(touches_phi, baa_signed, expected):
    software = make_software(
        touches_phi=touches_phi,
        baa_signed=baa_signed,
    )

    result = cloud_baa_status(software, entity_id="software:1")

    if expected is None:
        assert result is None
    else:
        assert result is not None
        assert result.rule_id == "R17"
        assert result.entity_id == "software:1"
        assert result.status == expected
        assert dict(result.evidence) == {
            "asset_id": "CLOUD",
            "vendor": "Example Vendor",
            "product": "Example Service",
            "deployment": "cloud",
            "touches_phi": touches_phi,
            "baa_signed": baa_signed,
        }


@pytest.mark.parametrize("baa_signed", ["Y", "N", "Unknown", "NA"])
def test_local_software_is_outside_scope(baa_signed):
    software = make_software(
        asset_id="TEST-WS01",
        deployment="local",
        baa_signed=baa_signed,
    )

    assert cloud_baa_status(
        software, entity_id="software:1"
    ) is None


@pytest.mark.parametrize("entity_id", ["", "   ", None, 123])
def test_requires_entry_identifier(entity_id):
    with pytest.raises(InputError, match="entry identifier"):
        cloud_baa_status(make_software(), entity_id=entity_id)


@pytest.mark.parametrize(
    "baa_signed,status,severity",
    [
        ("N", "confirmed", "High"),
        ("Unknown", "needs_review", "Info"),
        ("NA", "needs_review", "Info"),
    ],
)
def test_yaml_rule_runs_through_engine(baa_signed, status, severity):
    rule = load_rule(ROOT / "rules" / "R17.yaml")

    finding = evaluate_software_rule(
        rule,
        make_software(baa_signed=baa_signed),
        entity_id="software:1",
    )

    assert finding is not None
    assert finding.observation.status == status
    assert finding.severity == severity
    assert finding.rule.review_status == "draft"


def test_does_not_modify_software():
    software = make_software()
    original = software.model_dump()

    cloud_baa_status(software, entity_id="software:1")

    assert software.model_dump() == original


@pytest.mark.parametrize(
    "clinic,expected_products",
    [
        ("lakeview_dental", set()),
        (
            "southside_counseling",
            {"Consumer Texting", "Personal Cloud Drive"},
        ),
        ("westside_health", set()),
    ],
)
def test_matches_sample_software(clinic, expected_products):
    rule = load_rule(ROOT / "rules" / "R17.yaml")
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