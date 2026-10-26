from datetime import datetime, timezone

import pytest
import requests

from clinicshield import refresh_feeds
from clinicshield.epss_cache import EpssSnapshot
from clinicshield.kev_cache import KevSnapshot
from clinicshield.kev_models import KevCatalog
from clinicshield.eol_cache import EolSnapshot
from clinicshield.eol_download import EOL_BASE_URL

@pytest.fixture
def feeds(tmp_path, monkeypatch):
    retrieved_at = datetime(2026, 10, 26, 14, tzinfo=timezone.utc)
    kev = KevSnapshot(
        retrieved_at=retrieved_at,
        catalog=KevCatalog(
            catalogVersion="2026.10.23",
            dateReleased="2026-10-23T12:00:00Z",
            count=0,
            vulnerabilities=(),
        ),
    )
    epss = EpssSnapshot(
        retrieved_at=retrieved_at,
        model_version="v2026.06.15",
        score_date="2026-10-26",
        records=(
            {
                "cve": "CVE-2026-12345",
                "epss": "0.1",
                "percentile": "0.9",
                "score_date": "2026-10-26",
            },
        ),
    )
    calls = []

    def fake_kev(path):
        calls.append(("kev", path))
        return kev

    def fake_epss(path):
        calls.append(("epss", path))
        return epss

    monkeypatch.setattr(refresh_feeds, "refresh_kev_cache", fake_kev)
    monkeypatch.setattr(refresh_feeds, "refresh_epss_cache", fake_epss)
    return kev, epss, calls


def test_refreshes_both_feeds(tmp_path, capsys, feeds):
    kev, epss, calls = feeds

    result = refresh_feeds.main(["--cache-dir", str(tmp_path)])

    output = capsys.readouterr()
    assert result == 0
    assert calls == [
        ("kev", tmp_path / "kev.json"),
        ("epss", tmp_path / "epss.json"),
    ]
    assert "CISA KEV refreshed" in output.out
    assert "0 entries" in output.out
    assert kev.catalog.catalogVersion in output.out
    assert "FIRST EPSS refreshed" in output.out
    assert "1 records" in output.out
    assert epss.model_version in output.out
    assert str(epss.score_date) in output.out
    assert epss.retrieved_at.isoformat() in output.out
    assert output.err == ""


@pytest.mark.parametrize("failed_feed", ["kev", "epss"])
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
def test_one_failure_still_attempts_both_feeds(
    tmp_path, monkeypatch, capsys, feeds, failed_feed, error_type
):
    _, _, calls = feeds

    def fail_refresh(path):
        calls.append((failed_feed, path))
        raise error_type("internal error details")

    monkeypatch.setattr(
        refresh_feeds,
        f"refresh_{failed_feed}_cache",
        fail_refresh,
    )

    result = refresh_feeds.main(["--cache-dir", str(tmp_path)])

    output = capsys.readouterr()
    assert result == 1
    assert calls == [
        ("kev", tmp_path / "kev.json"),
        ("epss", tmp_path / "epss.json"),
    ]
    failed_name = "CISA KEV" if failed_feed == "kev" else "FIRST EPSS"
    successful_name = "FIRST EPSS" if failed_feed == "kev" else "CISA KEV"
    assert f"{failed_name} refresh failed" in output.err
    assert error_type.__name__ in output.err
    assert "internal error details" not in output.err
    assert f"{successful_name} refreshed" in output.out
    assert f"{failed_name} refreshed" not in output.out


def test_both_failures_are_reported(
    tmp_path, monkeypatch, capsys, feeds
):
    _, _, calls = feeds

    def fail_kev(path):
        calls.append(("kev", path))
        raise requests.Timeout("KEV timeout")

    def fail_epss(path):
        calls.append(("epss", path))
        raise ValueError("invalid EPSS data")

    monkeypatch.setattr(refresh_feeds, "refresh_kev_cache", fail_kev)
    monkeypatch.setattr(refresh_feeds, "refresh_epss_cache", fail_epss)

    assert refresh_feeds.main(["--cache-dir", str(tmp_path)]) == 1

    output = capsys.readouterr()
    assert [name for name, _ in calls] == ["kev", "epss"]
    assert "CISA KEV refresh failed" in output.err
    assert "FIRST EPSS refresh failed" in output.err
    assert output.out == ""


def test_requires_cache_directory(capsys, feeds):
    _, _, calls = feeds

    with pytest.raises(SystemExit) as error:
        refresh_feeds.main([])

    assert error.value.code == 2
    assert "--cache-dir" in capsys.readouterr().err
    assert calls == []


@pytest.mark.parametrize("failed_feed", ["kev", "epss"])
def test_unexpected_errors_propagate(
    tmp_path, monkeypatch, feeds, failed_feed
):
    def fail_refresh(path):
        raise RuntimeError("unexpected programming error")

    monkeypatch.setattr(
        refresh_feeds,
        f"refresh_{failed_feed}_cache",
        fail_refresh,
    )

    with pytest.raises(RuntimeError, match="programming error"):
        refresh_feeds.main(["--cache-dir", str(tmp_path)])

def make_eol_snapshot(product):
    return EolSnapshot(
        source_url=f"{EOL_BASE_URL}{product}/",
        retrieved_at=datetime(2026, 10, 26, 14, tzinfo=timezone.utc),
        product=product,
        response={
            "schema_version": "1.2.1",
            "generated_at": "2026-10-26T00:00:00Z",
            "last_modified": "2026-10-25T12:00:00Z",
            "result": {
                "name": product,
                "label": product,
                "releases": [],
            },
        },
    )


def test_refreshes_selected_eol_products(
    tmp_path, monkeypatch, capsys, feeds
):
    calls = []

    def fake_refresh(path, *, product):
        calls.append((path, product))
        return make_eol_snapshot(product)

    monkeypatch.setattr(
        refresh_feeds, "refresh_eol_cache", fake_refresh
    )

    result = refresh_feeds.main([
        "--cache-dir", str(tmp_path),
        "--eol-product", "python",
        "--eol-product", "ruby",
    ])

    output = capsys.readouterr()
    assert result == 0
    assert calls == [
        (tmp_path / "eol-python.json", "python"),
        (tmp_path / "eol-ruby.json", "ruby"),
    ]
    assert "endoflife.date refreshed: python" in output.out
    assert "endoflife.date refreshed: ruby" in output.out
    assert output.err == ""


def test_no_eol_products_means_no_eol_requests(
    tmp_path, monkeypatch, feeds
):
    def unexpected_refresh(*args, **kwargs):
        pytest.fail("No lifecycle products were selected.")

    monkeypatch.setattr(
        refresh_feeds, "refresh_eol_cache", unexpected_refresh
    )

    assert refresh_feeds.main(["--cache-dir", str(tmp_path)]) == 0


def test_duplicate_eol_products_refresh_once(
    tmp_path, monkeypatch, feeds
):
    calls = []

    def fake_refresh(path, *, product):
        calls.append(product)
        return make_eol_snapshot(product)

    monkeypatch.setattr(
        refresh_feeds, "refresh_eol_cache", fake_refresh
    )

    assert refresh_feeds.main([
        "--cache-dir", str(tmp_path),
        "--eol-product", "python",
        "--eol-product", "python",
    ]) == 0
    assert calls == ["python"]


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
def test_eol_failure_does_not_stop_next_product(
    tmp_path, monkeypatch, capsys, feeds, error_type
):
    calls = []

    def fake_refresh(path, *, product):
        calls.append(product)
        if product == "python":
            raise error_type("internal error details")
        return make_eol_snapshot(product)

    monkeypatch.setattr(
        refresh_feeds, "refresh_eol_cache", fake_refresh
    )

    result = refresh_feeds.main([
        "--cache-dir", str(tmp_path),
        "--eol-product", "python",
        "--eol-product", "ruby",
    ])

    output = capsys.readouterr()
    assert result == 1
    assert calls == ["python", "ruby"]
    assert "CISA KEV refreshed" in output.out
    assert "FIRST EPSS refreshed" in output.out
    assert "endoflife.date refreshed: ruby" in output.out
    assert "endoflife.date refresh failed for 'python'" in output.err
    assert error_type.__name__ in output.err
    assert "internal error details" not in output.err


@pytest.mark.parametrize(
    "product",
    ["../python", "Python", "python/extra", "python?x=1"],
)
def test_invalid_eol_slug_does_not_reach_refresher(
    tmp_path, monkeypatch, capsys, feeds, product
):
    def unexpected_refresh(*args, **kwargs):
        pytest.fail("Invalid product must not reach the refresher.")

    monkeypatch.setattr(
        refresh_feeds, "refresh_eol_cache", unexpected_refresh
    )

    result = refresh_feeds.main([
        "--cache-dir", str(tmp_path),
        "--eol-product", product,
    ])

    assert result == 1
    assert "endoflife.date refresh failed" in capsys.readouterr().err


def test_unexpected_eol_error_propagates(
    tmp_path, monkeypatch, feeds
):
    def fail_refresh(*args, **kwargs):
        raise RuntimeError("unexpected programming error")

    monkeypatch.setattr(
        refresh_feeds, "refresh_eol_cache", fail_refresh
    )

    with pytest.raises(RuntimeError, match="programming error"):
        refresh_feeds.main([
            "--cache-dir", str(tmp_path),
            "--eol-product", "python",
        ])