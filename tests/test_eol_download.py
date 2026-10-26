import json

import pytest
import requests
from pydantic import ValidationError

from clinicshield import eol_download


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
        }
    ).encode("utf-8")


def install_response(monkeypatch, response):
    monkeypatch.setattr(
        eol_download.requests,
        "get",
        lambda *args, **kwargs: response,
    )


def test_downloads_and_validates_product(monkeypatch, payload):
    response = FakeResponse([payload[:20], b"", payload[20:]])
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return response

    monkeypatch.setattr(eol_download.requests, "get", fake_get)

    result = eol_download.download_eol("python")

    assert result.result.name == "python"
    assert result.result.releases[0].isEol is True
    assert response.closed
    assert calls == [
        (
            f"{eol_download.EOL_BASE_URL}python/",
            {
                "timeout": (10, 30),
                "stream": True,
                "allow_redirects": False,
            },
        )
    ]


@pytest.mark.parametrize(
    "product",
    ["", "Python", "../python", "python/extra", "python?x=1", None, 123],
)
def test_rejects_invalid_slug_before_request(monkeypatch, product):
    def unexpected_get(*args, **kwargs):
        pytest.fail("Invalid slugs must not trigger requests.")

    monkeypatch.setattr(eol_download.requests, "get", unexpected_get)

    with pytest.raises(ValueError, match="slug"):
        eol_download.download_eol(product)


def test_accepts_hyphenated_slug(monkeypatch, payload):
    data = json.loads(payload)
    data["result"]["name"] = "example-product"
    response = FakeResponse([json.dumps(data).encode("utf-8")])
    install_response(monkeypatch, response)

    result = eol_download.download_eol("example-product")

    assert result.result.name == "example-product"


def test_rejects_different_product(monkeypatch, payload):
    response = FakeResponse([payload])
    install_response(monkeypatch, response)

    with pytest.raises(ValueError, match="different product"):
        eol_download.download_eol("other-product")

    assert response.closed


@pytest.mark.parametrize("status", [403, 404, 500])
def test_http_errors_propagate(monkeypatch, status):
    response = FakeResponse(status_code=status)
    install_response(monkeypatch, response)

    with pytest.raises(requests.HTTPError):
        eol_download.download_eol("python")

    assert response.closed


@pytest.mark.parametrize("status", [204, 301, 302])
def test_rejects_non_200_responses(monkeypatch, status):
    response = FakeResponse(status_code=status)
    install_response(monkeypatch, response)

    with pytest.raises(ValueError, match="HTTP 200"):
        eol_download.download_eol("python")

    assert response.closed


@pytest.mark.parametrize(
    "error_type",
    [requests.ConnectTimeout, requests.ConnectionError],
)
def test_connection_errors_propagate(monkeypatch, error_type):
    def fail_get(*args, **kwargs):
        raise error_type("simulated connection failure")

    monkeypatch.setattr(eol_download.requests, "get", fail_get)

    with pytest.raises(error_type):
        eol_download.download_eol("python")


@pytest.mark.parametrize("body", [b"", b"{", b"{}", b"\xff"])
def test_rejects_invalid_payload(monkeypatch, body):
    response = FakeResponse([body])
    install_response(monkeypatch, response)

    with pytest.raises(ValidationError):
        eol_download.download_eol("python")

    assert response.closed


def test_accepts_exact_size_limit(monkeypatch, payload):
    monkeypatch.setattr(
        eol_download, "MAX_DOWNLOAD_BYTES", len(payload)
    )
    install_response(monkeypatch, FakeResponse([payload]))

    assert eol_download.download_eol("python").result.name == "python"


def test_rejects_oversized_download(monkeypatch):
    monkeypatch.setattr(eol_download, "MAX_DOWNLOAD_BYTES", 10)
    response = FakeResponse([b"x" * 6, b"x" * 5])
    install_response(monkeypatch, response)

    with pytest.raises(ValueError, match="size limit"):
        eol_download.download_eol("python")

    assert response.closed


def test_stream_failure_closes_response(monkeypatch):
    class BrokenResponse(FakeResponse):
        def iter_content(self, chunk_size):
            yield b"partial"
            raise requests.ConnectionError("stream interrupted")

    response = BrokenResponse()
    install_response(monkeypatch, response)

    with pytest.raises(requests.ConnectionError, match="interrupted"):
        eol_download.download_eol("python")

    assert response.closed