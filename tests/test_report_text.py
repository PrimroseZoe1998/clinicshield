from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from clinicshield.assessment_evidence import (
    AssessmentEvidence,
    AssessmentFreshnessPolicy,
)
from clinicshield.assessment_input import read_assessment
from clinicshield.assessment_report import build_assessment_report
from clinicshield.assessment_scoring import score_assessment
from clinicshield.report_text import render_assessment_text


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)


def make_report(clinic="lakeview_dental"):
    folder = ROOT / "samples" / clinic
    services = folder / "services.csv"
    assessment = read_assessment(
        checklist_json=(folder / "checklist.json").read_bytes(),
        followups_json=(folder / "followups.json").read_bytes(),
        assets_csv=(folder / "assets.csv").read_bytes(),
        software_csv=(folder / "software.csv").read_bytes(),
        services_csv=services.read_bytes() if services.exists() else None,
    )
    result = score_assessment(
        assessment,
        AssessmentEvidence(),
        AssessmentFreshnessPolicy(
            administrator_observation_max_age=timedelta(days=30)
        ),
        rules_directory=ROOT / "rules",
        now=NOW,
    )
    return build_assessment_report(result)


@pytest.mark.parametrize(
    "clinic",
    ["lakeview_dental", "southside_counseling", "westside_health"],
)
def test_renders_sample_scores_and_sections(clinic):
    report = make_report(clinic)

    text = render_assessment_text(report)

    assert text.startswith("ClinicShield assessment")
    assert (
        f"Overall score: {report['score']['final']}/100"
        in text
    )
    assert report["score"]["band"] in text
    assert "Score status: provisional" in text
    assert "Findings from supplied evidence" in text
    assert "Items requiring verification" in text
    assert "60% Safeguards and 40% Exposure" in text


def test_displays_missing_coverage_and_score_limits():
    text = render_assessment_text(
        make_report("southside_counseling")
    )

    assert "Coverage requiring attention" in text
    assert "No service inventory is available" in text
    assert "CVE coverage is unassessed" in text
    assert "does not establish safety" in text


def test_displays_separate_freshness_policies():
    text = render_assessment_text(make_report())

    assert "Public feeds: 8 days" in text
    assert "Administrator observations: 30 days" in text


def test_includes_recommendations_roles_effort_and_cost():
    text = render_assessment_text(make_report())

    assert "Recommended actions:" in text
    assert "Responsible roles:" in text
    assert "Estimated effort:" in text
    assert "Estimated cost:" in text


def test_pending_framework_mappings_are_not_labeled_reviewed():
    report = make_report()
    for finding in report["findings"]:
        for reference in finding["framework_references"]:
            reference["review_status"] = "pending"
    text = render_assessment_text(report)

    assert "Framework reference pending validation:" in text
    assert "Source-checked project mapping:" not in text


def test_source_checked_reference_preserves_scope_and_source():
    text = render_assessment_text(make_report())
    assert "Source-checked project mapping:" in text
    assert "Mapping scope: Partial project mapping" in text
    assert "Source: https://nvlpubs.nist.gov/" in text


def test_administrative_findings_explain_exposure_exclusion():
    text = render_assessment_text(make_report())

    assert "No additional Exposure deduction" in text
    assert "answers are scored once" in text


def test_unresolved_findings_explain_no_confirmed_risk_deduction():
    text = render_assessment_text(make_report())

    assert "No confirmed-risk Exposure deduction." in text
    assert "Severity: Info" in text


def test_checklist_conflicts_are_visible():
    report = make_report()
    report["checklist_conflicts"] = [
        {
            "rule_id": "R12",
            "source_entry_id": "software:2",
            "question_id": "Q01",
        }
    ]

    text = render_assessment_text(report)

    assert "Answers that need reconciliation" in text
    assert "disagrees with a Yes answer to Q01" in text


def test_valid_zero_epss_is_displayed_as_zero_percent():
    report = make_report()
    report["findings"][0]["epss_context"] = [
        {
            "status": "available",
            "current_score": "0",
            "score_date": "2026-10-28",
        }
    ]

    text = render_assessment_text(report)

    assert "EPSS 30-day exploitation probability: 0.00%" in text
    assert "as of 2026-10-28" in text
    assert "EPSS is prioritization context" in text


def test_unavailable_epss_does_not_become_zero_percent():
    report = make_report()
    report["findings"][0]["epss_context"] = [
        {
            "status": "unknown",
            "current_score": None,
            "score_date": "2026-10-19",
        }
    ]

    text = render_assessment_text(report)

    assert "Current EPSS score unavailable: unknown." in text
    assert "EPSS 30-day exploitation probability: 0.00%" not in text


def test_critical_ceiling_is_explained():
    report = make_report()
    report["score"]["critical_ceiling"] = 69
    report["score"]["final"] = min(report["score"]["final"], 69)

    text = render_assessment_text(report)

    assert "A confirmed Critical finding limits the overall score to 69." in text


def test_rendering_does_not_modify_report():
    report = make_report()
    original = deepcopy(report)

    render_assessment_text(report)

    assert report == original