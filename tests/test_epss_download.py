import gzip
from decimal import Decimal

import pytest
import requests

from clinicshield import epss_download


CSV = (
    "#model_version:v2026.06.15,score_date:2026-10-26\n"
    "cve,epss,percentile\n"
    "CVE-2026-12345,0.123456789,0.987654321\n"
).encode("utf-8")


class FakeResponse:
    def __init__(self, chunks=(), status_code=200):
        self.chunks = chunks
        self.status_code = status_code
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError("simulated HTTP failure")

    def iter_content(self, chunk_size):
        yield from self.chunks


def install_response(monkeypatch, response):
    monkeypatch.setattr(
        epss_download.requests,
        "get",
        lambda *args, **kwargs: response,
    )


def test_downloads_decompresses_and_parses(monkeypatch):
    payload = gzip.compress(CSV)
    response = FakeResponse([payload[:10], b"", payload[10:]])
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return response

    monkeypatch.setattr(epss_download.requests, "get", fake_get)

    dataset = epss_download.download_epss()

    assert dataset.model_version == "v2026.06.15"
    assert len(dataset.records) == 1
    assert dataset.records[0].epss == Decimal("0.123456789")
    assert response.closed
    assert calls == [
        (
            epss_download.EPSS_URL,
            {
                "timeout": (10, 60),
                "stream": True,
                "allow_redirects": True,
            },
        )
    ]


@pytest.mark.parametrize("status", [403, 404, 500])
def test_http_errors_propagate(monkeypatch, status):
    response = FakeResponse(status_code=status)
    install_response(monkeypatch, response)

    with pytest.raises(requests.HTTPError):
        epss_download.download_epss()

    assert response.closed


@pytest.mark.parametrize("status", [204, 302])
def test_rejects_non_200_response(monkeypatch, status):
    response = FakeResponse(status_code=status)
    install_response(monkeypatch, response)

    with pytest.raises(ValueError, match="HTTP 200"):
        epss_download.download_epss()

    assert response.closed


@pytest.mark.parametrize(
    "error_type",
    [requests.ConnectTimeout, requests.ConnectionError],
)
def test_connection_errors_propagate(monkeypatch, error_type):
    def fail_get(*args, **kwargs):
        raise error_type("simulated connection failure")

    monkeypatch.setattr(epss_download.requests, "get", fail_get)

    with pytest.raises(error_type):
        epss_download.download_epss()


@pytest.mark.parametrize(
    "payload",
    [b"not gzip", gzip.compress(CSV)[:-8]],
)
def test_rejects_invalid_gzip(monkeypatch, payload):
    response = FakeResponse([payload])
    install_response(monkeypatch, response)

    with pytest.raises(ValueError, match="gzip"):
        epss_download.download_epss()

    assert response.closed


def test_rejects_invalid_utf8(monkeypatch):
    response = FakeResponse([gzip.compress(b"\xff")])
    install_response(monkeypatch, response)

    with pytest.raises(UnicodeDecodeError):
        epss_download.download_epss()

    assert response.closed


def test_rejects_invalid_csv(monkeypatch):
    response = FakeResponse([gzip.compress(b"invalid CSV")])
    install_response(monkeypatch, response)

    with pytest.raises(ValueError):
        epss_download.download_epss()

    assert response.closed


def test_accepts_exact_download_limit(monkeypatch):
    payload = gzip.compress(CSV)
    monkeypatch.setattr(
        epss_download, "MAX_DOWNLOAD_BYTES", len(payload)
    )
    install_response(monkeypatch, FakeResponse([payload]))

    assert len(epss_download.download_epss().records) == 1


def test_rejects_oversized_download(monkeypatch):
    monkeypatch.setattr(epss_download, "MAX_DOWNLOAD_BYTES", 10)
    response = FakeResponse([b"x" * 6, b"x" * 5])
    install_response(monkeypatch, response)

    with pytest.raises(ValueError, match="download exceeds"):
        epss_download.download_epss()

    assert response.closed


def test_accepts_exact_decompressed_limit(monkeypatch):
    monkeypatch.setattr(
        epss_download, "MAX_DECOMPRESSED_BYTES", len(CSV)
    )
    install_response(
        monkeypatch, FakeResponse([gzip.compress(CSV)])
    )

    assert len(epss_download.download_epss().records) == 1


def test_rejects_oversized_decompressed_data(monkeypatch):
    monkeypatch.setattr(
        epss_download, "MAX_DECOMPRESSED_BYTES", len(CSV) - 1
    )
    response = FakeResponse([gzip.compress(CSV)])
    install_response(monkeypatch, response)

    with pytest.raises(ValueError, match="Decompressed"):
        epss_download.download_epss()

    assert response.closed


def test_stream_failure_closes_response(monkeypatch):
    class BrokenResponse(FakeResponse):
        def iter_content(self, chunk_size):
            yield b"partial"
            raise requests.ConnectionError("stream interrupted")

    response = BrokenResponse()
    install_response(monkeypatch, response)

    with pytest.raises(requests.ConnectionError, match="interrupted"):
        epss_download.download_epss()

    assert response.closed