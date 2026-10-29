from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path

from clinicshield.assessment_evidence import AssessmentEvidence
from clinicshield.epss_cache_io import read_epss_cache
from clinicshield.feed_freshness import check_feed_freshness
from clinicshield.kev_cache import read_kev_cache


def load_assessment_caches(
    evidence: AssessmentEvidence,
    directory: Path,
    *,
    now: datetime,
    max_age: timedelta,
) -> tuple[AssessmentEvidence, tuple[str, ...]]:
    """Attach validated public snapshots without inferring applicability."""
    check_feed_freshness(None, now=now, max_age=max_age)
    snapshots = {}
    messages = []
    for name, field, reader, filename in (
        ("KEV", "kev_snapshot", read_kev_cache, "kev.json"),
        ("EPSS", "epss_snapshot", read_epss_cache, "epss.json"),
    ):
        try:
            snapshot = reader(directory / filename)
        except (ValueError, OSError):
            snapshot = None
            messages.append(f"{name} cache is invalid or unreadable; coverage is unavailable.")
        else:
            status = check_feed_freshness(
                snapshot.retrieved_at if snapshot else None,
                now=now,
                max_age=max_age,
            )
            messages.append(f"{name} cache retrieval status: {status.value}.")
            if snapshot:
                messages.append(f"{name} retrieved at {snapshot.retrieved_at.isoformat()}.")
                source_date = (
                    snapshot.catalog.dateReleased.date()
                    if name == "KEV" else snapshot.score_date
                )
                age = (now.date() - source_date).days
                if age < 0 or age > max_age / timedelta(days=1):
                    messages.append(f"{name} source date {source_date} requires freshness review.")
        snapshots[field] = snapshot
    return replace(evidence, **snapshots), tuple(messages)
