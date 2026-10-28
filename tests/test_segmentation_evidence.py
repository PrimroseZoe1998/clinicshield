from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from clinicshield.segmentation_evidence import MedicalSeparationEvidence


@pytest.fixture
def evidence_data():
    return {
        "asset_id": "TEST-MD01",
        "separation_verified": "No",
        "evidence_basis": "Fictional network administrator observation.",
        "evidence_source": "Synthetic test fixture",
        "observed_at": datetime(2026, 10, 27, tzinfo=timezone.utc),
    }


def test_preserves_status_and_source(evidence_data):
    evidence = MedicalSeparationEvidence(**evidence_data)

    assert evidence.asset_id == "TEST-MD01"
    assert evidence.separation_verified == "No"
    assert evidence.evidence_basis == evidence_data["evidence_basis"]
    assert evidence.evidence_source == "Synthetic test fixture"
    assert evidence.observed_at == evidence_data["observed_at"]


@pytest.mark.parametrize("status", ["Yes", "No", "Unknown"])
def test_accepts_explicit_statuses(evidence_data, status):
    evidence_data["separation_verified"] = status

    assert MedicalSeparationEvidence(
        **evidence_data
    ).separation_verified == status


@pytest.mark.parametrize("status", ["yes", "", True, None, "medical"])
def test_rejects_invalid_status(evidence_data, status):
    evidence_data["separation_verified"] = status

    with pytest.raises(ValidationError):
        MedicalSeparationEvidence(**evidence_data)


def test_preserves_missing_observation_time(evidence_data):
    evidence_data["observed_at"] = None

    assert MedicalSeparationEvidence(**evidence_data).observed_at is None


def test_rejects_time_without_timezone(evidence_data):
    evidence_data["observed_at"] = datetime(2026, 10, 27)

    with pytest.raises(ValidationError, match="timezone"):
        MedicalSeparationEvidence(**evidence_data)


@pytest.mark.parametrize(
    "field",
    ["asset_id", "evidence_basis", "evidence_source"],
)
@pytest.mark.parametrize("value", ["", "   ", 123])
def test_rejects_invalid_required_text(evidence_data, field, value):
    evidence_data[field] = value

    with pytest.raises(ValidationError):
        MedicalSeparationEvidence(**evidence_data)


@pytest.mark.parametrize(
    "field",
    [
        "asset_id",
        "separation_verified",
        "evidence_basis",
        "evidence_source",
        "observed_at",
    ],
)
def test_requires_explicit_fields(evidence_data, field):
    del evidence_data[field]

    with pytest.raises(ValidationError):
        MedicalSeparationEvidence(**evidence_data)


def test_rejects_segment_label_as_extra_evidence_field(evidence_data):
    evidence_data["network_segment"] = "medical"

    with pytest.raises(ValidationError):
        MedicalSeparationEvidence(**evidence_data)


def test_json_round_trip(evidence_data):
    evidence = MedicalSeparationEvidence(**evidence_data)

    assert MedicalSeparationEvidence.model_validate_json(
        evidence.model_dump_json()
    ) == evidence


def test_evidence_is_frozen(evidence_data):
    evidence = MedicalSeparationEvidence(**evidence_data)

    with pytest.raises(ValidationError):
        evidence.separation_verified = "Yes"