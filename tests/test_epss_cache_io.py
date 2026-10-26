from datetime import datetime, timezone

import pytest

from clinicshield import epss_cache_io
from clinicshield.epss_cache import EpssSnapshot


@pytest.fixture
def snapshot():
    return EpssSnapshot(
        retrieved_at=datetime(2026, 10, 26, 14, tzinfo=timezone.utc),
        model_version="v2026.06.15",
        score_date="2026-10-26",
        records=(
            {
                "cve": "CVE-2026-12345",
                "epss": "0.123456789",
                "percentile": "0.987654321",
                "score_date": "2026-10-26",
            },
        ),
    )


def test_missing_cache_returns_none(tmp_path):
    assert epss_cache_io.read_epss_cache(
        tmp_path / "missing.json"
    ) is None


def test_write_and_read_cache(tmp_path, snapshot):
    path = tmp_path / "cache" / "epss.json"

    epss_cache_io.write_epss_cache(path, snapshot)

    assert epss_cache_io.read_epss_cache(path) == snapshot
    assert list(path.parent.iterdir()) == [path]


def test_replaces_existing_cache(tmp_path, snapshot):
    path = tmp_path / "epss.json"
    path.write_bytes(b"old cache")

    epss_cache_io.write_epss_cache(path, snapshot)

    assert epss_cache_io.read_epss_cache(path) == snapshot


@pytest.mark.parametrize("payload", [b"{", b"{}", b"\xff"])
def test_rejects_invalid_cache(tmp_path, payload):
    path = tmp_path / "epss.json"
    path.write_bytes(payload)

    with pytest.raises(ValueError):
        epss_cache_io.read_epss_cache(path)


def test_rejects_oversized_read(tmp_path, monkeypatch):
    monkeypatch.setattr(epss_cache_io, "MAX_CACHE_BYTES", 10)
    path = tmp_path / "epss.json"
    path.write_bytes(b"x" * 11)

    with pytest.raises(ValueError, match="size limit"):
        epss_cache_io.read_epss_cache(path)


def test_accepts_exact_size_limit(tmp_path, snapshot, monkeypatch):
    payload = snapshot.model_dump_json().encode("utf-8")
    monkeypatch.setattr(
        epss_cache_io, "MAX_CACHE_BYTES", len(payload)
    )
    path = tmp_path / "epss.json"

    epss_cache_io.write_epss_cache(path, snapshot)

    assert epss_cache_io.read_epss_cache(path) == snapshot


def test_oversized_write_preserves_cache(
    tmp_path, snapshot, monkeypatch
):
    path = tmp_path / "epss.json"
    original = b"existing cache"
    path.write_bytes(original)
    monkeypatch.setattr(epss_cache_io, "MAX_CACHE_BYTES", 1)

    with pytest.raises(ValueError, match="size limit"):
        epss_cache_io.write_epss_cache(path, snapshot)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("operation", ["replace", "fsync"])
def test_write_failure_preserves_cache(
    tmp_path, snapshot, monkeypatch, operation
):
    path = tmp_path / "epss.json"
    original = b"existing cache"
    path.write_bytes(original)

    def fail(*args, **kwargs):
        raise OSError("simulated storage failure")

    monkeypatch.setattr(epss_cache_io.os, operation, fail)

    with pytest.raises(OSError, match="storage failure"):
        epss_cache_io.write_epss_cache(path, snapshot)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_directory_read_raises_error(tmp_path):
    with pytest.raises(OSError):
        epss_cache_io.read_epss_cache(tmp_path)