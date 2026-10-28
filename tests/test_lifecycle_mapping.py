import pytest
from pydantic import ValidationError

from clinicshield.lifecycle_mapping import OsReleaseMapping


@pytest.fixture
def mapping_data():
    return {
        "os_name": "Example OS",
        "os_version": "1.0 Enterprise",
        "product": "example-os",
        "release_name": "1",
        "mapping_basis": "Fictional vendor release mapping for tests.",
    }


def test_preserves_explicit_release_mapping(mapping_data):
    mapping = OsReleaseMapping(**mapping_data)

    assert mapping.os_name == "Example OS"
    assert mapping.os_version == "1.0 Enterprise"
    assert mapping.product == "example-os"
    assert mapping.release_name == "1"
    assert mapping.mapping_basis


def test_trims_text_without_rewriting_versions(mapping_data):
    mapping_data.update(
        os_name=" Example OS ",
        os_version=" v01.02 ",
        release_name=" Release-01 ",
    )

    mapping = OsReleaseMapping(**mapping_data)

    assert mapping.os_name == "Example OS"
    assert mapping.os_version == "v01.02"
    assert mapping.release_name == "Release-01"


@pytest.mark.parametrize(
    "field",
    ["os_name", "os_version", "release_name"],
)
@pytest.mark.parametrize("value", ["Unknown", "N/A", "unspecified"])
def test_rejects_unknown_identity(mapping_data, field, value):
    mapping_data[field] = value

    with pytest.raises(ValidationError, match="known identifiers"):
        OsReleaseMapping(**mapping_data)


@pytest.mark.parametrize(
    "field",
    ["os_name", "os_version", "release_name", "mapping_basis"],
)
@pytest.mark.parametrize("value", ["", "   "])
def test_rejects_blank_required_text(mapping_data, field, value):
    mapping_data[field] = value

    with pytest.raises(ValidationError):
        OsReleaseMapping(**mapping_data)


@pytest.mark.parametrize(
    "product",
    ["", "Example-OS", "../example-os", "example/os", "example?x=1"],
)
def test_rejects_invalid_product_slug(mapping_data, product):
    mapping_data["product"] = product

    with pytest.raises(ValidationError):
        OsReleaseMapping(**mapping_data)


@pytest.mark.parametrize(
    "field",
    ["os_name", "os_version", "product", "release_name", "mapping_basis"],
)
def test_requires_all_fields(mapping_data, field):
    del mapping_data[field]

    with pytest.raises(ValidationError):
        OsReleaseMapping(**mapping_data)


def test_rejects_unexpected_fields(mapping_data):
    mapping_data["unexpected"] = "value"

    with pytest.raises(ValidationError):
        OsReleaseMapping(**mapping_data)


def test_json_round_trip(mapping_data):
    mapping = OsReleaseMapping(**mapping_data)

    assert OsReleaseMapping.model_validate_json(
        mapping.model_dump_json()
    ) == mapping


def test_mapping_is_frozen(mapping_data):
    mapping = OsReleaseMapping(**mapping_data)

    with pytest.raises(ValidationError):
        mapping.release_name = "2"