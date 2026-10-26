from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from clinicshield import kev_cache
from clinicshield.kev_cache import (
    KevSnapshot,
    read_kev_cache,
    write_kev_cache,
)
from clinicshield.kev_download import KEV_URL


@pytest.fixture
def snapshot_data():
    return {
        "retrieved_at": datetime(2026, 10, 26, 12, tzinfo=timezone.utc),
        "catalog": {
            "catalogVersion": "2026.10.25",
            "dateReleased": "2026-10-25T10:00:00Z",
            "count": 0,
            "vulnerabilities": [],
        },
    }


@pytest.fixture
def snapshot(snapshot_data):
    return KevSnapshot(**snapshot_data)


def test_round_trip_preserves_metadata(tmp_path, snapshot):
    path = tmp_path / "cache" / "kev.json"

    write_kev_cache(path, snapshot)
    restored = read_kev_cache(path)

    assert restored == snapshot
    assert restored.source == "CISA KEV"
    assert restored.source_url == KEV_URL
    assert restored.retrieved_at != restored.catalog.dateReleased
    assert list(path.parent.iterdir()) == [path]


def test_missing_cache_returns_none(tmp_path):
    assert read_kev_cache(tmp_path / "missing.json") is None


@pytest.mark.parametrize("payload", [b"{", b"{}", b"\xff"])
def test_rejects_invalid_cache(tmp_path, payload):
    path = tmp_path / "kev.json"
    path.write_bytes(payload)

    with pytest.raises(ValidationError):
        read_kev_cache(path)


@pytest.mark.parametrize(
    "changes",
    [
        {"source": "Other source"},
        {"source_url": "https://example.org/feed.json"},
        {"schema_version": 2},
        {"unexpected": "value"},
    ],
)
def test_rejects_invalid_metadata(snapshot_data, changes):
    snapshot_data.update(changes)

    with pytest.raises(ValidationError):
        KevSnapshot(**snapshot_data)


def test_requires_retrieval_timezone(snapshot_data):
    snapshot_data["retrieved_at"] = datetime(2026, 10, 26)

    with pytest.raises(ValidationError, match="timezone"):
        KevSnapshot(**snapshot_data)


def test_validates_nested_catalog(snapshot_data):
    snapshot_data["catalog"]["count"] = 1

    with pytest.raises(ValidationError, match="count"):
        KevSnapshot(**snapshot_data)


def test_snapshot_is_frozen(snapshot):
    with pytest.raises(ValidationError):
        snapshot.source = "Other source"


def test_replaces_existing_cache(tmp_path, snapshot):
    path = tmp_path / "kev.json"
    path.write_bytes(b"old cache")

    write_kev_cache(path, snapshot)

    assert read_kev_cache(path) == snapshot


def test_rejects_oversized_read(tmp_path, monkeypatch):
    monkeypatch.setattr(kev_cache, "MAX_CACHE_BYTES", 10)
    path = tmp_path / "kev.json"
    path.write_bytes(b"x" * 11)

    with pytest.raises(ValueError, match="size limit"):
        read_kev_cache(path)


def test_accepts_exact_size_limit(tmp_path, snapshot, monkeypatch):
    payload = snapshot.model_dump_json().encode("utf-8")
    monkeypatch.setattr(kev_cache, "MAX_CACHE_BYTES", len(payload))
    path = tmp_path / "kev.json"

    write_kev_cache(path, snapshot)

    assert read_kev_cache(path) == snapshot


def test_oversized_write_preserves_cache(
    tmp_path, snapshot, monkeypatch
):
    path = tmp_path / "kev.json"
    original = b"existing cache"
    path.write_bytes(original)
    monkeypatch.setattr(kev_cache, "MAX_CACHE_BYTES", 1)

    with pytest.raises(ValueError, match="size limit"):
        write_kev_cache(path, snapshot)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("operation", ["replace", "fsync"])
def test_write_failure_preserves_cache(
    tmp_path, snapshot, monkeypatch, operation
):
    path = tmp_path / "kev.json"
    original = b"existing cache"
    path.write_bytes(original)

    def fail(*args, **kwargs):
        raise OSError("simulated write failure")

    monkeypatch.setattr(kev_cache.os, operation, fail)

    with pytest.raises(OSError, match="write failure"):
        write_kev_cache(path, snapshot)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_directory_read_raises_error(tmp_path):
    with pytest.raises(OSError):
        read_kev_cache(tmp_path)