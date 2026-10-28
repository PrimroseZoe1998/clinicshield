from datetime import datetime, timedelta, timezone

import pytest

from clinicshield.schemas import Asset
from clinicshield.segmentation_evidence import MedicalSeparationEvidence
from clinicshield.segmentation_handlers import medical_network_separation


NOW = datetime(2026, 10, 27, 12, tzinfo=timezone.utc)
MAX_AGE = timedelta(days=8)


def make_asset(**changes):
    data = {
        "asset_id": "TEST-MD01",
        "asset_name": "Test medical device",
        "asset_type": "medical_device",
        "os_name": "Example firmware",
        "os_version": "1.0",
        "touches_phi": "Y",
        "internet_facing": "N",
        "encrypted": "Unknown",
        "network_segment": "medical",
    }
    data.update(changes)
    return Asset(**data)


def make_evidence(**changes):
    data = {
        "asset_id": "TEST-MD01",
        "separation_verified": "No",
        "evidence_basis": "Fictional network administrator observation.",
        "evidence_source": "Synthetic test fixture",
        "observed_at": NOW,
    }
    data.update(changes)
    return MedicalSeparationEvidence(**data)


def evaluate(asset, evidence):
    return medical_network_separation(
        asset, evidence, now=NOW, max_age=MAX_AGE
    )


@pytest.mark.parametrize(
    "status,expected",
    [
        ("Yes", None),
        ("No", "confirmed"),
        ("Unknown", "needs_review"),
    ],
)
def test_current_separation_statuses(status, expected):
    result = evaluate(
        make_asset(),
        make_evidence(separation_verified=status),
    )

    if expected is None:
        assert result is None
    else:
        assert result is not None
        assert result.rule_id == "R11"
        assert result.entity_id == "TEST-MD01"
        assert result.status == expected
        assert dict(result.evidence)["separation_verified"] == status


@pytest.mark.parametrize("segment", ["medical", "clinic", "unknown"])
def test_segment_label_alone_cannot_resolve_separation(segment):
    result = evaluate(make_asset(network_segment=segment), None)

    assert result is not None
    assert result.status == "needs_review"
    assert dict(result.evidence)["network_segment"] == segment
    assert dict(result.evidence)["separation_verified"] == "Unknown"


@pytest.mark.parametrize(
    "asset_type",
    ["workstation", "server", "printer", "network_device"],
)
def test_nonmedical_assets_are_outside_scope(asset_type):
    assert evaluate(
        make_asset(asset_type=asset_type), None
    ) is None


@pytest.mark.parametrize("status", ["Yes", "No", "Unknown"])
@pytest.mark.parametrize(
    "observed_at",
    [
        None,
        NOW - MAX_AGE - timedelta(microseconds=1),
        NOW + timedelta(seconds=1),
    ],
)
def test_unresolved_freshness_requires_review(status, observed_at):
    result = evaluate(
        make_asset(),
        make_evidence(
            separation_verified=status,
            observed_at=observed_at,
        ),
    )

    assert result is not None
    assert result.status == "needs_review"
    assert "freshness" in dict(result.evidence)["evidence_basis"]


def test_exact_freshness_boundary_is_accepted():
    result = evaluate(
        make_asset(),
        make_evidence(observed_at=NOW - MAX_AGE),
    )

    assert result is not None
    assert result.status == "confirmed"


def test_rejects_evidence_for_different_asset():
    with pytest.raises(ValueError, match="match the asset"):
        evaluate(
            make_asset(),
            make_evidence(asset_id="OTHER-ASSET"),
        )


def test_preserves_source_and_asset_context():
    result = evaluate(make_asset(), make_evidence())

    assert result is not None
    assert dict(result.evidence) == {
        "asset_id": "TEST-MD01",
        "asset_type": "medical_device",
        "network_segment": "medical",
        "separation_verified": "No",
        "evidence_basis": "Fictional network administrator observation.",
        "evidence_source": "Synthetic test fixture",
        "observed_at": NOW.isoformat(),
    }


@pytest.mark.parametrize(
    "now,max_age",
    [
        (NOW.replace(tzinfo=None), MAX_AGE),
        (NOW, timedelta(0)),
        (NOW, timedelta(seconds=-1)),
    ],
)
def test_rejects_invalid_clock_configuration(now, max_age):
    with pytest.raises(ValueError):
        medical_network_separation(
            make_asset(), None, now=now, max_age=max_age
        )


def test_does_not_modify_inputs():
    asset = make_asset()
    evidence = make_evidence()
    original_asset = asset.model_dump()
    original_evidence = evidence.model_dump()

    evaluate(asset, evidence)

    assert asset.model_dump() == original_asset
    assert evidence.model_dump() == original_evidence