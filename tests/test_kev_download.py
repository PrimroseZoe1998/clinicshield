import json

import pytest
import requests
from pydantic import ValidationError

from clinicshield import kev_download


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


@pytest.fixture
def payload():
    return json.dumps(
        {
            "catalogVersion": "2026.10.26",
            "dateReleased": "2026-10-26T12:00:00Z",
            "count": 0,
            "vulnerabilities": [],
        }
    ).encode("utf-8")


def install_response(monkeypatch, response):
    monkeypatch.setattr(
        kev_download.requests,
        "get",
        lambda *args, **kwargs: response,
    )


def test_downloads_and_validates_catalog(monkeypatch, payload):
    response = FakeResponse([payload[:20], b"", payload[20:]])
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return response

    monkeypatch.setattr(kev_download.requests, "get", fake_get)

    catalog = kev_download.download_kev()

    assert catalog.catalogVersion == "2026.10.26"
    assert catalog.vulnerabilities == ()
    assert response.closed
    assert calls == [
        (
            kev_download.KEV_URL,
            {
                "timeout": (10, 30),
                "stream": True,
                "allow_redirects": False,
            },
        )
    ]


@pytest.mark.parametrize("status", [403, 404, 500])
def test_http_errors_propagate(monkeypatch, status):
    response = FakeResponse(status_code=status)
    install_response(monkeypatch, response)

    with pytest.raises(requests.HTTPError):
        kev_download.download_kev()

    assert response.closed


@pytest.mark.parametrize("status", [204, 301, 302])
def test_rejects_non_200_responses(monkeypatch, status):
    response = FakeResponse(status_code=status)
    install_response(monkeypatch, response)

    with pytest.raises(ValueError, match="HTTP 200"):
        kev_download.download_kev()

    assert response.closed


@pytest.mark.parametrize(
    "error",
    [
        requests.ConnectTimeout("connection timeout"),
        requests.ConnectionError("connection failed"),
    ],
)
def test_connection_errors_propagate(monkeypatch, error):
    def fail_get(*args, **kwargs):
        raise error

    monkeypatch.setattr(kev_download.requests, "get", fail_get)

    with pytest.raises(type(error)):
        kev_download.download_kev()


@pytest.mark.parametrize("body", [b"", b"{", b"{}", b"\xff"])
def test_rejects_invalid_payload(monkeypatch, body):
    response = FakeResponse([body])
    install_response(monkeypatch, response)

    with pytest.raises(ValidationError):
        kev_download.download_kev()

    assert response.closed


def test_accepts_exact_size_limit(monkeypatch, payload):
    monkeypatch.setattr(
        kev_download, "MAX_DOWNLOAD_BYTES", len(payload)
    )
    response = FakeResponse([payload])
    install_response(monkeypatch, response)

    assert kev_download.download_kev().count == 0
    assert response.closed


def test_rejects_oversized_stream(monkeypatch):
    monkeypatch.setattr(kev_download, "MAX_DOWNLOAD_BYTES", 10)
    response = FakeResponse([b"x" * 6, b"x" * 5])
    install_response(monkeypatch, response)

    with pytest.raises(ValueError, match="size limit"):
        kev_download.download_kev()

    assert response.closed


def test_stream_failure_propagates_and_closes_response(monkeypatch):
    class BrokenResponse(FakeResponse):
        def iter_content(self, chunk_size):
            yield b'{"catalogVersion":'
            raise requests.ConnectionError("stream interrupted")

    response = BrokenResponse()
    install_response(monkeypatch, response)

    with pytest.raises(requests.ConnectionError, match="interrupted"):
        kev_download.download_kev()

    assert response.closed