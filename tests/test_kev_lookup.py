from datetime import datetime, timedelta, timezone

import pytest

from clinicshield.kev_cache import KevSnapshot
from clinicshield.kev_lookup import lookup_kev


NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)
MAX_AGE = timedelta(days=8)
CVE = "CVE-2026-12345"


def make_snapshot(
    *,
    retrieved_at=NOW,
    released_at=NOW,
    include_cve=True,
):
    entries = []
    if include_cve:
        entries.append({
            "cveID": CVE,
            "vendorProject": "Example Vendor",
            "product": "Example Product",
            "vulnerabilityName": "Fictional vulnerability",
            "dateAdded": "2026-10-28",
            "shortDescription": "Synthetic test entry.",
            "requiredAction": "Follow fictional vendor guidance.",
            "dueDate": "2026-11-18",
        })

    return KevSnapshot(
        retrieved_at=retrieved_at,
        catalog={
            "catalogVersion": "synthetic-test-catalog",
            "dateReleased": released_at,
            "count": len(entries),
            "vulnerabilities": entries,
        },
    )


def lookup(snapshot, vulnerability_id=CVE):
    return lookup_kev(
        vulnerability_id,
        snapshot,
        now=NOW,
        max_age=MAX_AGE,
    )


def test_current_catalog_reports_exact_cve_as_listed():
    result = lookup(make_snapshot())

    assert result.status == "listed"
    assert result.catalog_contains_cve is True
    assert result.retrieved_at == NOW
    assert result.catalog_version == "synthetic-test-catalog"
    assert result.reasons == ()


def test_other_cve_is_not_listed():
    result = lookup(make_snapshot(), "CVE-2026-12346")

    assert result.status == "not_listed"
    assert result.catalog_contains_cve is False
    assert result.reasons == ()


def test_current_empty_catalog_reports_not_listed():
    result = lookup(make_snapshot(include_cve=False))

    assert result.status == "not_listed"
    assert result.catalog_contains_cve is False


def test_missing_cache_reports_unknown():
    result = lookup(None)

    assert result.status == "unknown"
    assert result.catalog_contains_cve is None
    assert result.retrieved_at is None
    assert result.catalog_version is None
    assert result.reasons


@pytest.mark.parametrize("include_cve", [True, False])
@pytest.mark.parametrize(
    "changes",
    [
        {"retrieved_at": NOW - MAX_AGE - timedelta(microseconds=1)},
        {"released_at": NOW - MAX_AGE - timedelta(microseconds=1)},
        {"retrieved_at": NOW + timedelta(seconds=1)},
        {"released_at": NOW + timedelta(seconds=1)},
    ],
)
def test_unresolved_freshness_preserves_membership_but_reports_unknown(
    include_cve, changes
):
    result = lookup(
        make_snapshot(include_cve=include_cve, **changes)
    )

    assert result.status == "unknown"
    assert result.catalog_contains_cve is include_cve
    assert result.reasons


def test_exact_freshness_boundary_is_accepted():
    timestamp = NOW - MAX_AGE

    result = lookup(make_snapshot(
        retrieved_at=timestamp,
        released_at=timestamp,
    ))

    assert result.status == "listed"


def test_release_after_retrieval_requires_review():
    result = lookup(make_snapshot(
        retrieved_at=NOW - timedelta(hours=1),
        released_at=NOW,
    ))

    assert result.status == "unknown"
    assert "KEV catalog release is after retrieval." in result.reasons


@pytest.mark.parametrize(
    "identifier",
    ["", "CVE-2026-123", "cve-2026-12345", "TEST-001", None, 123],
)
def test_rejects_invalid_cve_identifier(identifier):
    with pytest.raises(ValueError, match="valid CVE"):
        lookup(None, identifier)


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
        lookup_kev(CVE, None, now=now, max_age=max_age)


def test_does_not_modify_snapshot():
    snapshot = make_snapshot()
    original = snapshot.model_dump()

    lookup(snapshot)

    assert snapshot.model_dump() == original