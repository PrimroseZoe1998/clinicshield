from datetime import datetime, timedelta

from clinicshield.application_evidence import ApplicationSupportEvidence
from clinicshield.feed_freshness import (
    FeedFreshness,
    check_feed_freshness,
)
from clinicshield.input_limits import InputError
from clinicshield.normalization import normalize_name, normalize_version
from clinicshield.rule_handlers import RuleObservation
from clinicshield.schemas import Software


def application_support(
    software: Software,
    evidence: ApplicationSupportEvidence | None,
    *,
    entity_id: str,
    now: datetime,
    max_age: timedelta,
) -> RuleObservation | None:
    """Assess application support using matched, current evidence."""
    check_feed_freshness(None, now=now, max_age=max_age)

    if not isinstance(entity_id, str) or not entity_id.strip():
        raise InputError("R04 requires a software entry identifier.")

    if evidence is not None and evidence.software_entry_id != entity_id:
        raise ValueError("Application evidence must match the software entry.")

    reasons = []

    if evidence is None:
        reasons.append("Application support evidence is missing.")
    else:
        for field in ("vendor", "product"):
            actual = getattr(software, field)
            expected = getattr(evidence, field)
            if (
                normalize_version(actual) is None
                or normalize_version(expected) is None
                or normalize_name(actual) != normalize_name(expected)
            ):
                reasons.append(f"Application {field} is unresolved.")

        version = normalize_version(software.version)
        if (
            version is None
            or version != normalize_version(evidence.version)
            or software.deployment != evidence.deployment
        ):
            reasons.append("Release or deployment is unresolved.")

        if evidence.source_url is None:
            reasons.append("Source URL is missing.")

        for label, timestamp in (
            ("retrieval", evidence.retrieved_at),
            ("source generation", evidence.source_generated_at),
        ):
            if check_feed_freshness(
                timestamp, now=now, max_age=max_age
            ) is not FeedFreshness.FRESH:
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
        rule_id="R04",
        entity_id=entity_id,
        status="confirmed" if confirmed else "needs_review",
        evidence=(
            ("asset_id", software.asset_id),
            ("vendor", software.vendor),
            ("product", software.product),
            ("version", software.version),
            ("deployment", software.deployment),
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