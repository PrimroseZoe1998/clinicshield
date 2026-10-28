from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from clinicshield.assessment_evidence import AssessmentFreshnessPolicy
from clinicshield.assessment_input import read_assessment
from clinicshield.assessment_scoring import score_assessment
from clinicshield.input_limits import InputError
from clinicshield.sample_evidence import build_sample_evidence


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)


def load_sample(clinic):
    folder = ROOT / "samples" / clinic
    services = folder / "services.csv"
    return read_assessment(
        checklist_json=(folder / "checklist.json").read_bytes(),
        followups_json=(folder / "followups.json").read_bytes(),
        assets_csv=(folder / "assets.csv").read_bytes(),
        software_csv=(folder / "software.csv").read_bytes(),
        services_csv=services.read_bytes() if services.exists() else None,
    )


@pytest.mark.parametrize(
    "clinic,expected_assets",
    [
        ("lakeview_dental", {"LV-WS01", "LV-WS02", "LV-SRV01"}),
        ("southside_counseling", set()),
        ("westside_health", {"WH-MD02", "WH-LT01"}),
    ],
)
def test_explicit_scenario_os_evidence(clinic, expected_assets):
    assessment = load_sample(clinic)

    evidence = build_sample_evidence(clinic, assessment, now=NOW)

    assert set(evidence.os_support) == expected_assets
    assert all(
        record.support_status == "unsupported"
        and record.extended_support == "confirmed_absent"
        and "Fictional scenario" in record.support_basis
        for record in evidence.os_support.values()
    )
    assert not evidence.vulnerabilities
    assert evidence.kev_snapshot is None
    assert evidence.epss_snapshot is None


def test_lakeview_router_evidence_is_explicitly_fictional():
    evidence = build_sample_evidence(
        "lakeview_dental",
        load_sample("lakeview_dental"),
        now=NOW,
    )
    router = evidence.default_passwords["LV-RT01"]

    assert router.default_password_changed == "No"
    assert "Fictional Lakeview" in router.evidence_basis
    assert "not an administrator observation" in router.evidence_source


def test_westside_separation_evidence_is_explicitly_fictional():
    evidence = build_sample_evidence(
        "westside_health",
        load_sample("westside_health"),
        now=NOW,
    )
    separation = evidence.medical_separation["WH-MD02"]

    assert separation.separation_verified == "No"
    assert "Fictional Westside" in separation.evidence_basis
    assert "not a network verification" in separation.evidence_source


@pytest.mark.parametrize(
    "clinic,expected_score,expected_band",
    [
        ("lakeview_dental", 65, "At risk"),
        ("southside_counseling", 82, "Needs attention"),
        ("westside_health", 80, "Needs attention"),
    ],
)
def test_current_scenario_scoring_baseline(
    clinic, expected_score, expected_band
):
    assessment = load_sample(clinic)
    evidence = build_sample_evidence(clinic, assessment, now=NOW)

    result = score_assessment(
        assessment,
        evidence,
        AssessmentFreshnessPolicy(
            administrator_observation_max_age=timedelta(days=30)
        ),
        rules_directory=ROOT / "rules",
        now=NOW,
    )

    # Measured current behavior, not final approved calibration targets.
    assert result.combined.final_score == expected_score
    assert result.combined.band == expected_band
    assert result.combined.critical_ceiling is None
    assert result.is_provisional
    assert not any(
        item.finding.rule.rule_id in {"R01", "R02"}
        for item in result.evaluation.findings
    )


def test_rejects_unknown_scenario():
    with pytest.raises(InputError, match="fictional clinic"):
        build_sample_evidence(
            "unknown",
            load_sample("lakeview_dental"),
            now=NOW,
        )


def test_rejects_changed_os_identity():
    assessment = load_sample("lakeview_dental")
    assessment.inventory.assets[0].os_version = "different release"

    with pytest.raises(InputError, match="OS identity"):
        build_sample_evidence(
            "lakeview_dental", assessment, now=NOW
        )


def test_rejects_clock_without_timezone():
    with pytest.raises(ValueError, match="timezone"):
        build_sample_evidence(
            "lakeview_dental",
            load_sample("lakeview_dental"),
            now=NOW.replace(tzinfo=None),
        )


def test_does_not_modify_assessment():
    assessment = load_sample("lakeview_dental")
    original = deepcopy(assessment)

    build_sample_evidence(
        "lakeview_dental", assessment, now=NOW
    )

    assert assessment == original