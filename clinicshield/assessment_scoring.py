from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from clinicshield.assessment_evidence import (
    AssessmentEvidence,
    AssessmentFreshnessPolicy,
)
from clinicshield.assessment_grouping import group_assessment_findings
from clinicshield.assessment_input import AssessmentInput
from clinicshield.assessment_runner import (
    AssessmentEvaluation,
    evaluate_assessment,
)
from clinicshield.finding_groups import FindingGroup
from clinicshield.grouped_scoring import (
    GroupedScoringResult,
    score_finding_groups,
)
from clinicshield.scoring import (
    CombinedScore,
    SafeguardsScore,
    combine_scores,
    score_safeguards,
)


CHECKLIST_LINKS = {
    "R03": "Q18",
    "R05": "Q05",
    "R08": "Q18",
    "R10": "Q16",
    "R11": "Q23",
    "R12": "Q01",
    "R13": "Q07",
    "R17": "Q12",
}


@dataclass(frozen=True)
class ChecklistConflict:
    rule_id: str
    source_entry_id: str
    question_id: str


@dataclass(frozen=True)
class ScoredAssessment:
    evaluation: AssessmentEvaluation
    groups: tuple[FindingGroup, ...]
    grouped_scoring: GroupedScoringResult
    safeguards: SafeguardsScore
    combined: CombinedScore
    checklist_conflicts: tuple[ChecklistConflict, ...]
    score_limitations: tuple[str, ...]

    @property
    def is_provisional(self) -> bool:
        return bool(self.score_limitations)


def score_assessment(
    assessment: AssessmentInput,
    evidence: AssessmentEvidence,
    policy: AssessmentFreshnessPolicy,
    *,
    rules_directory: Path,
    now: datetime,
) -> ScoredAssessment:
    """Score assessed evidence while retaining scope and uncertainty."""
    evaluation = evaluate_assessment(
        assessment,
        evidence,
        policy,
        rules_directory=rules_directory,
        now=now,
    )
    groups = group_assessment_findings(evaluation)
    grouped = score_finding_groups(
        evaluation.scoring_inventory.entities,
        groups,
    )
    safeguards = score_safeguards(assessment.checklist)
    combined = combine_scores(
        safeguards,
        grouped.exposure,
        open_critical_findings=grouped.critical_findings,
    )

    conflicts = set()
    for linked in evaluation.findings:
        finding = linked.finding
        question = CHECKLIST_LINKS.get(finding.rule.rule_id)

        if (
            question is not None
            and finding.observation.status == "confirmed"
            and assessment.checklist.answers.get(question) == "Yes"
        ):
            conflicts.add((
                finding.rule.rule_id,
                linked.source_entry_id,
                question,
            ))

    limitations = []

    if evaluation.coverage_issues:
        limitations.append("Some source or inventory coverage is unassessed.")
    if grouped.review_groups:
        limitations.append("Some findings require verification.")
    if any(item.unknown_conditions for item in grouped.technical_findings):
        limitations.append("Some technical scoring conditions are unknown.")
    if any(
        linked.finding.rule.review_status != "reviewed"
        for linked in evaluation.findings
    ):
        limitations.append("Some applied rule definitions remain drafts.")
    if conflicts:
        limitations.append(
            "Explicit findings disagree with checklist answers. "
            "Safeguards uses the submitted answers pending review."
        )

    return ScoredAssessment(
        evaluation=evaluation,
        groups=groups,
        grouped_scoring=grouped,
        safeguards=safeguards,
        combined=combined,
        checklist_conflicts=tuple(
            ChecklistConflict(*values)
            for values in sorted(conflicts)
        ),
        score_limitations=tuple(limitations),
    )