from datetime import datetime, timedelta, timezone

import pytest
import requests
from pydantic import ValidationError

from clinicshield import eol_cache_io, eol_refresh
from clinicshield.eol_cache import EolSnapshot
from clinicshield.eol_cache_io import read_eol_cache, write_eol_cache
from clinicshield.eol_download import EOL_BASE_URL
from clinicshield.eol_models import EolResponse


@pytest.fixture
def response():
    return EolResponse(
        schema_version="1.2.1",
        generated_at="2026-10-26T00:00:00Z",
        last_modified="2026-10-25T12:00:00Z",
        result={
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
    )


def seed_cache(path, response):
    snapshot = EolSnapshot(
        source_url=f"{EOL_BASE_URL}python/",
        retrieved_at=datetime(2026, 10, 25, tzinfo=timezone.utc),
        product="python",
        response=response,
    )
    write_eol_cache(path, snapshot)
    return path.read_bytes()


def test_successful_refresh_creates_cache(
    tmp_path, monkeypatch, response
):
    path = tmp_path / "cache" / "python.json"
    products = []

    def fake_download(product):
        products.append(product)
        return response

    monkeypatch.setattr(eol_refresh, "download_eol", fake_download)
    before = datetime.now(timezone.utc)

    result = eol_refresh.refresh_eol_cache(path, product="python")

    after = datetime.now(timezone.utc)
    assert products == ["python"]
    assert result.product == "python"
    assert result.source_url == f"{EOL_BASE_URL}python/"
    assert result.response == response
    assert before <= result.retrieved_at <= after
    assert result.retrieved_at.utcoffset() == timedelta(0)
    assert read_eol_cache(path) == result
    assert list(path.parent.iterdir()) == [path]


def test_successful_refresh_replaces_cache(
    tmp_path, monkeypatch, response
):
    path = tmp_path / "python.json"
    original = seed_cache(path, response)
    monkeypatch.setattr(
        eol_refresh, "download_eol", lambda product: response
    )

    result = eol_refresh.refresh_eol_cache(path, product="python")

    assert path.read_bytes() != original
    assert read_eol_cache(path) == result


@pytest.mark.parametrize(
    "error_type",
    [requests.ConnectionError, requests.Timeout, requests.HTTPError],
)
def test_download_failure_preserves_cache(
    tmp_path, monkeypatch, response, error_type
):
    path = tmp_path / "python.json"
    original = seed_cache(path, response)

    def fail_download(product):
        raise error_type("simulated download failure")

    monkeypatch.setattr(eol_refresh, "download_eol", fail_download)

    with pytest.raises(error_type):
        eol_refresh.refresh_eol_cache(path, product="python")

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_mismatched_product_preserves_cache(
    tmp_path, monkeypatch, response
):
    path = tmp_path / "python.json"
    original = seed_cache(path, response)
    data = response.model_dump(mode="json")
    data["result"]["name"] = "other-product"
    mismatched = EolResponse.model_validate(data)
    monkeypatch.setattr(
        eol_refresh, "download_eol", lambda product: mismatched
    )

    with pytest.raises(ValidationError, match="match the product"):
        eol_refresh.refresh_eol_cache(path, product="python")

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_validation_failure_preserves_cache(
    tmp_path, monkeypatch, response
):
    path = tmp_path / "python.json"
    original = seed_cache(path, response)

    def invalid_download(product):
        return EolResponse.model_validate_json("{}")

    monkeypatch.setattr(eol_refresh, "download_eol", invalid_download)

    with pytest.raises(ValidationError):
        eol_refresh.refresh_eol_cache(path, product="python")

    assert path.read_bytes() == original


@pytest.mark.parametrize("operation", ["replace", "fsync"])
def test_storage_failure_preserves_cache(
    tmp_path, monkeypatch, response, operation
):
    path = tmp_path / "python.json"
    original = seed_cache(path, response)
    monkeypatch.setattr(
        eol_refresh, "download_eol", lambda product: response
    )

    def fail(*args, **kwargs):
        raise OSError("simulated storage failure")

    monkeypatch.setattr(eol_cache_io.os, operation, fail)

    with pytest.raises(OSError, match="storage failure"):
        eol_refresh.refresh_eol_cache(path, product="python")

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_failed_first_download_creates_no_cache(
    tmp_path, monkeypatch
):
    path = tmp_path / "cache" / "python.json"

    def fail_download(product):
        raise requests.ConnectionError("simulated download failure")

    monkeypatch.setattr(eol_refresh, "download_eol", fail_download)

    with pytest.raises(requests.ConnectionError):
        eol_refresh.refresh_eol_cache(path, product="python")

    assert not path.parent.exists()