from datetime import datetime, timezone

import pytest

from clinicshield.feed_models import VulnerabilityRecord
from clinicshield.matching import MatchStatus, match_feed_record
from clinicshield.normalization import normalize_software


def make_record(**changes):
    data = {
        "vulnerability_id": "TEST-2026-001",
        "source": "Example feed",
        "source_url": "https://example.org/advisories/001",
        "retrieved_at": datetime(2026, 10, 26, tzinfo=timezone.utc),
        "vendor": "Example Vendor",
        "product": "Product-X",
        "version_rule": "exact",
        "affected_versions": ("1.2.3",),
    }
    data.update(changes)
    return VulnerabilityRecord(**data)


@pytest.mark.parametrize(
    "version,expected",
    [
        ("1.2.3", MatchStatus.MATCH),
        ("1.2.4", MatchStatus.NO_MATCH),
        ("Unknown", MatchStatus.NEEDS_REVIEW),
    ],
)
def test_matches_exact_feed_record(version, expected):
    software = normalize_software("Example Vendor", "Product-X", version)

    assert match_feed_record(software, make_record()) is expected


@pytest.mark.parametrize("version", ["1.2.3", "1.2.4", "Unknown"])
@pytest.mark.parametrize("affected", [(), ("1.2.3",)])
def test_unsupported_rule_always_requires_review(version, affected):
    software = normalize_software("Example Vendor", "Product-X", version)
    record = make_record(
        version_rule="unsupported",
        affected_versions=affected,
        version_evidence=">=1.0, <2.0",
    )

    assert match_feed_record(
        software, record
    ) is MatchStatus.NEEDS_REVIEW


def test_empty_exact_version_list_requires_review():
    software = normalize_software("Example Vendor", "Product-X", "1.2.3")

    assert match_feed_record(
        software, make_record(affected_versions=())
    ) is MatchStatus.NEEDS_REVIEW


@pytest.mark.parametrize("rule", ["exact", "unsupported"])
@pytest.mark.parametrize(
    "identity",
    [
        {"vendor": "Other Vendor"},
        {"product": "Other Product"},
        {"product": "Product X"},
    ],
)
def test_different_identity_does_not_match(rule, identity):
    software = normalize_software("Example Vendor", "Product-X", "1.2.3")
    record = make_record(version_rule=rule, **identity)

    assert match_feed_record(software, record) is MatchStatus.NO_MATCH


def test_normalized_feed_identity_matches():
    software = normalize_software("Example Vendor", "Product-X", "1.2.3")
    record = make_record(
        vendor=" EXAMPLE   VENDOR ",
        product=" PRODUCT-X ",
    )

    assert match_feed_record(software, record) is MatchStatus.MATCH