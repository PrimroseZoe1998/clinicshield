from datetime import datetime, timedelta

from clinicshield.feed_freshness import (
    FeedFreshness,
    check_feed_freshness,
)
from clinicshield.rule_handlers import RuleObservation
from clinicshield.schemas import Asset
from clinicshield.segmentation_evidence import MedicalSeparationEvidence


def medical_network_separation(
    asset: Asset,
    evidence: MedicalSeparationEvidence | None,
    *,
    now: datetime,
    max_age: timedelta,
) -> RuleObservation | None:
    """Assess explicit medical-device separation evidence."""
    check_feed_freshness(None, now=now, max_age=max_age)

    if asset.asset_type != "medical_device":
        return None

    if evidence is not None and evidence.asset_id != asset.asset_id:
        raise ValueError("Separation evidence must match the asset.")

    fresh = (
        evidence is not None
        and check_feed_freshness(
            evidence.observed_at,
            now=now,
            max_age=max_age,
        ) is FeedFreshness.FRESH
    )

    if (
        fresh
        and evidence is not None
        and evidence.separation_verified == "Yes"
    ):
        return None

    confirmed = (
        fresh
        and evidence is not None
        and evidence.separation_verified == "No"
    )

    if evidence is None:
        basis = "Medical-device network separation has not been verified."
    elif not fresh:
        basis = (
            "Observation freshness requires review. "
            + evidence.evidence_basis
        )
    else:
        basis = evidence.evidence_basis

    return RuleObservation(
        rule_id="R11",
        entity_id=asset.asset_id,
        status="confirmed" if confirmed else "needs_review",
        evidence=(
            ("asset_id", asset.asset_id),
            ("asset_type", asset.asset_type),
            ("network_segment", asset.network_segment),
            (
                "separation_verified",
                evidence.separation_verified
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