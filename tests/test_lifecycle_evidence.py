from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from clinicshield.lifecycle_evidence import LifecycleEvidence


@pytest.fixture
def evidence_data():
    return {
        "os_name": "Example OS",
        "os_version": "1.0",
        "support_status": "unsupported",
        "support_basis": "Release support ended; no extended coverage.",
        "extended_support": "confirmed_absent",
        "source_url": "https://example.org/support",
        "retrieved_at": datetime(2026, 10, 27, tzinfo=timezone.utc),
        "source_generated_at": datetime(
            2026, 10, 26, tzinfo=timezone.utc
        ),
    }


def test_preserves_identity_and_support_evidence(evidence_data):
    evidence = LifecycleEvidence(**evidence_data)

    assert evidence.os_name == "Example OS"
    assert evidence.os_version == "1.0"
    assert evidence.support_status == "unsupported"
    assert evidence.extended_support == "confirmed_absent"
    assert str(evidence.source_url) == "https://example.org/support"
    assert evidence.retrieved_at != evidence.source_generated_at


def test_preserves_explicit_missing_source_details(evidence_data):
    evidence_data.update(
        support_status="unknown",
        extended_support="unknown",
        source_url=None,
        retrieved_at=None,
        source_generated_at=None,
    )

    evidence = LifecycleEvidence(**evidence_data)

    assert evidence.source_url is None
    assert evidence.retrieved_at is None
    assert evidence.source_generated_at is None
    assert evidence.support_status == "unknown"


@pytest.mark.parametrize(
    "status",
    ["supported", "unsupported", "unknown"],
)
def test_accepts_support_statuses(evidence_data, status):
    evidence_data["support_status"] = status

    assert LifecycleEvidence(**evidence_data).support_status == status


@pytest.mark.parametrize(
    "status",
    ["not_applicable", "confirmed_absent", "active", "unknown"],
)
def test_accepts_extended_support_statuses(evidence_data, status):
    evidence_data["extended_support"] = status

    assert LifecycleEvidence(**evidence_data).extended_support == status


@pytest.mark.parametrize(
    "field",
    ["os_name", "os_version", "support_basis"],
)
@pytest.mark.parametrize("value", ["", "   ", None, 123])
def test_rejects_invalid_required_text(evidence_data, field, value):
    evidence_data[field] = value

    with pytest.raises(ValidationError):
        LifecycleEvidence(**evidence_data)


@pytest.mark.parametrize(
    "field",
    ["retrieved_at", "source_generated_at"],
)
def test_requires_timezone(evidence_data, field):
    evidence_data[field] = datetime(2026, 10, 27)

    with pytest.raises(ValidationError, match="timezone"):
        LifecycleEvidence(**evidence_data)


@pytest.mark.parametrize(
    "changes",
    [
        {"support_status": "safe"},
        {"extended_support": "probably"},
        {"source_url": "not a URL"},
        {"unexpected": "value"},
    ],
)
def test_rejects_invalid_fields(evidence_data, changes):
    evidence_data.update(changes)

    with pytest.raises(ValidationError):
        LifecycleEvidence(**evidence_data)


@pytest.mark.parametrize(
    "field",
    [
        "os_name",
        "os_version",
        "support_status",
        "support_basis",
        "extended_support",
        "source_url",
        "retrieved_at",
        "source_generated_at",
    ],
)
def test_requires_explicit_fields(evidence_data, field):
    del evidence_data[field]

    with pytest.raises(ValidationError):
        LifecycleEvidence(**evidence_data)


def test_json_round_trip(evidence_data):
    evidence = LifecycleEvidence(**evidence_data)

    assert LifecycleEvidence.model_validate_json(
        evidence.model_dump_json()
    ) == evidence


def test_evidence_is_frozen(evidence_data):
    evidence = LifecycleEvidence(**evidence_data)

    with pytest.raises(ValidationError):
        evidence.support_status = "supported"