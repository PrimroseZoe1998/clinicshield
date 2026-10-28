from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from clinicshield.epss_cache import EpssSnapshot
from clinicshield.epss_lookup import lookup_epss


NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)
MAX_AGE = timedelta(days=8)
CVE = "CVE-2026-12345"


def make_snapshot(
    *,
    cve=CVE,
    score="0.123456789",
    score_date=None,
    retrieved_at=NOW,
):
    score_date = score_date if score_date is not None else NOW.date()
    return EpssSnapshot(
        retrieved_at=retrieved_at,
        model_version="synthetic-test-model",
        score_date=score_date,
        records=(
            {
                "cve": cve,
                "epss": score,
                "percentile": "0.987654321",
                "score_date": score_date,
            },
        ),
    )


def lookup(snapshot, vulnerability_id=CVE):
    return lookup_epss(
        vulnerability_id,
        snapshot,
        now=NOW,
        max_age=MAX_AGE,
    )


def test_current_score_is_available_with_provenance():
    result = lookup(make_snapshot())

    assert result.status == "available"
    assert result.record is not None
    assert result.record.cve == CVE
    assert result.record.epss == Decimal("0.123456789")
    assert result.record.percentile == Decimal("0.987654321")
    assert result.score_date == NOW.date()
    assert result.retrieved_at == NOW
    assert result.model_version == "synthetic-test-model"
    assert result.source_url
    assert result.reasons == ()


def test_valid_zero_is_available_not_missing():
    result = lookup(make_snapshot(score="0"))

    assert result.status == "available"
    assert result.record is not None
    assert result.record.epss == Decimal("0")


def test_missing_cve_is_not_found_not_zero():
    result = lookup(
        make_snapshot(cve="CVE-2026-12346")
    )

    assert result.status == "not_found"
    assert result.record is None
    assert result.score_date == NOW.date()
    assert result.reasons == ()


def test_missing_cache_is_unknown():
    result = lookup(None)

    assert result.status == "unknown"
    assert result.record is None
    assert result.source_url is None
    assert result.retrieved_at is None
    assert result.score_date is None
    assert result.model_version is None
    assert result.reasons


@pytest.mark.parametrize("listed", [True, False])
def test_stale_scores_do_not_establish_current_coverage(listed):
    result = lookup(make_snapshot(
        cve=CVE if listed else "CVE-2026-12346",
        score_date=(NOW - timedelta(days=9)).date(),
    ))

    assert result.status == "unknown"
    assert (result.record is not None) is listed
    assert "EPSS score date is stale." in result.reasons


def test_exact_score_age_boundary_is_available():
    result = lookup(make_snapshot(
        score_date=(NOW - timedelta(days=8)).date(),
    ))

    assert result.status == "available"


def test_future_score_date_requires_review():
    result = lookup(make_snapshot(
        score_date=(NOW + timedelta(days=1)).date(),
    ))

    assert result.status == "unknown"
    assert "EPSS score date is in the future." in result.reasons


@pytest.mark.parametrize(
    "retrieved_at",
    [
        NOW - MAX_AGE - timedelta(microseconds=1),
        NOW + timedelta(seconds=1),
    ],
)
def test_stale_or_future_retrieval_requires_review(retrieved_at):
    result = lookup(make_snapshot(retrieved_at=retrieved_at))

    assert result.status == "unknown"
    assert result.record is not None
    assert "EPSS retrieval freshness requires review." in result.reasons


def test_exact_retrieval_age_boundary_is_available():
    timestamp = NOW - MAX_AGE
    result = lookup(make_snapshot(
        retrieved_at=timestamp,
        score_date=timestamp.date(),
    ))

    assert result.status == "available"


def test_score_date_after_retrieval_requires_review():
    result = lookup(make_snapshot(
        retrieved_at=NOW - timedelta(days=1),
    ))

    assert result.status == "unknown"
    assert "EPSS score date is after retrieval." in result.reasons


def test_score_age_uses_utc_calendar_date():
    instant = NOW.replace(hour=1)
    local_time = instant.astimezone(
        timezone(timedelta(hours=-4))
    )
    snapshot = make_snapshot(retrieved_at=instant)

    result = lookup_epss(
        CVE,
        snapshot,
        now=local_time,
        max_age=MAX_AGE,
        max_score_age_days=0,
    )

    assert result.status == "available"


@pytest.mark.parametrize(
    "identifier",
    ["", "CVE-2026-123", "cve-2026-12345", "TEST-001", None, 123],
)
def test_rejects_invalid_cve_identifier(identifier):
    with pytest.raises(ValueError, match="valid CVE"):
        lookup(None, identifier)


@pytest.mark.parametrize("age", [-1, True, 1.5, "8"])
def test_rejects_invalid_score_age_limit(age):
    with pytest.raises(ValueError, match="whole days"):
        lookup_epss(
            CVE,
            None,
            now=NOW,
            max_age=MAX_AGE,
            max_score_age_days=age,
        )


@pytest.mark.parametrize(
    "now,max_age",
    [
        (NOW.replace(tzinfo=None), MAX_AGE),
        (NOW, timedelta(0)),
        (NOW, timedelta(seconds=-1)),
    ],
)
def test_rejects_invalid_clock_configuration(now, max_age):
    with pytest.raises(ValueError):
        lookup_epss(CVE, None, now=now, max_age=max_age)


def test_does_not_modify_snapshot():
    snapshot = make_snapshot()
    original = snapshot.model_dump()

    lookup(snapshot)

    assert snapshot.model_dump() == original