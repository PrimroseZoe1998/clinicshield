import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

from clinicshield.feed_freshness import (
    FeedFreshness,
    check_feed_freshness,
)
from clinicshield.kev_cache import KevSnapshot


@dataclass(frozen=True)
class KevLookup:
    status: Literal["listed", "not_listed", "unknown"]
    catalog_contains_cve: bool | None
    retrieved_at: datetime | None
    catalog_version: str | None
    reasons: tuple[str, ...] = ()


def lookup_kev(
    vulnerability_id: str,
    snapshot: KevSnapshot | None,
    *,
    now: datetime,
    max_age: timedelta,
) -> KevLookup:
    """Look up one exact CVE without treating missing data as absence."""
    check_feed_freshness(None, now=now, max_age=max_age)

    if not isinstance(vulnerability_id, str) or not re.fullmatch(
        r"CVE-[0-9]{4}-[0-9]{4,19}", vulnerability_id
    ):
        raise ValueError("KEV lookup requires a valid CVE ID.")

    if snapshot is None:
        return KevLookup(
            status="unknown",
            catalog_contains_cve=None,
            retrieved_at=None,
            catalog_version=None,
            reasons=("KEV cache is missing.",),
        )

    contains = any(
        entry.cveID == vulnerability_id
        for entry in snapshot.catalog.vulnerabilities
    )
    reasons = []

    for label, timestamp in (
        ("retrieval", snapshot.retrieved_at),
        ("catalog release", snapshot.catalog.dateReleased),
    ):
        if check_feed_freshness(
            timestamp, now=now, max_age=max_age
        ) is not FeedFreshness.FRESH:
            reasons.append(f"Unresolved KEV {label} freshness.")

    if snapshot.catalog.dateReleased > snapshot.retrieved_at:
        reasons.append("KEV catalog release is after retrieval.")

    return KevLookup(
        status="unknown" if reasons else (
            "listed" if contains else "not_listed"
        ),
        catalog_contains_cve=contains,
        retrieved_at=snapshot.retrieved_at,
        catalog_version=snapshot.catalog.catalogVersion,
        reasons=tuple(reasons),
    )