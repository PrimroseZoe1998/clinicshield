import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Literal

from clinicshield.epss_cache import EpssSnapshot
from clinicshield.epss_models import EpssRecord
from clinicshield.feed_freshness import (
    FeedFreshness,
    check_feed_freshness,
)


@dataclass(frozen=True)
class EpssLookup:
    status: Literal["available", "not_found", "unknown"]
    record: EpssRecord | None
    source_url: str | None
    retrieved_at: datetime | None
    score_date: date | None
    model_version: str | None
    reasons: tuple[str, ...] = ()


def lookup_epss(
    vulnerability_id: str,
    snapshot: EpssSnapshot | None,
    *,
    now: datetime,
    max_age: timedelta,
    max_score_age_days: int = 8,
) -> EpssLookup:
    """Look up an exact CVE without inventing a zero score."""
    check_feed_freshness(None, now=now, max_age=max_age)

    if (
        type(max_score_age_days) is not int
        or max_score_age_days < 0
    ):
        raise ValueError("Maximum score age must be nonnegative whole days.")

    if not isinstance(vulnerability_id, str) or not re.fullmatch(
        r"CVE-[0-9]{4}-[0-9]{4,19}", vulnerability_id
    ):
        raise ValueError("EPSS lookup requires a valid CVE ID.")

    if snapshot is None:
        return EpssLookup(
            status="unknown",
            record=None,
            source_url=None,
            retrieved_at=None,
            score_date=None,
            model_version=None,
            reasons=("EPSS cache is missing.",),
        )

    record = next(
        (item for item in snapshot.records if item.cve == vulnerability_id),
        None,
    )
    reasons = []

    if check_feed_freshness(
        snapshot.retrieved_at, now=now, max_age=max_age
    ) is not FeedFreshness.FRESH:
        reasons.append("EPSS retrieval freshness requires review.")

    today = now.astimezone(timezone.utc).date()
    score_age = (today - snapshot.score_date).days

    if score_age < 0:
        reasons.append("EPSS score date is in the future.")
    elif score_age > max_score_age_days:
        reasons.append("EPSS score date is stale.")

    retrieval_date = snapshot.retrieved_at.astimezone(timezone.utc).date()
    if snapshot.score_date > retrieval_date:
        reasons.append("EPSS score date is after retrieval.")

    return EpssLookup(
        status="unknown" if reasons else (
            "available" if record is not None else "not_found"
        ),
        record=record,
        source_url=snapshot.source_url,
        retrieved_at=snapshot.retrieved_at,
        score_date=snapshot.score_date,
        model_version=snapshot.model_version,
        reasons=tuple(reasons),
    )