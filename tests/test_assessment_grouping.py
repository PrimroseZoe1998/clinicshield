from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from clinicshield.assessment_evidence import (
    AssessmentEvidence,
    AssessmentFreshnessPolicy,
)
from clinicshield.assessment_grouping import group_assessment_findings
from clinicshield.assessment_input import read_assessment
from clinicshield.assessment_runner import evaluate_assessment
from clinicshield.grouped_scoring import score_finding_groups
from clinicshield.input_limits import InputError
from clinicshield.lifecycle_evidence import LifecycleEvidence
from clinicshield.schemas import Service


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


def evaluate(assessment, evidence=None):
    return evaluate_assessment(
        assessment,
        evidence if evidence is not None else AssessmentEvidence(),
        AssessmentFreshnessPolicy(
            administrator_observation_max_age=timedelta(days=30)
        ),
        rules_directory=ROOT / "rules",
        now=NOW,
    )


def group_rules(group):
    return {
        item.finding.rule.rule_id
        for item in group.occurrences
    }


def test_os_and_smb_support_share_one_risk_group():
    assessment = load_sample()
    evidence = AssessmentEvidence(os_support={
        "LV-SRV01": LifecycleEvidence(
            os_name="Windows Server",
            os_version="2012 R2",
            support_status="unsupported",
            support_basis="Fictional support fixture; no ESU coverage.",
            extended_support="confirmed_absent",
            source_url="https://example.org/support-fixture",
            retrieved_at=NOW,
            source_generated_at=NOW,
        ),
    })

    evaluation = evaluate(assessment, evidence)
    groups = group_assessment_findings(evaluation)
    support = next(
        group for group in groups
        if group.scoring_entity_id == "device:LV-SRV01"
        and {"R03", "R08"} <= group_rules(group)
    )

    assert support.severity == "High"
    assert len(support.occurrences) == 2
    assert any(
        dict(item.finding.observation.evidence).get("service") == "smb"
        for item in support.occurrences
    )

    scoring = score_finding_groups(
        evaluation.scoring_inventory.entities, groups
    )
    support_points = [
        item.finding.risk_points
        for item in scoring.technical_findings
        if item.finding.entity_id == "device:LV-SRV01"
    ]
    assert support_points == [9]


def test_remote_exposure_and_telnet_remain_distinct():
    assessment = load_sample()
    assessment.inventory.services.append(Service(
        asset_id="LV-RT01",
        host="192.0.2.50",
        port=23,
        protocol="tcp",
        service="telnet",
        exposure="internet",
    ))

    groups = group_assessment_findings(evaluate(assessment))
    relevant = [
        group for group in groups
        if group.scoring_entity_id == "device:LV-RT01"
        and group_rules(group) & {"R06", "R09"}
    ]

    assert len(relevant) == 2
    assert {frozenset(group_rules(g)) for g in relevant} == {
        frozenset({"R06"}),
        frozenset({"R09"}),
    }


def test_q17_service_contexts_do_not_multiply_safeguard_groups():
    assessment = load_sample()
    assessment.inventory.services.append(Service(
        asset_id="LV-RT01",
        host="192.0.2.50",
        port=22,
        protocol="tcp",
        service="ssh",
        exposure="internal",
    ))

    groups = group_assessment_findings(evaluate(assessment))
    remote = [group for group in groups if "R07" in group_rules(group)]

    assert len(remote) == 1
    assert remote[0].scoring_category == "administrative"
    assert remote[0].scoring_entity_id == "assessment"
    assert len(remote[0].occurrences) == 2


def test_duplicate_software_rows_preserve_evidence_without_extra_groups():
    assessment = load_sample()
    email = next(
        software for software in assessment.inventory.software
        if software.purpose == "email"
    )
    assessment.inventory.software.append(email.model_copy())

    groups = group_assessment_findings(evaluate(assessment))
    email_groups = [
        group for group in groups if "R12" in group_rules(group)
    ]

    assert len(email_groups) == 1
    assert len(email_groups[0].occurrences) == 2
    assert email_groups[0].scoring_category == "administrative"
    assert len({
        item.finding.observation.entity_id
        for item in email_groups[0].occurrences
    }) == 2


@pytest.mark.parametrize(
    "clinic",
    ["lakeview_dental", "southside_counseling", "westside_health"],
)
def test_duplicate_evaluation_evidence_does_not_inflate_exposure(clinic):
    evaluation = evaluate(load_sample(clinic))
    duplicate = replace(
        evaluation,
        findings=evaluation.findings + evaluation.findings,
    )

    original_score = score_finding_groups(
        evaluation.scoring_inventory.entities,
        group_assessment_findings(evaluation),
    )
    duplicate_score = score_finding_groups(
        duplicate.scoring_inventory.entities,
        group_assessment_findings(duplicate),
    )

    assert duplicate_score.exposure == original_score.exposure
    assert duplicate_score.critical_findings == original_score.critical_findings


def test_mfa_and_agreement_findings_are_administrative():
    groups = group_assessment_findings(
        evaluate(load_sample("southside_counseling"))
    )
    selected = [
        group for group in groups
        if group_rules(group) & {"R12", "R13", "R17"}
    ]

    assert selected
    assert all(
        group.scoring_category == "administrative"
        for group in selected
    )


def test_missing_grouping_identity_is_rejected():
    evaluation = evaluate(load_sample())
    linked = next(
        item for item in evaluation.findings
        if item.finding.rule.rule_id == "R12"
    )
    altered_observation = replace(
        linked.finding.observation,
        evidence=tuple(
            (key, value)
            for key, value in linked.finding.observation.evidence
            if key != "product"
        ),
    )
    altered = replace(
        linked,
        finding=replace(
            linked.finding,
            observation=altered_observation,
        ),
    )

    with pytest.raises(InputError, match="grouping evidence"):
        group_assessment_findings(
            replace(evaluation, findings=(altered,))
        )