from datetime import datetime, timedelta, timezone

import pytest

from clinicshield.feed_freshness import (
    FeedFreshness,
    check_feed_freshness,
)


NOW = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)
MAX_AGE = timedelta(hours=24)


@pytest.mark.parametrize(
    "age,expected",
    [
        (timedelta(0), FeedFreshness.FRESH),
        (timedelta(hours=12), FeedFreshness.FRESH),
        (MAX_AGE, FeedFreshness.FRESH),
        (
            MAX_AGE + timedelta(microseconds=1),
            FeedFreshness.STALE,
        ),
        (timedelta(days=7), FeedFreshness.STALE),
        (timedelta(seconds=-1), FeedFreshness.NEEDS_REVIEW),
    ],
)
def test_feed_age_boundaries(age, expected):
    assert check_feed_freshness(
        NOW - age,
        now=NOW,
        max_age=MAX_AGE,
    ) is expected


def test_missing_feed_is_unavailable():
    assert check_feed_freshness(
        None,
        now=NOW,
        max_age=MAX_AGE,
    ) is FeedFreshness.UNAVAILABLE


def test_equivalent_timezones_produce_same_result():
    offset = timezone(timedelta(hours=-4))
    retrieved_at = (NOW - MAX_AGE).astimezone(offset)

    assert check_feed_freshness(
        retrieved_at,
        now=NOW,
        max_age=MAX_AGE,
    ) is FeedFreshness.FRESH


def test_current_time_requires_timezone():
    with pytest.raises(ValueError, match="Current time"):
        check_feed_freshness(
            NOW,
            now=NOW.replace(tzinfo=None),
            max_age=MAX_AGE,
        )


def test_retrieval_time_requires_timezone():
    with pytest.raises(ValueError, match="Feed retrieval time"):
        check_feed_freshness(
            NOW.replace(tzinfo=None),
            now=NOW,
            max_age=MAX_AGE,
        )


@pytest.mark.parametrize(
    "max_age",
    [timedelta(0), timedelta(seconds=-1)],
)
def test_rejects_nonpositive_maximum_age(max_age):
    with pytest.raises(ValueError, match="must be positive"):
        check_feed_freshness(
            NOW,
            now=NOW,
            max_age=max_age,
        )