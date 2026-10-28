from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from clinicshield.credential_evidence import DefaultPasswordEvidence


@pytest.fixture
def evidence_data():
    return {
        "asset_id": "TEST-RT01",
        "applicability": "Yes",
        "default_password_changed": "No",
        "evidence_basis": "Fictional administrator confirmation.",
        "evidence_source": "Synthetic test fixture",
        "observed_at": datetime(2026, 10, 27, tzinfo=timezone.utc),
    }


def test_preserves_setting_status_and_source(evidence_data):
    evidence = DefaultPasswordEvidence(**evidence_data)

    assert evidence.asset_id == "TEST-RT01"
    assert evidence.applicability == "Yes"
    assert evidence.default_password_changed == "No"
    assert evidence.evidence_source == "Synthetic test fixture"
    assert evidence.observed_at == evidence_data["observed_at"]


@pytest.mark.parametrize(
    "field",
    ["applicability", "default_password_changed"],
)
@pytest.mark.parametrize("answer", ["Yes", "No", "Unknown"])
def test_accepts_explicit_statuses(evidence_data, field, answer):
    evidence_data[field] = answer

    assert getattr(DefaultPasswordEvidence(**evidence_data), field) == answer


@pytest.mark.parametrize(
    "field",
    ["applicability", "default_password_changed"],
)
@pytest.mark.parametrize("answer", ["yes", "", True, None])
def test_rejects_invalid_statuses(evidence_data, field, answer):
    evidence_data[field] = answer

    with pytest.raises(ValidationError):
        DefaultPasswordEvidence(**evidence_data)


def test_preserves_missing_observation_time(evidence_data):
    evidence_data["observed_at"] = None

    assert DefaultPasswordEvidence(**evidence_data).observed_at is None


def test_rejects_observation_time_without_timezone(evidence_data):
    evidence_data["observed_at"] = datetime(2026, 10, 27)

    with pytest.raises(ValidationError, match="timezone"):
        DefaultPasswordEvidence(**evidence_data)


@pytest.mark.parametrize(
    "field",
    ["asset_id", "evidence_basis", "evidence_source"],
)
@pytest.mark.parametrize("value", ["", "   ", 123])
def test_rejects_invalid_required_text(evidence_data, field, value):
    evidence_data[field] = value

    with pytest.raises(ValidationError):
        DefaultPasswordEvidence(**evidence_data)


@pytest.mark.parametrize(
    "field",
    ["password", "default_password", "administrator_password"],
)
def test_rejects_credential_value_fields(evidence_data, field):
    evidence_data[field] = "dummy-test-value"

    with pytest.raises(ValidationError):
        DefaultPasswordEvidence(**evidence_data)


@pytest.mark.parametrize(
    "field",
    [
        "asset_id",
        "applicability",
        "default_password_changed",
        "evidence_basis",
        "evidence_source",
        "observed_at",
    ],
)
def test_requires_explicit_fields(evidence_data, field):
    del evidence_data[field]

    with pytest.raises(ValidationError):
        DefaultPasswordEvidence(**evidence_data)


def test_json_round_trip(evidence_data):
    evidence = DefaultPasswordEvidence(**evidence_data)

    assert DefaultPasswordEvidence.model_validate_json(
        evidence.model_dump_json()
    ) == evidence


def test_evidence_is_frozen(evidence_data):
    evidence = DefaultPasswordEvidence(**evidence_data)

    with pytest.raises(ValidationError):
        evidence.default_password_changed = "Yes"