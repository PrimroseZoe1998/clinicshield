import json

from clinicshield.assessment_runner import AssessmentEvaluation
from clinicshield.finding_groups import (
    FindingGroup,
    FindingOccurrence,
    group_findings,
)
from clinicshield.input_limits import InputError
from clinicshield.normalization import normalize_name


ADMINISTRATIVE_RULES = {
    "R07", "R12", "R13", "R14", "R15", "R16", "R17",
    "R18", "R19", "R20", "R21", "R22", "R23",
}


def group_assessment_findings(
    evaluation: AssessmentEvaluation,
) -> tuple[FindingGroup, ...]:
    """Apply explicit same-risk associations to assessment findings."""
    occurrences = []

    for linked in evaluation.findings:
        finding = linked.finding
        rule_id = finding.rule.rule_id
        entity_id = linked.scoring_entity_id

        if rule_id not in {f"R{number:02d}" for number in range(1, 25)}:
            raise InputError("Finding has no assessment grouping policy.")

        details = {}
        for key, value in finding.observation.evidence:
            if key in details:
                raise InputError("Finding contains duplicate evidence keys.")
            details[key] = value

        def require(name):
            value = details.get(name)
            if not isinstance(value, str) or not value.strip():
                raise InputError("Required grouping evidence is missing.")
            return value

        category = (
            "administrative"
            if rule_id in ADMINISTRATIVE_RULES
            else "technical"
        )

        if rule_id in {"R01", "R02"}:
            parts = [
                "vulnerability",
                require("vulnerability_id"),
                normalize_name(require("vendor")),
                normalize_name(require("product")),
            ]
            basis = "Same CVE and software product on the same scoring entity."

        elif rule_id in {"R03", "R08"}:
            parts = ["os-support"]
            basis = (
                "Same asset OS-support risk; retain SMB context "
                "without adding the same support penalty again."
            )

        elif rule_id in {"R04", "R12", "R13", "R17", "R24"}:
            parts = [
                rule_id,
                normalize_name(require("vendor")),
                normalize_name(require("product")),
            ]
            basis = (
                "Same rule and software product on the same scoring entity."
            )

        elif rule_id in {"R06", "R09"}:
            parts = [
                rule_id,
                details.get("host", "").strip().casefold(),
                require("protocol"),
                require("port"),
                require("service"),
            ]
            basis = (
                "Same rule and reported service endpoint; "
                "other service risks remain separate."
            )

        elif rule_id == "R07":
            entity_id = "assessment"
            parts = ["remote-access-safeguards", "Q17"]
            basis = (
                "One organization-level Q17 safeguard gap; "
                "retain all associated service contexts."
            )

        else:
            parts = [rule_id]
            basis = (
                "Same rule and scoring entity; preserve each evidence source."
            )

        occurrences.append(FindingOccurrence(
            finding=finding,
            scoring_entity_id=entity_id,
            issue_key=json.dumps(parts, separators=(",", ":")),
            scoring_category=category,
            grouping_basis=basis,
        ))

    return group_findings(tuple(occurrences))