import pytest

from clinicshield.input_limits import InputError
from clinicshield.rule_handlers import unknown_software_version
from clinicshield.schemas import Software


def make_software(**changes):
    data = {
        "asset_id": "TEST-WS01",
        "vendor": "Example Vendor",
        "product": "Example Product",
        "version": "Unknown",
        "purpose": "ehr",
        "deployment": "local",
        "touches_phi": "Y",
        "mfa_enabled": "Unknown",
    }
    data.update(changes)
    return Software(**data)


def test_unknown_version_requires_review():
    result = unknown_software_version(
        make_software(), entity_id="software:1"
    )

    assert result is not None
    assert result.rule_id == "R24"
    assert result.entity_id == "software:1"
    assert result.status == "needs_review"
    assert dict(result.evidence) == {
        "asset_id": "TEST-WS01",
        "vendor": "Example Vendor",
        "product": "Example Product",
        "version": "Unknown",
        "deployment": "local",
        "touches_phi": "Y",
    }


@pytest.mark.parametrize(
    "version",
    ["Unknown", "UNKNOWN", "N/A", "NA", "not known", "unspecified"],
)
def test_recognizes_unknown_version_markers(version):
    result = unknown_software_version(
        make_software(version=version),
        entity_id="software:1",
    )

    assert result is not None
    assert result.status == "needs_review"
    assert dict(result.evidence)["version"] == version


@pytest.mark.parametrize(
    "version",
    ["1.2.3", "v1.2.3", "01.02", "1.0-beta", "1.2+build.7"],
)
def test_known_version_does_not_trigger(version):
    assert unknown_software_version(
        make_software(version=version),
        entity_id="software:1",
    ) is None


def test_unknown_phi_access_remains_unknown():
    result = unknown_software_version(
        make_software(touches_phi="Unknown"),
        entity_id="software:1",
    )

    assert result is not None
    assert result.status == "needs_review"
    assert dict(result.evidence)["touches_phi"] == "Unknown"


def test_no_phi_access_is_outside_rule_scope():
    assert unknown_software_version(
        make_software(touches_phi="N"),
        entity_id="software:1",
    ) is None


@pytest.mark.parametrize("asset_id", ["", "CLOUD"])
def test_supports_cloud_software(asset_id):
    result = unknown_software_version(
        make_software(asset_id=asset_id, deployment="cloud"),
        entity_id="software:cloud:1",
    )

    assert result is not None
    assert result.entity_id == "software:cloud:1"
    assert dict(result.evidence)["deployment"] == "cloud"


def test_distinguishes_entries_on_same_device():
    first = unknown_software_version(
        make_software(product="Product A"),
        entity_id="software:1",
    )
    second = unknown_software_version(
        make_software(product="Product B"),
        entity_id="software:2",
    )

    assert first is not None
    assert second is not None
    assert first.entity_id != second.entity_id
    assert dict(first.evidence)["asset_id"] == dict(second.evidence)["asset_id"]


@pytest.mark.parametrize("entity_id", ["", "   ", None, 123])
def test_requires_valid_entry_identifier(entity_id):
    with pytest.raises(InputError, match="entry identifier"):
        unknown_software_version(
            make_software(), entity_id=entity_id
        )


def test_does_not_modify_software():
    software = make_software()
    original = software.model_dump()

    unknown_software_version(software, entity_id="software:1")

    assert software.model_dump() == original