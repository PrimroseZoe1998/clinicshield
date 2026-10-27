from datetime import datetime, timedelta, timezone

import pytest

from clinicshield.lifecycle_evidence import LifecycleEvidence
from clinicshield.lifecycle_handlers import operating_system_support
from clinicshield.schemas import Asset


NOW = datetime(2026, 10, 27, 12, tzinfo=timezone.utc)
MAX_AGE = timedelta(days=8)


@pytest.fixture
def asset():
    return Asset(
        asset_id="TEST-WS01",
        asset_name="Test workstation",
        asset_type="workstation",
        os_name="Example OS",
        os_version="1.0",
        touches_phi="Y",
        internet_facing="N",
        encrypted="Y",
    )


def make_evidence(**changes):
    data = {
        "os_name": "Example OS",
        "os_version": "1.0",
        "support_status": "unsupported",
        "support_basis": "Support ended; no extended coverage.",
        "extended_support": "confirmed_absent",
        "source_url": "https://example.org/support",
        "retrieved_at": NOW,
        "source_generated_at": NOW - timedelta(hours=1),
    }
    data.update(changes)
    return LifecycleEvidence(**data)


def evaluate(asset, evidence):
    return operating_system_support(
        asset, evidence, now=NOW, max_age=MAX_AGE
    )


def test_confirms_matched_current_unsupported_release(asset):
    result = evaluate(asset, make_evidence())

    assert result is not None
    assert result.rule_id == "R03"
    assert result.entity_id == asset.asset_id
    assert result.status == "confirmed"
    assert dict(result.evidence)["support_status"] == "unsupported"
    assert dict(result.evidence)["support_basis"] == (
        "Support ended; no extended coverage."
    )


def test_current_supported_release_does_not_trigger(asset):
    assert evaluate(
        asset, make_evidence(support_status="supported")
    ) is None


def test_missing_evidence_requires_review(asset):
    result = evaluate(asset, None)

    assert result is not None
    assert result.status == "needs_review"
    assert dict(result.evidence)["support_status"] == "unknown"


@pytest.mark.parametrize(
    "changes",
    [
        {"os_name": "Other OS"},
        {"os_version": "2.0"},
        {"os_version": "v1.0"},
        {"os_version": "Unknown"},
        {"source_url": None},
        {"retrieved_at": None},
        {"source_generated_at": None},
        {"support_status": "unknown"},
        {"extended_support": "unknown"},
        {"extended_support": "active"},
    ],
)
def test_unresolved_evidence_never_confirms_unsupported(asset, changes):
    result = evaluate(asset, make_evidence(**changes))

    assert result is not None
    assert result.status == "needs_review"
    assert dict(result.evidence)["support_status"] == "unknown"
    assert dict(result.evidence)["support_basis"]


@pytest.mark.parametrize(
    "timestamp_field",
    ["retrieved_at", "source_generated_at"],
)
@pytest.mark.parametrize(
    "timestamp",
    [
        NOW - MAX_AGE - timedelta(microseconds=1),
        NOW + timedelta(seconds=1),
    ],
)
def test_stale_or_future_timestamps_require_review(
    asset, timestamp_field, timestamp
):
    result = evaluate(
        asset, make_evidence(**{timestamp_field: timestamp})
    )

    assert result is not None
    assert result.status == "needs_review"


def test_exact_freshness_boundary_is_accepted(asset):
    result = evaluate(
        asset,
        make_evidence(
            retrieved_at=NOW - MAX_AGE,
            source_generated_at=NOW - MAX_AGE,
        ),
    )

    assert result is not None
    assert result.status == "confirmed"


def test_generation_after_retrieval_requires_review(asset):
    result = evaluate(
        asset,
        make_evidence(
            retrieved_at=NOW - timedelta(hours=2),
            source_generated_at=NOW - timedelta(hours=1),
        ),
    )

    assert result is not None
    assert result.status == "needs_review"


def test_stale_supported_claim_requires_review(asset):
    result = evaluate(
        asset,
        make_evidence(
            support_status="supported",
            source_generated_at=NOW - timedelta(days=9),
        ),
    )

    assert result is not None
    assert result.status == "needs_review"


def test_normalizes_name_case_and_spacing(asset):
    result = evaluate(
        asset, make_evidence(os_name=" EXAMPLE   OS ")
    )

    assert result is not None
    assert result.status == "confirmed"


@pytest.mark.parametrize("field", ["os_name", "os_version"])
def test_unknown_asset_identity_requires_review(asset, field):
    data = asset.model_dump()
    data[field] = "Unknown"
    unresolved_asset = Asset.model_validate(data)

    result = evaluate(unresolved_asset, make_evidence())

    assert result is not None
    assert result.status == "needs_review"


@pytest.mark.parametrize(
    "now,max_age",
    [
        (NOW.replace(tzinfo=None), MAX_AGE),
        (NOW, timedelta(0)),
        (NOW, timedelta(seconds=-1)),
    ],
)
def test_rejects_invalid_clock_configuration(asset, now, max_age):
    with pytest.raises(ValueError):
        operating_system_support(
            asset, None, now=now, max_age=max_age
        )


def test_does_not_modify_inputs(asset):
    evidence = make_evidence()
    original_asset = asset.model_dump()
    original_evidence = evidence.model_dump()

    evaluate(asset, evidence)

    assert asset.model_dump() == original_asset
    assert evidence.model_dump() == original_evidence