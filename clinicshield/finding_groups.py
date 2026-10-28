from dataclasses import dataclass
from typing import Literal

from clinicshield.input_limits import InputError
from clinicshield.rule_engine import RuleFinding
from clinicshield.rule_models import Severity
from clinicshield.scoring import SEVERITY_POINTS


@dataclass(frozen=True)
class FindingOccurrence:
    finding: RuleFinding
    scoring_entity_id: str
    issue_key: str
    scoring_category: Literal["technical", "administrative"]
    grouping_basis: str


@dataclass(frozen=True)
class FindingGroup:
    scoring_entity_id: str
    issue_key: str
    scoring_category: Literal["technical", "administrative"]
    occurrences: tuple[FindingOccurrence, ...]

    @property
    def severity(self) -> Severity:
        confirmed = [
            item.finding.severity
            for item in self.occurrences
            if item.finding.observation.status == "confirmed"
        ]
        return max(
            confirmed,
            key=SEVERITY_POINTS.__getitem__,
            default="Info",
        )

    @property
    def has_confirmed_gap(self) -> bool:
        return any(
            item.finding.observation.status == "confirmed"
            for item in self.occurrences
        )


def group_findings(
    occurrences: tuple[FindingOccurrence, ...],
) -> tuple[FindingGroup, ...]:
    """Preserve evidence while grouping explicitly identified same risks."""
    groups = {}
    categories = {}

    for item in occurrences:
        for value in (
            item.scoring_entity_id,
            item.issue_key,
            item.grouping_basis,
        ):
            if not isinstance(value, str) or not value.strip():
                raise InputError("Finding grouping requires explicit identifiers and basis.")

        if item.scoring_category not in {"technical", "administrative"}:
            raise InputError("Choose a supported scoring category.")

        if (
            item.finding.rule.rule_id
            != item.finding.observation.rule_id
        ):
            raise InputError("Finding rule and observation IDs must match.")

        key = (item.scoring_entity_id, item.issue_key)

        if key in categories and categories[key] != item.scoring_category:
            raise InputError("The same issue has conflicting scoring categories.")

        categories[key] = item.scoring_category
        groups.setdefault(key, []).append(item)

    return tuple(
        FindingGroup(
            scoring_entity_id=entity_id,
            issue_key=issue_key,
            scoring_category=categories[(entity_id, issue_key)],
            occurrences=tuple(groups[(entity_id, issue_key)]),
        )
        for entity_id, issue_key in sorted(groups)
    )