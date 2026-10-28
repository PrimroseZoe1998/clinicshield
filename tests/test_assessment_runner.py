from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import requests

from clinicshield.assessment_evidence import (
    AssessmentEvidence,
    AssessmentFreshnessPolicy,
)
from clinicshield.assessment_input import read_assessment
from clinicshield.assessment_runner import evaluate_assessment
from clinicshield.credential_evidence import DefaultPasswordEvidence
from clinicshield.input_limits import InputError
from clinicshield.lifecycle_evidence import LifecycleEvidence


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


def run(assessment, evidence=None, *, observation_days=30):
    return evaluate_assessment(
        assessment,
        evidence if evidence is not None else AssessmentEvidence(),
        AssessmentFreshnessPolicy(
            administrator_observation_max_age=timedelta(
                days=observation_days
            ),
        ),
        rules_directory=ROOT / "rules",
        now=NOW,
    )


@pytest.mark.parametrize(
    "clinic,expected_confirmed_rules",
    [
        (
            "lakeview_dental",
            {"R05", "R07", "R12", "R16", "R18", "R19"},
        ),
        (
            "southside_counseling",
            {"R12", "R16", "R17", "R20", "R22"},
        ),
        (
            "westside_health",
            {"R09", "R14", "R16"},
        ),
    ],
)
def test_runs_all_rules_against_sample_inputs(
    clinic, expected_confirmed_rules
):
    result = run(load_sample(clinic))

    assert result.rules_loaded == 24
    assert result.evaluated_at == NOW
    assert {
        item.finding.rule.rule_id
        for item in result.findings
        if item.finding.observation.status == "confirmed"
    } == expected_confirmed_rules
    assert all(
        item.finding.severity == "Info"
        for item in result.findings
        if item.finding.observation.status == "needs_review"
    )


def test_missing_service_inventory_is_reported_as_unassessed():
    result = run(load_sample("southside_counseling"))

    assert any(
        issue.topic == "services"
        for issue in result.coverage_issues
    )
    assert not any(
        item.finding.rule.rule_id in {"R06", "R07", "R08", "R09"}
        for item in result.findings
    )


def test_missing_public_feeds_remain_explicit():
    result = run(load_sample("lakeview_dental"))
    topics = {issue.topic for issue in result.coverage_issues}

    assert {"KEV", "EPSS"} <= topics


def test_missing_applicability_does_not_invent_cve_findings():
    assessment = load_sample("lakeview_dental")
    result = run(assessment)

    assert not any(
        item.finding.rule.rule_id in {"R01", "R02"}
        for item in result.findings
    )
    assert sum(
        issue.topic == "vulnerability_applicability"
        for issue in result.coverage_issues
    ) == len(assessment.inventory.software)


def test_findings_retain_correct_scoring_entity_links():
    result = run(load_sample("lakeview_dental"))
    known_entities = {
        entity.entity_id for entity in result.scoring_inventory.entities
    }

    for item in result.findings:
        if item.source_entry_id == "checklist":
            assert item.scoring_entity_id == "assessment"
        else:
            assert item.scoring_entity_id in known_entities

        if item.source_entry_id.startswith("software:"):
            assert (
                item.finding.observation.entity_id
                == item.source_entry_id
            )


def test_administrator_age_is_separate_from_public_feed_age():
    old_time = NOW - timedelta(days=20)
    evidence = AssessmentEvidence(
        default_passwords={
            "LV-RT01": DefaultPasswordEvidence(
                asset_id="LV-RT01",
                applicability="Yes",
                default_password_changed="No",
                evidence_basis="Fictional administrator observation.",
                evidence_source="Synthetic test fixture",
                observed_at=old_time,
            ),
        },
        os_support={
            "LV-WS01": LifecycleEvidence(
                os_name="Windows",
                os_version="10 22H2",
                support_status="unsupported",
                support_basis="Fictional public lifecycle snapshot.",
                extended_support="confirmed_absent",
                source_url="https://example.org/support",
                retrieved_at=old_time,
                source_generated_at=old_time,
            ),
        },
    )

    result = run(
        load_sample("lakeview_dental"),
        evidence,
        observation_days=30,
    )
    router = next(
        item for item in result.findings
        if item.finding.rule.rule_id == "R10"
        and item.finding.observation.entity_id == "LV-RT01"
    )
    workstation = next(
        item for item in result.findings
        if item.finding.rule.rule_id == "R03"
        and item.finding.observation.entity_id == "LV-WS01"
    )

    assert router.finding.observation.status == "confirmed"
    assert workstation.finding.observation.status == "needs_review"
    assert result.freshness_policy.public_feed_max_age == timedelta(days=8)
    assert (
        result.freshness_policy.administrator_observation_max_age
        == timedelta(days=30)
    )


def test_shorter_observation_policy_requires_review():
    evidence = AssessmentEvidence(default_passwords={
        "LV-RT01": DefaultPasswordEvidence(
            asset_id="LV-RT01",
            applicability="Yes",
            default_password_changed="No",
            evidence_basis="Fictional administrator observation.",
            evidence_source="Synthetic test fixture",
            observed_at=NOW - timedelta(days=20),
        ),
    })

    result = run(
        load_sample("lakeview_dental"),
        evidence,
        observation_days=7,
    )
    router = next(
        item for item in result.findings
        if item.finding.rule.rule_id == "R10"
        and item.finding.observation.entity_id == "LV-RT01"
    )

    assert router.finding.observation.status == "needs_review"


def test_assessment_execution_makes_no_network_requests(monkeypatch):
    def unexpected_request(*args, **kwargs):
        pytest.fail("Assessment execution must remain offline.")

    monkeypatch.setattr(
        requests.sessions.Session, "request", unexpected_request
    )

    result = run(load_sample("westside_health"))

    assert result.rules_loaded == 24


def test_rejects_orphaned_evidence():
    evidence = AssessmentEvidence(default_passwords={
        "MISSING-ASSET": DefaultPasswordEvidence(
            asset_id="MISSING-ASSET",
            applicability="Unknown",
            default_password_changed="Unknown",
            evidence_basis="Synthetic test evidence.",
            evidence_source="Test fixture",
            observed_at=NOW,
        ),
    })

    with pytest.raises(InputError, match="unknown asset"):
        run(load_sample("lakeview_dental"), evidence)


def test_does_not_modify_assessment():
    assessment = load_sample("lakeview_dental")
    original = deepcopy(assessment)

    run(assessment)

    assert assessment == original