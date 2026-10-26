from enum import Enum

from clinicshield.normalization import (
    NormalizedSoftware,
    normalize_name,
    normalize_version,
)
from clinicshield.feed_models import VulnerabilityRecord

class MatchStatus(str, Enum):
    MATCH = "match"
    NO_MATCH = "no_match"
    NEEDS_REVIEW = "needs_review"


def match_exact_versions(
    software: NormalizedSoftware,
    *,
    vendor: str,
    product: str,
    affected_versions: tuple[str, ...],
) -> MatchStatus:
    """Match a complete list of exact affected versions.

    Do not pass version ranges or wildcard expressions.
    NO_MATCH applies only to this record, not overall safety.
    """
    if (
        software.vendor != normalize_name(vendor)
        or software.product != normalize_name(product)
    ):
        return MatchStatus.NO_MATCH

    if software.version is None or not affected_versions:
        return MatchStatus.NEEDS_REVIEW

    versions = tuple(
        normalize_version(value) for value in affected_versions
    )

    if software.version in versions:
        return MatchStatus.MATCH

    if None in versions:
        return MatchStatus.NEEDS_REVIEW

    return MatchStatus.NO_MATCH

def match_feed_record(
    software: NormalizedSoftware,
    record: VulnerabilityRecord,
) -> MatchStatus:
    """Match one feed record without interpreting unsupported rules."""
    if (
        software.vendor != record.vendor
        or software.product != record.product
    ):
        return MatchStatus.NO_MATCH

    if record.version_rule == "unsupported":
        return MatchStatus.NEEDS_REVIEW

    return match_exact_versions(
        software,
        vendor=record.vendor,
        product=record.product,
        affected_versions=record.affected_versions,
    )