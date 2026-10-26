from datetime import datetime, timezone

import pytest

from clinicshield import eol_cache_io
from clinicshield.eol_cache import EolSnapshot
from clinicshield.eol_download import EOL_BASE_URL


@pytest.fixture
def snapshot():
    return EolSnapshot(
        source_url=f"{EOL_BASE_URL}python/",
        retrieved_at=datetime(2026, 10, 26, 14, tzinfo=timezone.utc),
        product="python",
        response={
            "schema_version": "1.2.1",
            "generated_at": "2026-10-26T00:00:00Z",
            "last_modified": "2026-10-25T12:00:00Z",
            "result": {
                "name": "python",
                "label": "Python",
                "releases": [
                    {
                        "name": "3.10",
                        "isEol": True,
                        "eolFrom": "2026-10-01",
                        "isMaintained": False,
                    }
                ],
            },
        },
    )


def test_missing_cache_returns_none(tmp_path):
    assert eol_cache_io.read_eol_cache(
        tmp_path / "missing.json"
    ) is None


def test_write_and_read_cache(tmp_path, snapshot):
    path = tmp_path / "cache" / "python.json"

    eol_cache_io.write_eol_cache(path, snapshot)

    assert eol_cache_io.read_eol_cache(path) == snapshot
    assert list(path.parent.iterdir()) == [path]


def test_replaces_existing_cache(tmp_path, snapshot):
    path = tmp_path / "python.json"
    path.write_bytes(b"old cache")

    eol_cache_io.write_eol_cache(path, snapshot)

    assert eol_cache_io.read_eol_cache(path) == snapshot


@pytest.mark.parametrize("payload", [b"{", b"{}", b"\xff"])
def test_rejects_invalid_cache(tmp_path, payload):
    path = tmp_path / "python.json"
    path.write_bytes(payload)

    with pytest.raises(ValueError):
        eol_cache_io.read_eol_cache(path)


def test_rejects_oversized_read(tmp_path, monkeypatch):
    monkeypatch.setattr(eol_cache_io, "MAX_CACHE_BYTES", 10)
    path = tmp_path / "python.json"
    path.write_bytes(b"x" * 11)

    with pytest.raises(ValueError, match="size limit"):
        eol_cache_io.read_eol_cache(path)


def test_accepts_exact_size_limit(tmp_path, snapshot, monkeypatch):
    payload = snapshot.model_dump_json().encode("utf-8")
    monkeypatch.setattr(
        eol_cache_io, "MAX_CACHE_BYTES", len(payload)
    )
    path = tmp_path / "python.json"

    eol_cache_io.write_eol_cache(path, snapshot)

    assert eol_cache_io.read_eol_cache(path) == snapshot


def test_oversized_write_preserves_cache(
    tmp_path, snapshot, monkeypatch
):
    path = tmp_path / "python.json"
    original = b"existing cache"
    path.write_bytes(original)
    monkeypatch.setattr(eol_cache_io, "MAX_CACHE_BYTES", 1)

    with pytest.raises(ValueError, match="size limit"):
        eol_cache_io.write_eol_cache(path, snapshot)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("operation", ["replace", "fsync"])
def test_write_failure_preserves_cache(
    tmp_path, snapshot, monkeypatch, operation
):
    path = tmp_path / "python.json"
    original = b"existing cache"
    path.write_bytes(original)

    def fail(*args, **kwargs):
        raise OSError("simulated storage failure")

    monkeypatch.setattr(eol_cache_io.os, operation, fail)

    with pytest.raises(OSError, match="storage failure"):
        eol_cache_io.write_eol_cache(path, snapshot)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_directory_read_raises_error(tmp_path):
    with pytest.raises(OSError):
        eol_cache_io.read_eol_cache(tmp_path)