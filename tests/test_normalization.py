import pytest

from clinicshield.input_limits import InputError
from clinicshield.normalization import (
    normalize_name,
    normalize_software,
    normalize_version,
)


def test_normalizes_name_case_and_whitespace():
    assert normalize_name("  Example   VENDOR\tLtd  ") == "example vendor ltd"


@pytest.mark.parametrize(
    "name",
    ["Product-X", "Product X", "Product.X", "Product_X"],
)
def test_preserves_name_punctuation(name):
    assert normalize_name(name) == name.casefold()


@pytest.mark.parametrize(
    "version",
    ["1.2.3", "v1.2.3", "01.02", "1.0-beta", "2026.10", "1.2+build.7"],
)
def test_preserves_version_details(version):
    assert normalize_version(f"  {version}  ") == version


@pytest.mark.parametrize(
    "version",
    ["", " ", "Unknown", "UNKNOWN", "N/A", "NA", "not known", "unspecified"],
)
def test_unknown_versions_remain_unknown(version):
    assert normalize_version(version) is None


def test_normalizes_complete_software_identity():
    result = normalize_software(
        " Example Vendor ", " Example  Product ", " 1.2.3 "
    )
    assert result.vendor == "example vendor"
    assert result.product == "example product"
    assert result.version == "1.2.3"


@pytest.mark.parametrize(
    "vendor,product",
    [
        ("", "Product"),
        ("Unknown", "Product"),
        ("Vendor", ""),
        ("Vendor", "N/A"),
    ],
)
def test_rejects_missing_vendor_or_product(vendor, product):
    with pytest.raises(InputError, match="known vendor and product"):
        normalize_software(vendor, product, "1.0")


@pytest.mark.parametrize("value", [None, 123, [], {}])
def test_rejects_nontext_names(value):
    with pytest.raises(InputError, match="must be text"):
        normalize_name(value)


@pytest.mark.parametrize("value", [None, 123, [], {}])
def test_rejects_nontext_versions(value):
    with pytest.raises(InputError, match="must be text"):
        normalize_version(value)