from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from clinicshield.feed_cache import (
    FeedSnapshot,
    deserialize_snapshot,
    serialize_snapshot,
)
from clinicshield.feed_models import VulnerabilityRecord


NOW = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)
SOURCE = "Example feed"
SOURCE_URL = "https://example.org/feed.json"


def make_record(**changes):
    data = {
        "vulnerability_id": "TEST-2026-001",
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "retrieved_at": NOW,
        "vendor": "Example Vendor",
        "product": "Product-X",
        "version_rule": "exact",
        "affected_versions": ("1.2.3",),
    }
    data.update(changes)
    return VulnerabilityRecord(**data)


def make_snapshot(**changes):
    data = {
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "retrieved_at": NOW,
        "records": (make_record(),),
    }
    data.update(changes)
    return FeedSnapshot(**data)


def test_round_trip_preserves_snapshot():
    snapshot = make_snapshot()

    restored = deserialize_snapshot(serialize_snapshot(snapshot))

    assert restored == snapshot
    assert restored.records[0].affected_versions == ("1.2.3",)


def test_empty_feed_preserves_metadata():
    snapshot = make_snapshot(records=())

    restored = deserialize_snapshot(serialize_snapshot(snapshot))

    assert restored.records == ()
    assert restored.source == SOURCE
    assert str(restored.source_url) == SOURCE_URL
    assert restored.retrieved_at == NOW


def test_round_trip_preserves_unsupported_rule():
    record = make_record(
        version_rule="unsupported",
        affected_versions=(),
        version_evidence=">=1.0, <2.0",
    )
    snapshot = make_snapshot(records=(record,))

    restored = deserialize_snapshot(serialize_snapshot(snapshot))

    assert restored == snapshot
    assert restored.records[0].version_evidence == ">=1.0, <2.0"


@pytest.mark.parametrize(
    "changes",
    [
        {"source": "Other feed"},
        {"source_url": "https://example.org/other.json"},
        {"retrieved_at": NOW - timedelta(seconds=1)},
    ],
)
def test_rejects_mismatched_record_provenance(changes):
    record = make_record(**changes)

    with pytest.raises(ValidationError, match="provenance"):
        make_snapshot(records=(record,))


def test_accepts_equivalent_retrieval_timezones():
    offset = timezone(timedelta(hours=-4))
    record = make_record(retrieved_at=NOW.astimezone(offset))

    assert make_snapshot(records=(record,)).records == (record,)


def test_rejects_snapshot_time_without_timezone():
    with pytest.raises(ValidationError, match="timezone"):
        make_snapshot(
            retrieved_at=NOW.replace(tzinfo=None),
            records=(),
        )


def test_rejects_unsupported_schema_version():
    with pytest.raises(ValidationError):
        make_snapshot(schema_version=2)


def test_rejects_unexpected_fields():
    with pytest.raises(ValidationError):
        make_snapshot(unexpected="value")


def test_requires_records_field():
    with pytest.raises(ValidationError):
        FeedSnapshot(
            source=SOURCE,
            source_url=SOURCE_URL,
            retrieved_at=NOW,
        )


@pytest.mark.parametrize("source", ["", "   "])
def test_rejects_blank_source(source):
    with pytest.raises(ValidationError):
        make_snapshot(source=source, records=())


def test_rejects_invalid_source_url():
    with pytest.raises(ValidationError):
        make_snapshot(source_url="not a URL", records=())


@pytest.mark.parametrize("payload", ["{", "null", "[]", "{}"])
def test_rejects_invalid_cache_payload(payload):
    with pytest.raises(ValidationError):
        deserialize_snapshot(payload)


def test_deserialization_rejects_mismatched_provenance():
    data = make_snapshot().model_dump(mode="json")
    data["records"][0]["source"] = "Other feed"

    import json

    with pytest.raises(ValidationError, match="provenance"):
        deserialize_snapshot(json.dumps(data))


def test_snapshot_is_frozen():
    snapshot = make_snapshot()

    with pytest.raises(ValidationError):
        snapshot.source = "Changed feed"