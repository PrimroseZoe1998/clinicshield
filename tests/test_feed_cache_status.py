from datetime import datetime, timedelta, timezone

import pytest

from clinicshield import feed_cache_status
from clinicshield.feed_cache import FeedSnapshot
from clinicshield.feed_cache_io import write_feed_cache
from clinicshield.feed_cache_status import load_cached_feed
from clinicshield.feed_freshness import FeedFreshness


NOW = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)
MAX_AGE = timedelta(hours=24)


@pytest.mark.parametrize(
    "age,expected",
    [
        (timedelta(0), FeedFreshness.FRESH),
        (MAX_AGE, FeedFreshness.FRESH),
        (
            MAX_AGE + timedelta(microseconds=1),
            FeedFreshness.STALE,
        ),
        (timedelta(seconds=-1), FeedFreshness.NEEDS_REVIEW),
    ],
)
def test_reports_freshness_and_preserves_snapshot(
    tmp_path, age, expected
):
    snapshot = FeedSnapshot(
        source="Example feed",
        source_url="https://example.org/feed.json",
        retrieved_at=NOW - age,
        records=(),
    )
    path = tmp_path / "feed.json"
    write_feed_cache(path, snapshot)

    result = load_cached_feed(path, now=NOW, max_age=MAX_AGE)

    assert result.snapshot == snapshot
    assert result.freshness is expected
    assert result.problem is None


def test_reports_missing_cache(tmp_path):
    result = load_cached_feed(
        tmp_path / "missing.json",
        now=NOW,
        max_age=MAX_AGE,
    )

    assert result.snapshot is None
    assert result.freshness is FeedFreshness.UNAVAILABLE
    assert result.problem == "missing"


@pytest.mark.parametrize("payload", [b"{", b"{}", b"\xff"])
def test_reports_invalid_cache(tmp_path, payload):
    path = tmp_path / "feed.json"
    path.write_bytes(payload)

    result = load_cached_feed(path, now=NOW, max_age=MAX_AGE)

    assert result.snapshot is None
    assert result.freshness is FeedFreshness.UNAVAILABLE
    assert result.problem == "invalid"


def test_reports_unreadable_cache(tmp_path, monkeypatch):
    def fail_read(path):
        raise PermissionError("simulated access failure")

    monkeypatch.setattr(feed_cache_status, "read_feed_cache", fail_read)

    result = load_cached_feed(
        tmp_path / "feed.json",
        now=NOW,
        max_age=MAX_AGE,
    )

    assert result.snapshot is None
    assert result.freshness is FeedFreshness.UNAVAILABLE
    assert result.problem == "unreadable"


@pytest.mark.parametrize(
    "now,max_age",
    [
        (NOW.replace(tzinfo=None), MAX_AGE),
        (NOW, timedelta(0)),
        (NOW, timedelta(seconds=-1)),
    ],
)
def test_rejects_invalid_configuration_before_reading(
    tmp_path, monkeypatch, now, max_age
):
    def unexpected_read(path):
        pytest.fail("Cache should not be read with invalid configuration.")

    monkeypatch.setattr(
        feed_cache_status, "read_feed_cache", unexpected_read
    )

    with pytest.raises(ValueError):
        load_cached_feed(
            tmp_path / "feed.json",
            now=now,
            max_age=max_age,
        )