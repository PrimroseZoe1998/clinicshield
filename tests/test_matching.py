import pytest

from clinicshield.matching import MatchStatus, match_exact_versions
from clinicshield.normalization import normalize_software


@pytest.mark.parametrize(
    "version,affected,expected",
    [
        ("1.2.3", ("1.2.3",), MatchStatus.MATCH),
        ("1.2.3", ("1.2.2", "1.2.3"), MatchStatus.MATCH),
        ("1.2.4", ("1.2.3",), MatchStatus.NO_MATCH),
        ("Unknown", ("1.2.3",), MatchStatus.NEEDS_REVIEW),
        ("1.2.3", (), MatchStatus.NEEDS_REVIEW),
        ("1.2.3", ("Unknown",), MatchStatus.NEEDS_REVIEW),
        ("1.2.3", ("1.2.2", "Unknown"), MatchStatus.NEEDS_REVIEW),
        ("1.2.3", ("1.2.3", "Unknown"), MatchStatus.MATCH),
        ("v1.2.3", ("1.2.3",), MatchStatus.NO_MATCH),
        ("01.02", ("1.2",), MatchStatus.NO_MATCH),
        ("1.0-beta", ("1.0",), MatchStatus.NO_MATCH),
        ("1.2+build.7", ("1.2",), MatchStatus.NO_MATCH),
        ("1.2.3", (" 1.2.3 ",), MatchStatus.MATCH),
    ],
)
def test_exact_version_matching(version, affected, expected):
    software = normalize_software("Example Vendor", "Product-X", version)

    result = match_exact_versions(
        software,
        vendor="Example Vendor",
        product="Product-X",
        affected_versions=affected,
    )

    assert result is expected


def test_normalizes_feed_vendor_and_product():
    software = normalize_software("Example Vendor", "Product-X", "1.2.3")

    assert match_exact_versions(
        software,
        vendor="  EXAMPLE   VENDOR ",
        product=" PRODUCT-X ",
        affected_versions=("1.2.3",),
    ) is MatchStatus.MATCH


@pytest.mark.parametrize(
    "vendor,product",
    [
        ("Other Vendor", "Product-X"),
        ("Example Vendor", "Other Product"),
        ("Example Vendor", "Product X"),
        ("Example Vendor", "Product.X"),
    ],
)
@pytest.mark.parametrize("version", ["1.2.3", "Unknown"])
def test_different_identity_does_not_match(vendor, product, version):
    software = normalize_software("Example Vendor", "Product-X", version)

    assert match_exact_versions(
        software,
        vendor=vendor,
        product=product,
        affected_versions=("1.2.3",),
    ) is MatchStatus.NO_MATCH