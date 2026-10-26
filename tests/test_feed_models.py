from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from clinicshield.feed_models import VulnerabilityRecord


@pytest.fixture
def record_data():
    return {
        "vulnerability_id": "TEST-2026-001",
        "source": "Example feed",
        "source_url": "https://example.org/advisories/001",
        "retrieved_at": datetime(2026, 10, 26, tzinfo=timezone.utc),
        "vendor": " Example   Vendor ",
        "product": " Product-X ",
        "version_rule": "exact",
        "affected_versions": (" 1.2.3 ", "v2.0"),
    }


def test_normalizes_identity_and_preserves_versions(record_data):
    record = VulnerabilityRecord(**record_data)

    assert record.vendor == "example vendor"
    assert record.product == "product-x"
    assert record.affected_versions == ("1.2.3", "v2.0")


def test_preserves_source_information(record_data):
    record = VulnerabilityRecord(**record_data)

    assert record.vulnerability_id == "TEST-2026-001"
    assert record.source == "Example feed"
    assert str(record.source_url) == "https://example.org/advisories/001"
    assert record.retrieved_at == record_data["retrieved_at"]


def test_preserves_unsupported_version_evidence(record_data):
    record_data.update(
        version_rule="unsupported",
        affected_versions=(),
        version_evidence=">=1.0, <2.0",
    )

    record = VulnerabilityRecord(**record_data)

    assert record.version_rule == "unsupported"
    assert record.version_evidence == ">=1.0, <2.0"


def test_allows_missing_exact_versions_for_later_review(record_data):
    record_data["affected_versions"] = ()

    assert VulnerabilityRecord(**record_data).affected_versions == ()


@pytest.mark.parametrize("field", ["vendor", "product"])
@pytest.mark.parametrize("value", ["", "  ", "Unknown", "N/A"])
def test_rejects_unknown_identity(record_data, field, value):
    record_data[field] = value

    with pytest.raises(ValidationError):
        VulnerabilityRecord(**record_data)


@pytest.mark.parametrize("value", ["", "Unknown", "N/A"])
def test_rejects_unknown_affected_versions(record_data, value):
    record_data["affected_versions"] = (value,)

    with pytest.raises(ValidationError):
        VulnerabilityRecord(**record_data)


def test_rejects_timestamp_without_timezone(record_data):
    record_data["retrieved_at"] = datetime(2026, 10, 26)

    with pytest.raises(ValidationError):
        VulnerabilityRecord(**record_data)


@pytest.mark.parametrize("field", ["vulnerability_id", "source"])
def test_rejects_blank_source_fields(record_data, field):
    record_data[field] = "   "

    with pytest.raises(ValidationError):
        VulnerabilityRecord(**record_data)


def test_rejects_invalid_source_url(record_data):
    record_data["source_url"] = "not a URL"

    with pytest.raises(ValidationError):
        VulnerabilityRecord(**record_data)


def test_rejects_unknown_version_rule(record_data):
    record_data["version_rule"] = "guess"

    with pytest.raises(ValidationError):
        VulnerabilityRecord(**record_data)


def test_rejects_unexpected_fields(record_data):
    record_data["unexpected"] = "value"

    with pytest.raises(ValidationError):
        VulnerabilityRecord(**record_data)


def test_record_is_frozen(record_data):
    record = VulnerabilityRecord(**record_data)

    with pytest.raises(ValidationError):
        record.source = "Changed source"