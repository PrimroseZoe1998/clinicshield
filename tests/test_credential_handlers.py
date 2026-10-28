from datetime import datetime, timedelta, timezone

import pytest

from clinicshield.credential_evidence import DefaultPasswordEvidence
from clinicshield.credential_handlers import default_admin_password
from clinicshield.schemas import Asset


NOW = datetime(2026, 10, 27, 12, tzinfo=timezone.utc)
MAX_AGE = timedelta(days=8)


@pytest.fixture
def asset():
    return Asset(
        asset_id="TEST-RT01",
        asset_name="Test router",
        asset_type="network_device",
        os_name="Example firmware",
        os_version="1.0",
        touches_phi="Unknown",
        internet_facing="N",
        encrypted="Unknown",
    )


def make_evidence(**changes):
    data = {
        "asset_id": "TEST-RT01",
        "applicability": "Yes",
        "default_password_changed": "No",
        "evidence_basis": "Fictional administrator confirmation.",
        "evidence_source": "Synthetic test fixture",
        "observed_at": NOW,
    }
    data.update(changes)
    return DefaultPasswordEvidence(**data)


def evaluate(asset, evidence):
    return default_admin_password(
        asset, evidence, now=NOW, max_age=MAX_AGE
    )


@pytest.mark.parametrize(
    "applicability,changed,expected",
    [
        ("Yes", "Yes", None),
        ("Yes", "No", "confirmed"),
        ("Yes", "Unknown", "needs_review"),
        ("No", "Yes", None),
        ("No", "No", None),
        ("No", "Unknown", None),
        ("Unknown", "Yes", "needs_review"),
        ("Unknown", "No", "needs_review"),
        ("Unknown", "Unknown", "needs_review"),
    ],
)
def test_current_status_combinations(
    asset, applicability, changed, expected
):
    result = evaluate(
        asset,
        make_evidence(
            applicability=applicability,
            default_password_changed=changed,
        ),
    )

    if expected is None:
        assert result is None
    else:
        assert result is not None
        assert result.rule_id == "R10"
        assert result.entity_id == asset.asset_id
        assert result.status == expected
        assert dict(result.evidence)["applicability"] == applicability
        assert dict(result.evidence)["default_password_changed"] == changed


def test_missing_evidence_requires_review(asset):
    result = evaluate(asset, None)

    assert result is not None
    assert result.status == "needs_review"
    assert dict(result.evidence)["applicability"] == "Unknown"
    assert dict(result.evidence)["observed_at"] == ""


@pytest.mark.parametrize(
    "observed_at",
    [
        None,
        NOW - MAX_AGE - timedelta(microseconds=1),
        NOW + timedelta(seconds=1),
    ],
)
@pytest.mark.parametrize(
    "changes",
    [
        {"applicability": "Yes", "default_password_changed": "No"},
        {"applicability": "Yes", "default_password_changed": "Yes"},
        {"applicability": "No", "default_password_changed": "Unknown"},
    ],
)
def test_unresolved_freshness_never_confirms_or_clears(
    asset, observed_at, changes
):
    result = evaluate(
        asset,
        make_evidence(observed_at=observed_at, **changes),
    )

    assert result is not None
    assert result.status == "needs_review"
    assert "freshness" in dict(result.evidence)["evidence_basis"]


def test_accepts_exact_freshness_boundary(asset):
    result = evaluate(
        asset, make_evidence(observed_at=NOW - MAX_AGE)
    )

    assert result is not None
    assert result.status == "confirmed"


def test_rejects_evidence_for_different_asset(asset):
    with pytest.raises(ValueError, match="match the asset"):
        evaluate(asset, make_evidence(asset_id="OTHER-ASSET"))


def test_preserves_source_without_credential_values(asset):
    result = evaluate(asset, make_evidence())

    assert result is not None
    assert dict(result.evidence) == {
        "asset_id": "TEST-RT01",
        "applicability": "Yes",
        "default_password_changed": "No",
        "evidence_basis": "Fictional administrator confirmation.",
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
def test_rejects_invalid_clock_configuration(asset, now, max_age):
    with pytest.raises(ValueError):
        default_admin_password(
            asset, None, now=now, max_age=max_age
        )


def test_does_not_modify_inputs(asset):
    evidence = make_evidence()
    original_asset = asset.model_dump()
    original_evidence = evidence.model_dump()

    evaluate(asset, evidence)

    assert asset.model_dump() == original_asset
    assert evidence.model_dump() == original_evidence