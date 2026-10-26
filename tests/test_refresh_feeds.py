from datetime import datetime, timezone

import pytest
import requests

from clinicshield import refresh_feeds
from clinicshield.kev_cache import KevSnapshot
from clinicshield.kev_models import KevCatalog


@pytest.fixture
def snapshot():
    return KevSnapshot(
        retrieved_at=datetime(2026, 10, 26, 12, tzinfo=timezone.utc),
        catalog=KevCatalog(
            catalogVersion="2026.10.23",
            dateReleased="2026-10-23T12:00:00Z",
            count=0,
            vulnerabilities=(),
        ),
    )


def test_success_reports_metadata_and_uses_cache_directory(
    tmp_path, monkeypatch, capsys, snapshot
):
    paths = []

    def fake_refresh(path):
        paths.append(path)
        return snapshot

    monkeypatch.setattr(
        refresh_feeds, "refresh_kev_cache", fake_refresh
    )

    result = refresh_feeds.main(["--cache-dir", str(tmp_path)])

    output = capsys.readouterr()
    assert result == 0
    assert paths == [tmp_path / "kev.json"]
    assert "CISA KEV refreshed" in output.out
    assert "0 entries" in output.out
    assert "2026.10.23" in output.out
    assert snapshot.retrieved_at.isoformat() in output.out
    assert output.err == ""


@pytest.mark.parametrize(
    "error_type",
    [
        requests.ConnectionError,
        requests.Timeout,
        requests.HTTPError,
        ValueError,
        OSError,
    ],
)
def test_expected_failures_return_nonzero(
    tmp_path, monkeypatch, capsys, error_type
):
    def fail_refresh(path):
        raise error_type("internal error details")

    monkeypatch.setattr(
        refresh_feeds, "refresh_kev_cache", fail_refresh
    )

    result = refresh_feeds.main(["--cache-dir", str(tmp_path)])

    output = capsys.readouterr()
    assert result == 1
    assert output.out == ""
    assert "CISA KEV refresh failed" in output.err
    assert error_type.__name__ in output.err
    assert "internal error details" not in output.err


def test_requires_cache_directory(monkeypatch, capsys):
    def unexpected_refresh(path):
        pytest.fail("Refresh must not run without a cache directory.")

    monkeypatch.setattr(
        refresh_feeds, "refresh_kev_cache", unexpected_refresh
    )

    with pytest.raises(SystemExit) as error:
        refresh_feeds.main([])

    assert error.value.code == 2
    assert "--cache-dir" in capsys.readouterr().err


def test_unexpected_errors_propagate(tmp_path, monkeypatch):
    def fail_refresh(path):
        raise RuntimeError("unexpected programming error")

    monkeypatch.setattr(
        refresh_feeds, "refresh_kev_cache", fail_refresh
    )

    with pytest.raises(RuntimeError, match="programming error"):
        refresh_feeds.main(["--cache-dir", str(tmp_path)])