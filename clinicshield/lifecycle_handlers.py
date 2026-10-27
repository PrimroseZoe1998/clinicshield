from datetime import datetime, timedelta

from clinicshield.feed_freshness import (
    FeedFreshness,
    check_feed_freshness,
)
from clinicshield.lifecycle_evidence import LifecycleEvidence
from clinicshield.normalization import normalize_name, normalize_version
from clinicshield.rule_handlers import RuleObservation
from clinicshield.schemas import Asset


def operating_system_support(
    asset: Asset,
    evidence: LifecycleEvidence | None,
    *,
    now: datetime,
    max_age: timedelta,
) -> RuleObservation | None:
    """Confirm unsupported status only from matched, current evidence."""
    check_feed_freshness(None, now=now, max_age=max_age)
    reasons = []

    if evidence is None:
        reasons.append("Lifecycle evidence is missing.")
    else:
        asset_version = normalize_version(asset.os_version)
        evidence_version = normalize_version(evidence.os_version)

        if (
            normalize_version(asset.os_name) is None
            or normalize_name(asset.os_name)
            != normalize_name(evidence.os_name)
            or asset_version is None
            or evidence_version is None
            or asset_version != evidence_version
        ):
            reasons.append("OS identity or release is unresolved.")

        if evidence.source_url is None:
            reasons.append("Source URL is missing.")

        for label, timestamp in (
            ("retrieval", evidence.retrieved_at),
            ("source generation", evidence.source_generated_at),
        ):
            freshness = check_feed_freshness(
                timestamp, now=now, max_age=max_age
            )
            if freshness is not FeedFreshness.FRESH:
                reasons.append(f"Unresolved {label} freshness.")

        if (
            evidence.retrieved_at is not None
            and evidence.source_generated_at is not None
            and evidence.source_generated_at > evidence.retrieved_at
        ):
            reasons.append("Source generation is after retrieval.")

        if evidence.support_status == "unknown":
            reasons.append("Source support status is unknown.")

        if (
            evidence.support_status == "unsupported"
            and evidence.extended_support
            not in {"not_applicable", "confirmed_absent"}
        ):
            reasons.append("Extended-support coverage requires review.")

        if not reasons and evidence.support_status == "supported":
            return None

    confirmed = (
        evidence is not None
        and not reasons
        and evidence.support_status == "unsupported"
    )

    return RuleObservation(
        rule_id="R03",
        entity_id=asset.asset_id,
        status="confirmed" if confirmed else "needs_review",
        evidence=(
            ("asset_id", asset.asset_id),
            ("os_name", asset.os_name),
            ("os_version", asset.os_version),
            ("support_status", "unsupported" if confirmed else "unknown"),
            (
                "support_basis",
                evidence.support_basis if confirmed else " ".join(reasons),
            ),
            (
                "source_url",
                str(evidence.source_url)
                if evidence is not None and evidence.source_url is not None
                else "",
            ),
            (
                "retrieved_at",
                evidence.retrieved_at.isoformat()
                if evidence is not None and evidence.retrieved_at is not None
                else "",
            ),
            (
                "source_generated_at",
                evidence.source_generated_at.isoformat()
                if evidence is not None
                and evidence.source_generated_at is not None
                else "",
            ),
            (
                "extended_support",
                evidence.extended_support if evidence is not None else "unknown",
            ),
        ),
    )