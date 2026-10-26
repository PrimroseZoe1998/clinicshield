from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from clinicshield.feed_cache import FeedSnapshot
from clinicshield.feed_cache_io import read_feed_cache
from clinicshield.feed_freshness import (
    FeedFreshness,
    check_feed_freshness,
)


@dataclass(frozen=True)
class CachedFeedResult:
    snapshot: FeedSnapshot | None
    freshness: FeedFreshness
    problem: Literal["missing", "invalid", "unreadable"] | None = None


def load_cached_feed(
    path: Path,
    *,
    now: datetime,
    max_age: timedelta,
) -> CachedFeedResult:
    """Load a cache and report its availability and retrieval age."""
    # Validate the clock and age limit before handling cache errors.
    check_feed_freshness(None, now=now, max_age=max_age)

    try:
        snapshot = read_feed_cache(path)
    except ValueError:
        return CachedFeedResult(
            snapshot=None,
            freshness=FeedFreshness.UNAVAILABLE,
            problem="invalid",
        )
    except OSError:
        return CachedFeedResult(
            snapshot=None,
            freshness=FeedFreshness.UNAVAILABLE,
            problem="unreadable",
        )

    if snapshot is None:
        return CachedFeedResult(
            snapshot=None,
            freshness=FeedFreshness.UNAVAILABLE,
            problem="missing",
        )

    return CachedFeedResult(
        snapshot=snapshot,
        freshness=check_feed_freshness(
            snapshot.retrieved_at,
            now=now,
            max_age=max_age,
        ),
    )