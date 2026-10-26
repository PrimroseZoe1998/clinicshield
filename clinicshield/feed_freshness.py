from datetime import datetime, timedelta
from enum import Enum


class FeedFreshness(str, Enum):
    FRESH = "fresh"
    STALE = "stale"
    UNAVAILABLE = "unavailable"
    NEEDS_REVIEW = "needs_review"


def check_feed_freshness(
    retrieved_at: datetime | None,
    *,
    now: datetime,
    max_age: timedelta,
) -> FeedFreshness:
    """Check cache age using an explicit clock and freshness limit."""
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Current time must include a timezone.")

    if max_age <= timedelta(0):
        raise ValueError("Maximum feed age must be positive.")

    if retrieved_at is None:
        return FeedFreshness.UNAVAILABLE

    if (
        retrieved_at.tzinfo is None
        or retrieved_at.utcoffset() is None
    ):
        raise ValueError("Feed retrieval time must include a timezone.")

    age = now - retrieved_at

    if age < timedelta(0):
        return FeedFreshness.NEEDS_REVIEW

    if age > max_age:
        return FeedFreshness.STALE

    return FeedFreshness.FRESH