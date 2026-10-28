from datetime import datetime, timezone
from pathlib import Path

import pytest

from clinicshield.application_evidence import ApplicationSupportEvidence
from clinicshield.assessment_evidence import AssessmentEvidence
from clinicshield.assessment_evidence_links import validate_evidence_links
from clinicshield.assessment_input import read_assessment
from clinicshield.credential_evidence import DefaultPasswordEvidence
from clinicshield.input_limits import InputError
from clinicshield.lifecycle_evidence import LifecycleEvidence
from clinicshield.segmentation_evidence import MedicalSeparationEvidence
from clinicshield.vulnerability_evidence import VulnerabilityEvidence


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 28, tzinfo=timezone.utc)


@pytest.fixture
def assessment():
    folder = ROOT / "samples" / "lakeview_dental"
    return read_assessment(
        checklist_json=(folder / "checklist.json").read_bytes(),
        followups_json=(folder / "followups.json").read_bytes(),
        assets_csv=(folder / "assets.csv").read_bytes(),
        software_csv=(folder / "software.csv").read_bytes(),
        services_csv=(folder / "services.csv").read_bytes(),
    )


@pytest.fixture
def records():
    return {
        "os_support": LifecycleEvidence(
            os_name="Windows",
            os_version="10 22H2",
            support_status="unknown",
            support_basis="Synthetic test evidence.",
            extended_support="unknown",
            source_url=None,
            retrieved_at=None,
            source_generated_at=None,
        ),
        "default_passwords": DefaultPasswordEvidence(
            asset_id="LV-WS01",
            applicability="Unknown",
            default_password_changed="Unknown",
            evidence_basis="Synthetic test evidence.",
            evidence_source="Test fixture",
            observed_at=NOW,
        ),
        "medical_separation": MedicalSeparationEvidence(
            asset_id="LV-MD01",
            separation_verified="Unknown",
            evidence_basis="Synthetic test evidence.",
            evidence_source="Test fixture",
            observed_at=NOW,
        ),
        "application_support": ApplicationSupportEvidence(
            software_entry_id="software:1",
            vendor="Example Dental Vendor",
            product="Practice Manager",
            version="Unknown",
            deployment="local",
            support_status="unknown",
            support_basis="Synthetic test evidence.",
            extended_support="unknown",
            source_url=None,
            retrieved_at=None,
            source_generated_at=None,
        ),
        "vulnerabilities": VulnerabilityEvidence(
            software_entry_id="software:1",
            record={
                "vulnerability_id": "CVE-2026-12345",
                "source": "Synthetic vulnerability fixture",
                "source_url": "https://example.org/advisory",
                "retrieved_at": NOW,
                "vendor": "Example Dental Vendor",
                "product": "Practice Manager",
                "version_rule": "exact",
                "affected_versions": ["1.0"],
            },
            record_status="active",
            source_generated_at=NOW,
        ),
    }


def bundle_for(field, key, record):
    value = (record,) if field == "vulnerabilities" else record
    return AssessmentEvidence(**{field: {key: value}})


def test_empty_evidence_bundle_is_allowed(assessment):
    validate_evidence_links(assessment, AssessmentEvidence())


@pytest.mark.parametrize(
    "field,key",
    [
        ("os_support", "LV-WS01"),
        ("default_passwords", "LV-WS01"),
        ("medical_separation", "LV-MD01"),
        ("application_support", "software:1"),
        ("vulnerabilities", "software:1"),
    ],
)
def test_accepts_correctly_linked_evidence(
    assessment, records, field, key
):
    validate_evidence_links(
        assessment, bundle_for(field, key, records[field])
    )


@pytest.mark.parametrize(
    "field",
    ["os_support", "default_passwords", "medical_separation"],
)
def test_rejects_unknown_asset_keys(assessment, records, field):
    with pytest.raises(InputError, match="unknown asset"):
        validate_evidence_links(
            assessment,
            bundle_for(field, "MISSING-ASSET", records[field]),
        )


@pytest.mark.parametrize(
    "field",
    ["application_support", "vulnerabilities"],
)
def test_rejects_unknown_software_keys(assessment, records, field):
    with pytest.raises(InputError, match="unknown software entry"):
        validate_evidence_links(
            assessment,
            bundle_for(field, "software:999", records[field]),
        )


@pytest.mark.parametrize(
    "field,key",
    [
        ("os_support", "LV-WS01"),
        ("default_passwords", "LV-WS01"),
        ("medical_separation", "LV-MD01"),
        ("application_support", "software:1"),
        ("vulnerabilities", "software:1"),
    ],
)
def test_rejects_wrong_evidence_types(assessment, field, key):
    with pytest.raises(InputError, match="unsupported type"):
        validate_evidence_links(
            assessment, bundle_for(field, key, "not evidence")
        )


@pytest.mark.parametrize(
    "field,key",
    [
        ("default_passwords", "LV-WS02"),
        ("medical_separation", "LV-WS01"),
    ],
)
def test_rejects_asset_key_record_mismatch(
    assessment, records, field, key
):
    with pytest.raises(InputError, match="key does not match"):
        validate_evidence_links(
            assessment, bundle_for(field, key, records[field])
        )


@pytest.mark.parametrize(
    "field",
    ["application_support", "vulnerabilities"],
)
def test_rejects_software_key_record_mismatch(
    assessment, records, field
):
    with pytest.raises(InputError, match="key does not match"):
        validate_evidence_links(
            assessment,
            bundle_for(field, "software:2", records[field]),
        )


def test_does_not_modify_assessment_or_evidence(assessment, records):
    evidence = bundle_for(
        "default_passwords", "LV-WS01", records["default_passwords"]
    )
    original_assets = [
        asset.model_dump() for asset in assessment.inventory.assets
    ]
    original_record = records["default_passwords"].model_dump()

    validate_evidence_links(assessment, evidence)

    assert [
        asset.model_dump() for asset in assessment.inventory.assets
    ] == original_assets
    assert evidence.default_passwords["LV-WS01"].model_dump() == original_record