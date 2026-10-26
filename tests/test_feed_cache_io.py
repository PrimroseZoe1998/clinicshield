from datetime import datetime, timezone

import pytest

from clinicshield import feed_cache_io
from clinicshield.feed_cache import FeedSnapshot


@pytest.fixture
def snapshot():
    return FeedSnapshot(
        source="Example feed",
        source_url="https://example.org/feed.json",
        retrieved_at=datetime(2026, 10, 26, tzinfo=timezone.utc),
        records=(),
    )


def test_missing_cache_returns_none(tmp_path):
    assert feed_cache_io.read_feed_cache(
        tmp_path / "missing.json"
    ) is None


def test_write_and_read_cache(tmp_path, snapshot):
    path = tmp_path / "cache" / "feed.json"

    feed_cache_io.write_feed_cache(path, snapshot)

    assert feed_cache_io.read_feed_cache(path) == snapshot
    assert list(path.parent.iterdir()) == [path]


def test_replaces_existing_cache(tmp_path, snapshot):
    path = tmp_path / "feed.json"
    path.write_text("old cache", encoding="utf-8")

    feed_cache_io.write_feed_cache(path, snapshot)

    assert feed_cache_io.read_feed_cache(path) == snapshot


@pytest.mark.parametrize("payload", [b"{", b"{}", b"\xff"])
def test_rejects_invalid_cache(tmp_path, payload):
    path = tmp_path / "feed.json"
    path.write_bytes(payload)

    with pytest.raises(ValueError):
        feed_cache_io.read_feed_cache(path)


def test_rejects_oversized_read(tmp_path, monkeypatch):
    monkeypatch.setattr(feed_cache_io, "MAX_CACHE_BYTES", 10)
    path = tmp_path / "feed.json"
    path.write_bytes(b"x" * 11)

    with pytest.raises(ValueError, match="size limit"):
        feed_cache_io.read_feed_cache(path)


def test_accepts_cache_at_exact_size_limit(
    tmp_path, snapshot, monkeypatch
):
    path = tmp_path / "feed.json"
    payload = feed_cache_io.serialize_snapshot(snapshot).encode("utf-8")
    monkeypatch.setattr(
        feed_cache_io, "MAX_CACHE_BYTES", len(payload)
    )

    feed_cache_io.write_feed_cache(path, snapshot)

    assert feed_cache_io.read_feed_cache(path) == snapshot


def test_oversized_write_preserves_existing_cache(
    tmp_path, snapshot, monkeypatch
):
    path = tmp_path / "feed.json"
    original = b"existing cache"
    path.write_bytes(original)
    monkeypatch.setattr(feed_cache_io, "MAX_CACHE_BYTES", 1)

    with pytest.raises(ValueError, match="size limit"):
        feed_cache_io.write_feed_cache(path, snapshot)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_failed_replace_preserves_existing_cache(
    tmp_path, snapshot, monkeypatch
):
    path = tmp_path / "feed.json"
    original = b"existing cache"
    path.write_bytes(original)

    def fail_replace(*args, **kwargs):
        raise OSError("simulated replacement failure")

    monkeypatch.setattr(feed_cache_io.os, "replace", fail_replace)

    with pytest.raises(OSError, match="replacement failure"):
        feed_cache_io.write_feed_cache(path, snapshot)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_failed_sync_preserves_existing_cache(
    tmp_path, snapshot, monkeypatch
):
    path = tmp_path / "feed.json"
    original = b"existing cache"
    path.write_bytes(original)

    def fail_sync(*args, **kwargs):
        raise OSError("simulated sync failure")

    monkeypatch.setattr(feed_cache_io.os, "fsync", fail_sync)

    with pytest.raises(OSError, match="sync failure"):
        feed_cache_io.write_feed_cache(path, snapshot)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_directory_read_raises_error(tmp_path):
    with pytest.raises(OSError):
        feed_cache_io.read_feed_cache(tmp_path)