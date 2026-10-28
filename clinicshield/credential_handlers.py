from datetime import datetime, timedelta

from clinicshield.credential_evidence import DefaultPasswordEvidence
from clinicshield.feed_freshness import (
    FeedFreshness,
    check_feed_freshness,
)
from clinicshield.rule_handlers import RuleObservation
from clinicshield.schemas import Asset


def default_admin_password(
    asset: Asset,
    evidence: DefaultPasswordEvidence | None,
    *,
    now: datetime,
    max_age: timedelta,
) -> RuleObservation | None:
    """Assess explicit setting evidence without handling passwords."""
    check_feed_freshness(None, now=now, max_age=max_age)

    if evidence is not None and evidence.asset_id != asset.asset_id:
        raise ValueError("Credential evidence must match the asset.")

    fresh = (
        evidence is not None
        and check_feed_freshness(
            evidence.observed_at,
            now=now,
            max_age=max_age,
        ) is FeedFreshness.FRESH
    )

    if fresh and evidence is not None:
        if evidence.applicability == "No":
            return None

        if (
            evidence.applicability == "Yes"
            and evidence.default_password_changed == "Yes"
        ):
            return None

    confirmed = (
        fresh
        and evidence is not None
        and evidence.applicability == "Yes"
        and evidence.default_password_changed == "No"
    )

    if evidence is None:
        basis = "Default-password applicability and status are unverified."
    elif not fresh:
        basis = (
            "Observation freshness requires review. "
            + evidence.evidence_basis
        )
    else:
        basis = evidence.evidence_basis

    return RuleObservation(
        rule_id="R10",
        entity_id=asset.asset_id,
        status="confirmed" if confirmed else "needs_review",
        evidence=(
            ("asset_id", asset.asset_id),
            (
                "applicability",
                evidence.applicability if evidence is not None else "Unknown",
            ),
            (
                "default_password_changed",
                evidence.default_password_changed
                if evidence is not None else "Unknown",
            ),
            ("evidence_basis", basis),
            (
                "evidence_source",
                evidence.evidence_source if evidence is not None else "",
            ),
            (
                "observed_at",
                evidence.observed_at.isoformat()
                if evidence is not None and evidence.observed_at is not None
                else "",
            ),
        ),
    )