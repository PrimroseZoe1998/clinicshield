from copy import deepcopy
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path

import pytest

from clinicshield.assessment_evidence import (
    AssessmentEvidence,
    AssessmentFreshnessPolicy,
)
from clinicshield.assessment_input import read_assessment
from clinicshield.assessment_scoring import score_assessment
from clinicshield.kev_cache import KevSnapshot
from clinicshield.schemas import Software
from clinicshield.scoring import score_safeguards
from clinicshield.vulnerability_evidence import VulnerabilityEvidence


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)


def load_sample(clinic="lakeview_dental"):
    folder = ROOT / "samples" / clinic
    services = folder / "services.csv"
    return read_assessment(
        checklist_json=(folder / "checklist.json").read_bytes(),
        followups_json=(folder / "followups.json").read_bytes(),
        assets_csv=(folder / "assets.csv").read_bytes(),
        software_csv=(folder / "software.csv").read_bytes(),
        services_csv=services.read_bytes() if services.exists() else None,
    )


def score(assessment, evidence=None):
    return score_assessment(
        assessment,
        evidence if evidence is not None else AssessmentEvidence(),
        AssessmentFreshnessPolicy(
            administrator_observation_max_age=timedelta(days=30)
        ),
        rules_directory=ROOT / "rules",
        now=NOW,
    )


def make_vulnerability_evidence(software):
    return AssessmentEvidence(
        vulnerabilities={
            "software:1": (
                VulnerabilityEvidence(
                    software_entry_id="software:1",
                    record={
                        "vulnerability_id": "CVE-2026-12345",
                        "source": "Synthetic vulnerability fixture",
                        "source_url": "https://example.org/advisory",
                        "retrieved_at": NOW,
                        "vendor": software.vendor,
                        "product": software.product,
                        "version_rule": "exact",
                        "affected_versions": ["1.2.3"],
                    },
                    record_status="active",
                    source_generated_at=NOW,
                ),
            ),
        },
        kev_snapshot=KevSnapshot(
            retrieved_at=NOW,
            catalog={
                "catalogVersion": "synthetic-test-catalog",
                "dateReleased": NOW,
                "count": 1,
                "vulnerabilities": [
                    {
                        "cveID": "CVE-2026-12345",
                        "vendorProject": software.vendor,
                        "product": software.product,
                        "vulnerabilityName": "Fictional vulnerability",
                        "dateAdded": "2026-10-28",
                        "shortDescription": "Synthetic test entry.",
                        "requiredAction": "Follow fictional vendor guidance.",
                        "dueDate": "2026-11-18",
                    }
                ],
            },
        ),
    )


@pytest.mark.parametrize(
    "clinic",
    ["lakeview_dental", "southside_counseling", "westside_health"],
)
def test_sample_assessment_scores_use_existing_formula(clinic):
    assessment = load_sample(clinic)
    result = score(assessment)

    assert result.safeguards == score_safeguards(assessment.checklist)
    assert result.combined.raw_score == (
        Fraction(3, 5) * result.safeguards.score
        + Fraction(2, 5) * result.grouped_scoring.exposure.score
    )
    assert 0 <= result.combined.final_score <= 100
    assert result.is_provisional
    assert result.score_limitations


def test_missing_service_coverage_is_not_hidden_by_score():
    result = score(load_sample("southside_counseling"))

    assert result.is_provisional
    assert any(
        issue.topic == "services"
        for issue in result.evaluation.coverage_issues
    )
    assert "Some source or inventory coverage is unassessed." in (
        result.score_limitations
    )


def test_unknown_findings_do_not_create_critical_ceiling():
    result = score(load_sample())

    assert result.grouped_scoring.review_groups
    assert all(
        group.severity == "Info"
        for group in result.groups
        if not group.has_confirmed_gap
    )
    assert result.combined.critical_ceiling is None
    assert result.combined.critical_findings == ()


def test_confirmed_kev_vulnerability_reaches_overall_ceiling():
    assessment = load_sample()
    data = assessment.inventory.software[0].model_dump()
    data["version"] = "1.2.3"
    software = Software.model_validate(data)
    assessment.inventory.software[0] = software

    result = score(
        assessment, make_vulnerability_evidence(software)
    )

    assert result.combined.critical_ceiling == 69
    assert result.combined.final_score <= 69
    assert result.combined.critical_findings


def test_unknown_version_cannot_create_critical_ceiling():
    assessment = load_sample()
    software = assessment.inventory.software[0]

    result = score(
        assessment, make_vulnerability_evidence(software)
    )

    assert result.combined.critical_ceiling is None
    assert any(
        item.finding.rule.rule_id == "R01"
        and item.finding.observation.status == "needs_review"
        for item in result.evaluation.findings
    )


def test_inventory_checklist_conflict_is_explicit_without_answer_override():
    assessment = load_sample()
    assessment.checklist.answers["Q01"] = "Yes"

    result = score(assessment)

    assert any(
        conflict.rule_id == "R12"
        and conflict.question_id == "Q01"
        for conflict in result.checklist_conflicts
    )
    assert assessment.checklist.answers["Q01"] == "Yes"
    assert result.safeguards == score_safeguards(assessment.checklist)
    assert any(
        "disagree with checklist" in limitation
        for limitation in result.score_limitations
    )


def test_unknown_mfa_does_not_become_confirmed_checklist_conflict():
    assessment = load_sample()
    assessment.checklist.answers["Q01"] = "Yes"
    for index, software in enumerate(assessment.inventory.software):
        if software.purpose == "email":
            data = software.model_dump()
            data["mfa_enabled"] = "Unknown"
            assessment.inventory.software[index] = Software.model_validate(data)

    result = score(assessment)

    assert not any(
        conflict.rule_id == "R12"
        for conflict in result.checklist_conflicts
    )


def test_duplicate_software_evidence_does_not_change_component_scores():
    assessment = load_sample()
    original = score(assessment)
    assessment.inventory.software.append(
        assessment.inventory.software[0].model_copy()
    )

    duplicated = score(assessment)

    assert duplicated.safeguards == original.safeguards
    assert duplicated.grouped_scoring.exposure == (
        original.grouped_scoring.exposure
    )
    assert duplicated.combined == original.combined


def test_scoring_does_not_modify_assessment():
    assessment = load_sample()
    original = deepcopy(assessment)

    score(assessment)

    assert assessment == original