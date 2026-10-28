from datetime import datetime, timezone
from typing import Literal

from clinicshield.eol_cache import EolSnapshot
from clinicshield.lifecycle_evidence import LifecycleEvidence
from clinicshield.lifecycle_mapping import OsReleaseMapping
from clinicshield.normalization import normalize_name, normalize_version
from clinicshield.schemas import Asset


def lifecycle_evidence_from_cache(
    asset: Asset,
    mapping: OsReleaseMapping | None,
    snapshot: EolSnapshot | None,
    *,
    now: datetime,
    extended_support: Literal[
        "not_applicable", "confirmed_absent", "active", "unknown"
    ] = "unknown",
    coverage_basis: str = "Extended-support coverage has not been verified.",
) -> LifecycleEvidence | None:
    """Adapt one explicitly mapped cached release into OS evidence."""
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Current time must include a timezone.")

    if not isinstance(coverage_basis, str) or not coverage_basis.strip():
        raise ValueError("Provide an extended-support evidence basis.")

    if mapping is None or snapshot is None:
        return None

    if (
        normalize_name(asset.os_name) != normalize_name(mapping.os_name)
        or normalize_version(asset.os_version) is None
        or normalize_version(asset.os_version)
        != normalize_version(mapping.os_version)
        or snapshot.product != mapping.product
    ):
        return None

    release = next(
        (
            item
            for item in snapshot.response.result.releases
            if item.name == mapping.release_name
        ),
        None,
    )

    if release is None:
        return None

    today = now.astimezone(timezone.utc).date()
    status: Literal["supported", "unsupported", "unknown"] = "unknown"

    if release.isEol is True:
        if release.eolFrom is None or release.eolFrom <= today:
            status = "unsupported"
    elif release.isEol is False and release.isMaintained is True:
        if release.eolFrom is None or release.eolFrom > today:
            status = "supported"

    return LifecycleEvidence(
        os_name=asset.os_name,
        os_version=asset.os_version,
        support_status=status,
        support_basis=(
            f"Product {mapping.product}; release {mapping.release_name}; "
            f"isEol={release.isEol}; eolFrom={release.eolFrom}; "
            f"isMaintained={release.isMaintained}. "
            f"Mapping: {mapping.mapping_basis} "
            f"Coverage: {coverage_basis.strip()}"
        ),
        extended_support=extended_support,
        source_url=snapshot.source_url,
        retrieved_at=snapshot.retrieved_at,
        source_generated_at=snapshot.response.generated_at,
    )