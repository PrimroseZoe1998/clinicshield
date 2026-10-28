from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from clinicshield.application_evidence import ApplicationSupportEvidence


@pytest.fixture
def evidence_data():
    return {
        "software_entry_id": "software:1",
        "vendor": "Example Vendor",
        "product": "Example Application",
        "version": "1.0",
        "deployment": "local",
        "support_status": "unsupported",
        "support_basis": "Fictional vendor support statement.",
        "extended_support": "confirmed_absent",
        "source_url": "https://example.org/support",
        "retrieved_at": datetime(2026, 10, 27, tzinfo=timezone.utc),
        "source_generated_at": datetime(
            2026, 10, 26, tzinfo=timezone.utc
        ),
    }


def test_preserves_software_identity_and_source(evidence_data):
    evidence = ApplicationSupportEvidence(**evidence_data)

    assert evidence.software_entry_id == "software:1"
    assert evidence.vendor == "Example Vendor"
    assert evidence.product == "Example Application"
    assert evidence.version == "1.0"
    assert evidence.deployment == "local"
    assert evidence.support_status == "unsupported"
    assert str(evidence.source_url) == "https://example.org/support"
    assert evidence.retrieved_at != evidence.source_generated_at


@pytest.mark.parametrize("deployment", ["local", "cloud"])
def test_accepts_deployment_types(evidence_data, deployment):
    evidence_data["deployment"] = deployment

    assert ApplicationSupportEvidence(
        **evidence_data
    ).deployment == deployment


def test_preserves_explicit_missing_source_details(evidence_data):
    evidence_data.update(
        support_status="unknown",
        source_url=None,
        retrieved_at=None,
        source_generated_at=None,
    )

    evidence = ApplicationSupportEvidence(**evidence_data)

    assert evidence.source_url is None
    assert evidence.retrieved_at is None
    assert evidence.source_generated_at is None


@pytest.mark.parametrize(
    "field",
    [
        "software_entry_id",
        "vendor",
        "product",
        "version",
        "support_basis",
    ],
)
@pytest.mark.parametrize("value", ["", "   ", 123])
def test_rejects_invalid_required_text(evidence_data, field, value):
    evidence_data[field] = value

    with pytest.raises(ValidationError):
        ApplicationSupportEvidence(**evidence_data)


@pytest.mark.parametrize(
    "field",
    ["retrieved_at", "source_generated_at"],
)
def test_requires_timezone(evidence_data, field):
    evidence_data[field] = datetime(2026, 10, 27)

    with pytest.raises(ValidationError, match="timezone"):
        ApplicationSupportEvidence(**evidence_data)


@pytest.mark.parametrize(
    "changes",
    [
        {"deployment": "hybrid"},
        {"support_status": "safe"},
        {"extended_support": "probably"},
        {"source_url": "not a URL"},
        {"unexpected": "value"},
    ],
)
def test_rejects_invalid_fields(evidence_data, changes):
    evidence_data.update(changes)

    with pytest.raises(ValidationError):
        ApplicationSupportEvidence(**evidence_data)


@pytest.mark.parametrize(
    "field",
    [
        "software_entry_id",
        "vendor",
        "product",
        "version",
        "deployment",
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
        ApplicationSupportEvidence(**evidence_data)


def test_json_round_trip(evidence_data):
    evidence = ApplicationSupportEvidence(**evidence_data)

    assert ApplicationSupportEvidence.model_validate_json(
        evidence.model_dump_json()
    ) == evidence


def test_evidence_is_frozen(evidence_data):
    evidence = ApplicationSupportEvidence(**evidence_data)

    with pytest.raises(ValidationError):
        evidence.support_status = "supported"