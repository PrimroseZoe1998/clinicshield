from datetime import datetime, timedelta, timezone

import pytest
import requests
from pydantic import ValidationError

from clinicshield import kev_cache, kev_refresh
from clinicshield.kev_cache import (
    KevSnapshot,
    read_kev_cache,
    write_kev_cache,
)
from clinicshield.kev_models import KevCatalog


@pytest.fixture
def catalog():
    return KevCatalog(
        catalogVersion="2026.10.26",
        dateReleased="2026-10-26T12:00:00Z",
        count=0,
        vulnerabilities=(),
    )


def seed_cache(path, catalog):
    snapshot = KevSnapshot(
        retrieved_at=datetime(2026, 10, 25, tzinfo=timezone.utc),
        catalog=catalog,
    )
    write_kev_cache(path, snapshot)
    return path.read_bytes()


def test_successful_refresh_creates_cache(tmp_path, monkeypatch, catalog):
    path = tmp_path / "cache" / "kev.json"
    monkeypatch.setattr(kev_refresh, "download_kev", lambda: catalog)
    before = datetime.now(timezone.utc)

    result = kev_refresh.refresh_kev_cache(path)

    after = datetime.now(timezone.utc)
    assert result.catalog == catalog
    assert before <= result.retrieved_at <= after
    assert result.retrieved_at.utcoffset() == timedelta(0)
    assert read_kev_cache(path) == result
    assert list(path.parent.iterdir()) == [path]


def test_successful_refresh_replaces_cache(tmp_path, monkeypatch, catalog):
    path = tmp_path / "kev.json"
    original = seed_cache(path, catalog)
    monkeypatch.setattr(kev_refresh, "download_kev", lambda: catalog)

    result = kev_refresh.refresh_kev_cache(path)

    assert path.read_bytes() != original
    assert read_kev_cache(path) == result


@pytest.mark.parametrize(
    "error_type",
    [requests.ConnectionError, requests.Timeout, requests.HTTPError],
)
def test_download_failure_preserves_cache(
    tmp_path, monkeypatch, catalog, error_type
):
    path = tmp_path / "kev.json"
    original = seed_cache(path, catalog)

    def fail_download():
        raise error_type("simulated download failure")

    monkeypatch.setattr(kev_refresh, "download_kev", fail_download)

    with pytest.raises(error_type):
        kev_refresh.refresh_kev_cache(path)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_validation_failure_preserves_cache(
    tmp_path, monkeypatch, catalog
):
    path = tmp_path / "kev.json"
    original = seed_cache(path, catalog)

    def invalid_download():
        return KevCatalog.model_validate_json("{}")

    monkeypatch.setattr(kev_refresh, "download_kev", invalid_download)

    with pytest.raises(ValidationError):
        kev_refresh.refresh_kev_cache(path)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_size_failure_preserves_cache(tmp_path, monkeypatch, catalog):
    path = tmp_path / "kev.json"
    original = seed_cache(path, catalog)

    def oversized_download():
        raise ValueError("KEV download exceeds the size limit.")

    monkeypatch.setattr(kev_refresh, "download_kev", oversized_download)

    with pytest.raises(ValueError, match="size limit"):
        kev_refresh.refresh_kev_cache(path)

    assert path.read_bytes() == original


@pytest.mark.parametrize("operation", ["replace", "fsync"])
def test_storage_failure_preserves_cache(
    tmp_path, monkeypatch, catalog, operation
):
    path = tmp_path / "kev.json"
    original = seed_cache(path, catalog)
    monkeypatch.setattr(kev_refresh, "download_kev", lambda: catalog)

    def fail(*args, **kwargs):
        raise OSError("simulated storage failure")

    monkeypatch.setattr(kev_cache.os, operation, fail)

    with pytest.raises(OSError, match="storage failure"):
        kev_refresh.refresh_kev_cache(path)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_failed_first_download_creates_no_cache(tmp_path, monkeypatch):
    path = tmp_path / "cache" / "kev.json"

    def fail_download():
        raise requests.ConnectionError("simulated download failure")

    monkeypatch.setattr(kev_refresh, "download_kev", fail_download)

    with pytest.raises(requests.ConnectionError):
        kev_refresh.refresh_kev_cache(path)

    assert not path.parent.exists()