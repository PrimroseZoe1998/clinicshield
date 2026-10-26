from datetime import date, datetime, timedelta, timezone

import pytest
import requests
from pydantic import ValidationError

from clinicshield import epss_cache_io, epss_refresh
from clinicshield.epss_cache import EpssSnapshot
from clinicshield.epss_cache_io import read_epss_cache, write_epss_cache
from clinicshield.epss_models import EpssRecord
from clinicshield.epss_parse import EpssDataset


@pytest.fixture
def dataset():
    return EpssDataset(
        model_version="v2026.06.15",
        score_date=date(2026, 10, 26),
        records=(
            EpssRecord(
                cve="CVE-2026-12345",
                epss="0.123456789",
                percentile="0.987654321",
                score_date="2026-10-26",
            ),
        ),
    )


def seed_cache(path, dataset):
    snapshot = EpssSnapshot(
        retrieved_at=datetime(2026, 10, 25, tzinfo=timezone.utc),
        model_version=dataset.model_version,
        score_date=dataset.score_date,
        records=dataset.records,
    )
    write_epss_cache(path, snapshot)
    return path.read_bytes()


def test_successful_refresh_creates_cache(
    tmp_path, monkeypatch, dataset
):
    path = tmp_path / "cache" / "epss.json"
    monkeypatch.setattr(epss_refresh, "download_epss", lambda: dataset)
    before = datetime.now(timezone.utc)

    result = epss_refresh.refresh_epss_cache(path)

    after = datetime.now(timezone.utc)
    assert result.model_version == dataset.model_version
    assert result.score_date == dataset.score_date
    assert result.records == dataset.records
    assert before <= result.retrieved_at <= after
    assert result.retrieved_at.utcoffset() == timedelta(0)
    assert read_epss_cache(path) == result
    assert list(path.parent.iterdir()) == [path]


def test_successful_refresh_replaces_cache(
    tmp_path, monkeypatch, dataset
):
    path = tmp_path / "epss.json"
    original = seed_cache(path, dataset)
    monkeypatch.setattr(epss_refresh, "download_epss", lambda: dataset)

    result = epss_refresh.refresh_epss_cache(path)

    assert path.read_bytes() != original
    assert read_epss_cache(path) == result


@pytest.mark.parametrize(
    "error_type",
    [requests.ConnectionError, requests.Timeout, requests.HTTPError],
)
def test_download_failure_preserves_cache(
    tmp_path, monkeypatch, dataset, error_type
):
    path = tmp_path / "epss.json"
    original = seed_cache(path, dataset)

    def fail_download():
        raise error_type("simulated download failure")

    monkeypatch.setattr(epss_refresh, "download_epss", fail_download)

    with pytest.raises(error_type):
        epss_refresh.refresh_epss_cache(path)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_invalid_dataset_preserves_cache(
    tmp_path, monkeypatch, dataset
):
    path = tmp_path / "epss.json"
    original = seed_cache(path, dataset)
    invalid = EpssDataset(
        model_version=dataset.model_version,
        score_date=date(2026, 10, 25),
        records=dataset.records,
    )
    monkeypatch.setattr(epss_refresh, "download_epss", lambda: invalid)

    with pytest.raises(ValidationError, match="score dates must match"):
        epss_refresh.refresh_epss_cache(path)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_parse_failure_preserves_cache(
    tmp_path, monkeypatch, dataset
):
    path = tmp_path / "epss.json"
    original = seed_cache(path, dataset)

    def fail_download():
        raise ValueError("Invalid EPSS metadata.")

    monkeypatch.setattr(epss_refresh, "download_epss", fail_download)

    with pytest.raises(ValueError, match="metadata"):
        epss_refresh.refresh_epss_cache(path)

    assert path.read_bytes() == original


@pytest.mark.parametrize("operation", ["replace", "fsync"])
def test_storage_failure_preserves_cache(
    tmp_path, monkeypatch, dataset, operation
):
    path = tmp_path / "epss.json"
    original = seed_cache(path, dataset)
    monkeypatch.setattr(epss_refresh, "download_epss", lambda: dataset)

    def fail(*args, **kwargs):
        raise OSError("simulated storage failure")

    monkeypatch.setattr(epss_cache_io.os, operation, fail)

    with pytest.raises(OSError, match="storage failure"):
        epss_refresh.refresh_epss_cache(path)

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_failed_first_download_creates_no_cache(tmp_path, monkeypatch):
    path = tmp_path / "cache" / "epss.json"

    def fail_download():
        raise requests.ConnectionError("simulated download failure")

    monkeypatch.setattr(epss_refresh, "download_epss", fail_download)

    with pytest.raises(requests.ConnectionError):
        epss_refresh.refresh_epss_cache(path)

    assert not path.parent.exists()