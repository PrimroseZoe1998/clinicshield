import json
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
from clinicshield.epss_cache import EpssSnapshot
from clinicshield.kev_cache import KevSnapshot
from clinicshield.schemas import Software
from clinicshield.vulnerability_evidence import VulnerabilityEvidence


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)
CVE = "CVE-2026-12345"


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


def vulnerability_result(*, epss_score="0.75", epss_age=0, known_version=True):
    assessment = load_sample()
    software = assessment.inventory.software[0]
    if known_version:
        data = software.model_dump()
        data["version"] = "1.2.3"
        software = Software.model_validate(data)
        assessment.inventory.software[0] = software

    score_date = (NOW - timedelta(days=epss_age)).date()
    snapshot = None
    if epss_score is not None:
        snapshot = EpssSnapshot(
            retrieved_at=NOW,
            model_version="synthetic-test-model",
            score_date=score_date,
            records=(
                {
                    "cve": CVE,
                    "epss": epss_score,
                    "percentile": "0.95",
                    "score_date": score_date,
                },
            ),
        )

    evidence = AssessmentEvidence(
        vulnerabilities={
            "software:1": (
                VulnerabilityEvidence(
                    software_entry_id="software:1",
                    record={
                        "vulnerability_id": CVE,
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
                "catalogVersion": "synthetic-empty-catalog",
                "dateReleased": NOW,
                "count": 0,
                "vulnerabilities": [],
            },
        ),
        epss_snapshot=snapshot,
    )
    return score(assessment, evidence)


def r02_report(report):
    return next(
        finding for finding in report["findings"]
        if "R02" in finding["rule_ids"]
    )


@pytest.mark.parametrize(
    "clinic",
    ["lakeview_dental", "southside_counseling", "westside_health"],
)
def test_report_is_json_serializable_and_matches_scores(clinic):
    result = score(load_sample(clinic))

    report = build_assessment_report(result)
    restored = json.loads(json.dumps(report, allow_nan=False))

    assert restored["score"]["final"] == result.combined.final_score
    assert restored["score"]["band"] == result.combined.band
    assert restored["score"]["status"] == "provisional"
    assert restored["evaluated_at"] == NOW.isoformat()
    assert len(restored["findings"]) == len(result.groups)


def test_missing_coverage_is_included():
    report = build_assessment_report(
        score(load_sample("southside_counseling"))
    )

    topics = {issue["topic"] for issue in report["coverage_issues"]}
    assert {"services", "KEV", "EPSS", "vulnerability_applicability"} <= topics
    assert report["score"]["limitations"]


def test_unresolved_findings_are_info_with_zero_exposure_points():
    report = build_assessment_report(score(load_sample()))
    unresolved = [
        finding for finding in report["findings"]
        if finding["status"] == "needs_review"
    ]

    assert unresolved
    assert all(
        finding["severity"] == "Info"
        and finding["exposure_points"] == 0
        for finding in unresolved
    )


def test_recommendations_and_source_checked_reference_scopes_remain_visible():
    report = build_assessment_report(score(load_sample()))

    for finding in report["findings"]:
        assert finding["recommendations"]
        assert finding["owners"]
        assert finding["evidence"]
        assert finding["framework_references"]
        assert all(
            reference["review_status"] == "reviewed"
            and "Partial project mapping" in reference["rationale"]
            and reference["source"].startswith("https://")
            for reference in finding["framework_references"]
        )


def test_administrative_findings_add_no_exposure_points():
    report = build_assessment_report(score(load_sample()))
    administrative = [
        finding for finding in report["findings"]
        if finding["scoring_category"] == "administrative"
    ]

    assert administrative
    assert all(
        finding["exposure_points"] == 0
        for finding in administrative
    )


def test_freshness_policies_are_displayed_separately():
    report = build_assessment_report(score(load_sample()))

    assert report["freshness_policy"] == {
        "public_feed_max_age_seconds": 8 * 24 * 60 * 60,
        "administrator_observation_max_age_seconds": 30 * 24 * 60 * 60,
    }


def test_checklist_conflicts_are_retained():
    assessment = load_sample()
    assessment.checklist.answers["Q01"] = "Yes"

    report = build_assessment_report(score(assessment))

    assert any(
        conflict["rule_id"] == "R12"
        and conflict["question_id"] == "Q01"
        for conflict in report["checklist_conflicts"]
    )


def test_current_epss_includes_score_date_source_and_model():
    report = build_assessment_report(vulnerability_result())
    finding = r02_report(report)
    context = finding["epss_context"][0]

    assert finding["severity"] == "High"
    assert context["status"] == "available"
    assert context["cve"] == CVE
    assert context["current_score"] == "0.75"
    assert context["priority_score"] == "0.75"
    assert context["score_date"] == NOW.date().isoformat()
    assert context["model_version"] == "synthetic-test-model"
    assert context["source_url"]


def test_valid_zero_epss_is_not_reported_as_missing():
    report = build_assessment_report(
        vulnerability_result(epss_score="0")
    )
    context = r02_report(report)["epss_context"][0]

    assert context["status"] == "available"
    assert context["current_score"] == "0"
    assert context["priority_score"] == "0"


@pytest.mark.parametrize(
    "options",
    [
        {"epss_score": None},
        {"epss_age": 9},
    ],
)
def test_unavailable_or_stale_epss_does_not_appear_as_current(options):
    report = build_assessment_report(vulnerability_result(**options))
    finding = r02_report(report)
    context = finding["epss_context"][0]

    assert finding["severity"] == "High"
    assert context["status"] == "unknown"
    assert context["current_score"] is None
    assert context["priority_score"] is None
    assert context["review_reasons"]


def test_high_epss_does_not_confirm_unknown_version():
    report = build_assessment_report(
        vulnerability_result(epss_score="1", known_version=False)
    )
    finding = r02_report(report)

    assert finding["status"] == "needs_review"
    assert finding["severity"] == "Info"
    assert finding["epss_context"][0]["priority_score"] is None


def test_building_report_does_not_change_scored_result():
    result = score(load_sample())
    original = [
        (
            linked.finding.rule.model_dump(),
            linked.finding.observation,
        )
        for linked in result.evaluation.findings
    ]

    build_assessment_report(result)

    assert [
        (
            linked.finding.rule.model_dump(),
            linked.finding.observation,
        )
        for linked in result.evaluation.findings
    ] == original