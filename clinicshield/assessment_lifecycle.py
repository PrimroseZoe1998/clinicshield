from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints, TypeAdapter, ValidationError

from clinicshield.assessment_evidence import AssessmentEvidence
from clinicshield.assessment_input import AssessmentInput
from clinicshield.eol_cache_io import read_eol_cache
from clinicshield.feed_freshness import check_feed_freshness
from clinicshield.input_limits import InputError, MAX_JSON_BYTES, validate_upload
from clinicshield.lifecycle_adapter import lifecycle_evidence_from_cache
from clinicshield.lifecycle_mapping import OsReleaseMapping


class ReviewedLifecycleMapping(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    asset_id: Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1)]
    review_status: Literal["reviewed"]
    mapping: OsReleaseMapping


def read_lifecycle_mappings(data: bytes) -> tuple[ReviewedLifecycleMapping, ...]:
    validate_upload(data, max_bytes=MAX_JSON_BYTES)
    try:
        records = TypeAdapter(list[ReviewedLifecycleMapping]).validate_json(data)
    except ValidationError:
        raise InputError("Provide a valid reviewed lifecycle mapping JSON list.") from None
    if len({record.asset_id for record in records}) != len(records):
        raise InputError("Provide only one lifecycle mapping per asset.")
    return tuple(records)


def load_assessment_lifecycle(
    assessment: AssessmentInput,
    evidence: AssessmentEvidence,
    mappings: tuple[ReviewedLifecycleMapping, ...],
    directory: Path,
    *,
    now: datetime,
    max_age: timedelta,
) -> tuple[AssessmentEvidence, tuple[str, ...]]:
    """Load explicitly reviewed asset mappings; never infer support coverage."""
    check_feed_freshness(None, now=now, max_age=max_age)
    assets = {asset.asset_id: asset for asset in assessment.inventory.assets}
    if any(record.asset_id not in assets for record in mappings):
        raise InputError("Lifecycle mapping references an unknown asset.")
    if any(record.asset_id in evidence.os_support for record in mappings):
        raise InputError("Lifecycle mapping conflicts with existing OS evidence.")
    support = dict(evidence.os_support)
    messages = []
    snapshots = {}
    for record in mappings:
        product = record.mapping.product
        if product not in snapshots:
            try:
                snapshots[product] = read_eol_cache(directory / f"eol-{product}.json")
            except (ValueError, OSError):
                snapshots[product] = None
        snapshot = snapshots[product]
        adapted = lifecycle_evidence_from_cache(
            assets[record.asset_id], record.mapping, snapshot, now=now,
        )
        if adapted is None:
            messages.append(
                f"{record.asset_id}: lifecycle cache unavailable or exact mapping unmatched; "
                "OS support remains unassessed."
            )
            continue
        support[record.asset_id] = adapted
        retrieval = check_feed_freshness(snapshot.retrieved_at, now=now, max_age=max_age)
        source = check_feed_freshness(snapshot.response.generated_at, now=now, max_age=max_age)
        messages.append(
            f"{record.asset_id}: mapped lifecycle evidence; retrieval {retrieval.value}, "
            f"source {source.value}. Extended-support coverage remains unknown."
        )
    mapped = {record.asset_id for record in mappings}
    for asset_id in sorted(assets.keys() - mapped - support.keys()):
        messages.append(f"{asset_id}: no reviewed lifecycle mapping; OS support remains unassessed.")
    return replace(evidence, os_support=support), tuple(messages)
