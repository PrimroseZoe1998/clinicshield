import json
from dataclasses import dataclass

from clinicshield.finding_groups import FindingGroup
from clinicshield.input_limits import InputError
from clinicshield.inventory import ScoringEntity
from clinicshield.scoring import (
    EvaluatedFinding,
    ExposureScore,
    evaluate_technical_finding,
    score_exposure,
)


@dataclass(frozen=True)
class GroupedScoringResult:
    exposure: ExposureScore
    technical_findings: tuple[EvaluatedFinding, ...]
    administrative_groups: tuple[FindingGroup, ...]
    review_groups: tuple[FindingGroup, ...]
    critical_findings: tuple[str, ...]


def score_finding_groups(
    entities: tuple[ScoringEntity, ...],
    groups: tuple[FindingGroup, ...],
) -> GroupedScoringResult:
    """Score each confirmed technical risk group once."""
    entity_map = {entity.entity_id: entity for entity in entities}

    if len(entity_map) != len(entities):
        raise InputError("Scoring entity IDs must be unique.")

    seen = set()
    technical = []
    administrative = []
    review = []
    critical = []

    for group in groups:
        key = (group.scoring_entity_id, group.issue_key)

        if key in seen:
            raise InputError("Duplicate finding groups must be resolved first.")
        seen.add(key)

        if not group.occurrences or any(
            item.scoring_entity_id != group.scoring_entity_id
            or item.issue_key != group.issue_key
            or item.scoring_category != group.scoring_category
            for item in group.occurrences
        ):
            raise InputError("Finding group identity is inconsistent.")

        if group.scoring_category not in {
            "technical", "administrative"
        }:
            raise InputError("Choose a supported scoring category.")

        if (
            group.scoring_category == "technical"
            and group.scoring_entity_id not in entity_map
        ):
            raise InputError("Technical group references an unknown entity.")

        if group.scoring_category == "administrative":
            administrative.append(group)

        if any(
            item.finding.observation.status == "needs_review"
            for item in group.occurrences
        ):
            review.append(group)

        if not group.has_confirmed_gap:
            continue

        if group.severity == "Critical":
            critical.append(json.dumps(
                [group.scoring_entity_id, group.issue_key],
                separators=(",", ":"),
            ))

        if group.scoring_category == "technical":
            technical.append(evaluate_technical_finding(
                entity_map[group.scoring_entity_id],
                group.issue_key,
                group.severity,
            ))

    exposure = score_exposure(
        [entity.entity_id for entity in entities],
        [item.finding for item in technical],
    )

    return GroupedScoringResult(
        exposure=exposure,
        technical_findings=tuple(technical),
        administrative_groups=tuple(administrative),
        review_groups=tuple(review),
        critical_findings=tuple(sorted(critical)),
    )