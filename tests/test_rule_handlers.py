import pytest

from clinicshield.rule_handlers import portable_encryption
from clinicshield.schemas import Asset


def make_asset(**changes):
    data = {
        "asset_id": "TEST-LT01",
        "asset_name": "Test laptop",
        "asset_type": "laptop",
        "os_name": "Example OS",
        "os_version": "1.0",
        "touches_phi": "Y",
        "internet_facing": "N",
        "encrypted": "N",
    }
    data.update(changes)
    return Asset(**data)


def test_disabled_encryption_is_confirmed():
    result = portable_encryption(make_asset(encrypted="N"))

    assert result is not None
    assert result.rule_id == "R05"
    assert result.entity_id == "TEST-LT01"
    assert result.status == "confirmed"
    assert dict(result.evidence) == {
        "asset_id": "TEST-LT01",
        "portable": "Y",
        "encrypted": "N",
    }


def test_unknown_encryption_requires_review():
    result = portable_encryption(make_asset(encrypted="Unknown"))

    assert result is not None
    assert result.status == "needs_review"
    assert dict(result.evidence)["encrypted"] == "Unknown"


def test_enabled_encryption_does_not_trigger():
    assert portable_encryption(make_asset(encrypted="Y")) is None


@pytest.mark.parametrize("encrypted", ["Y", "N", "Unknown"])
def test_nonportable_asset_does_not_trigger(encrypted):
    asset = make_asset(portable="N", encrypted=encrypted)

    assert portable_encryption(asset) is None


@pytest.mark.parametrize("asset_type", ["laptop", "tablet", "phone"])
def test_uses_inferred_portability(asset_type):
    asset = make_asset(asset_type=asset_type)

    result = portable_encryption(asset)

    assert result is not None
    assert result.status == "confirmed"
    assert dict(result.evidence)["portable"] == "Y"


def test_explicit_portability_overrides_asset_type():
    asset = make_asset(asset_type="workstation", portable="Y")

    assert portable_encryption(asset) is not None


def test_nonportable_inference_does_not_trigger():
    asset = make_asset(asset_type="workstation")

    assert portable_encryption(asset) is None


@pytest.mark.parametrize("touches_phi", ["Y", "N", "Unknown"])
def test_detection_does_not_depend_on_phi_flag(touches_phi):
    result = portable_encryption(make_asset(touches_phi=touches_phi))

    assert result is not None
    assert result.status == "confirmed"


def test_detection_does_not_modify_asset():
    asset = make_asset(encrypted="Unknown")
    original = asset.model_dump()

    portable_encryption(asset)

    assert asset.model_dump() == original