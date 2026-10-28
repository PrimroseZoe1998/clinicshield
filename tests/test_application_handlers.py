from datetime import datetime, timedelta, timezone

import pytest

from clinicshield.application_evidence import ApplicationSupportEvidence
from clinicshield.application_handlers import application_support
from clinicshield.input_limits import InputError
from clinicshield.schemas import Software


NOW = datetime(2026, 10, 27, 12, tzinfo=timezone.utc)
MAX_AGE = timedelta(days=8)


def make_software(**changes):
    data = {
        "asset_id": "TEST-WS01",
        "vendor": "Example Vendor",
        "product": "Example Application",
        "version": "1.0",
        "purpose": "ehr",
        "deployment": "local",
        "touches_phi": "Y",
        "mfa_enabled": "Y",
    }
    data.update(changes)
    return Software(**data)


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


def evaluate(software, evidence):
    return application_support(
        software,
        evidence,
        entity_id="software:1",
        now=NOW,
        max_age=MAX_AGE,
    )


def test_confirms_matched_current_unsupported_release():
    result = evaluate(make_software(), make_evidence())

    assert result is not None
    assert result.rule_id == "R04"
    assert result.entity_id == "software:1"
    assert result.status == "confirmed"
    assert dict(result.evidence)["support_status"] == "unsupported"


def test_current_supported_release_does_not_trigger():
    assert evaluate(
        make_software(),
        make_evidence(support_status="supported"),
    ) is None


def test_missing_evidence_requires_review():
    result = evaluate(make_software(), None)

    assert result is not None
    assert result.status == "needs_review"


@pytest.mark.parametrize(
    "changes",
    [
        {"vendor": "Other Vendor"},
        {"product": "Other Product"},
        {"version": "2.0"},
        {"version": "v1.0"},
        {"version": "Unknown"},
        {"deployment": "cloud"},
        {"source_url": None},
        {"retrieved_at": None},
        {"source_generated_at": None},
        {"support_status": "unknown"},
        {"extended_support": "unknown"},
        {"extended_support": "active"},
    ],
)
def test_unresolved_evidence_never_confirms_gap(changes):
    result = evaluate(make_software(), make_evidence(**changes))

    assert result is not None
    assert result.status == "needs_review"
    assert dict(result.evidence)["support_status"] == "unknown"


def test_unknown_inventory_version_requires_review():
    result = evaluate(
        make_software(version="Unknown"), make_evidence()
    )

    assert result is not None
    assert result.status == "needs_review"


def test_name_normalization_preserves_exact_version_matching():
    result = evaluate(
        make_software(),
        make_evidence(
            vendor=" EXAMPLE   VENDOR ",
            product=" EXAMPLE APPLICATION ",
        ),
    )

    assert result is not None
    assert result.status == "confirmed"


@pytest.mark.parametrize(
    "field",
    ["retrieved_at", "source_generated_at"],
)
@pytest.mark.parametrize(
    "timestamp",
    [
        NOW - MAX_AGE - timedelta(microseconds=1),
        NOW + timedelta(seconds=1),
    ],
)
def test_stale_or_future_timestamps_require_review(field, timestamp):
    result = evaluate(
        make_software(), make_evidence(**{field: timestamp})
    )

    assert result is not None
    assert result.status == "needs_review"


def test_exact_freshness_boundary_is_accepted():
    result = evaluate(
        make_software(),
        make_evidence(
            retrieved_at=NOW - MAX_AGE,
            source_generated_at=NOW - MAX_AGE,
        ),
    )

    assert result is not None
    assert result.status == "confirmed"


def test_generation_after_retrieval_requires_review():
    result = evaluate(
        make_software(),
        make_evidence(
            retrieved_at=NOW - timedelta(hours=2),
            source_generated_at=NOW - timedelta(hours=1),
        ),
    )

    assert result is not None
    assert result.status == "needs_review"


def test_rejects_evidence_for_different_entry():
    with pytest.raises(ValueError, match="match the software entry"):
        evaluate(
            make_software(),
            make_evidence(software_entry_id="software:2"),
        )


@pytest.mark.parametrize("entity_id", ["", "   ", None, 123])
def test_requires_entry_identifier(entity_id):
    with pytest.raises(InputError, match="entry identifier"):
        application_support(
            make_software(),
            None,
            entity_id=entity_id,
            now=NOW,
            max_age=MAX_AGE,
        )


def test_cloud_release_can_be_assessed_with_matched_evidence():
    result = evaluate(
        make_software(asset_id="CLOUD", deployment="cloud"),
        make_evidence(deployment="cloud"),
    )

    assert result is not None
    assert result.status == "confirmed"


def test_stale_supported_claim_requires_review():
    result = evaluate(
        make_software(),
        make_evidence(
            support_status="supported",
            source_generated_at=NOW - timedelta(days=9),
        ),
    )

    assert result is not None
    assert result.status == "needs_review"


def test_does_not_modify_inputs():
    software = make_software()
    evidence = make_evidence()
    originals = (software.model_dump(), evidence.model_dump())

    evaluate(software, evidence)

    assert (software.model_dump(), evidence.model_dump()) == originals