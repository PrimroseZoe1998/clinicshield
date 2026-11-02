from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest
from test_score_explanation import inputs
from clinicshield.sample_evidence import build_sample_evidence
from clinicshield.sample_remediation import build_westside_post_fix, NOTICE
from clinicshield.assessment_scoring import score_assessment
from clinicshield.assessment_evidence import AssessmentFreshnessPolicy
from clinicshield.assessment_report import build_assessment_report
from clinicshield.report_text import render_assessment_text
from clinicshield.input_limits import InputError

ROOT=Path(__file__).resolve().parents[1]
NOW=datetime(2026,11,2,17,tzinfo=timezone.utc)


def score(a,e):
    return score_assessment(a,e,AssessmentFreshnessPolicy(administrator_observation_max_age=timedelta(days=30)),
                            rules_directory=ROOT/"rules",now=NOW)


def confirmed(r):
    return {i.finding.rule.rule_id for i in r.evaluation.findings if i.finding.observation.status=="confirmed"}


def test_before_after_is_reproducible_without_changing_original_fixture():
    original=inputs("westside_health");saved=deepcopy(original)
    before=score(original,build_sample_evidence("westside_health",original,now=NOW))
    after,evidence=build_westside_post_fix(original,now=NOW)
    result=score(after,evidence)
    assert original==saved and after is not original
    assert before.combined.final_score==80
    assert confirmed(before)=={"R03","R09","R11","R14","R16"}
    assert result.combined.final_score==99 and result.combined.band=="Good shape"
    assert not confirmed(result)
    assert result.is_provisional and result.grouped_scoring.review_groups
    assert result.evaluation.coverage_issues
    assert result.safeguards.earned_weight==46 and result.safeguards.applicable_weight==47
    assert after.checklist.answers["Q18"]=="Unknown"
    assert float(result.grouped_scoring.exposure.score)==100
    assert before.grouped_scoring.exposure.entity_count==result.grouped_scoring.exposure.entity_count


def test_changes_are_bounded_and_unverified_versions_stay_unknown():
    original=inputs("westside_health");after,evidence=build_westside_post_fix(original,now=NOW)
    assert len(after.inventory.assets)==35 and len(after.inventory.software)==5
    assert len(after.inventory.services)==2
    assert after.checklist.followups==original.checklist.followups
    assert {q for q in original.checklist.answers if original.checklist.answers[q]!=after.checklist.answers[q]}=={"Q05","Q06","Q11","Q18","Q23"}
    assert [s.version for s in after.inventory.software]==[s.version for s in original.inventory.software]
    assert all(s.version=="Unknown" for s in after.inventory.software)
    assert all("SYNTHETIC" in e.support_basis for e in evidence.os_support.values())
    assert evidence.medical_separation["WH-MD02"].separation_verified=="Yes"


@pytest.mark.parametrize("condition",["clinic","changed_identity","missing_telnet","naive_clock"])
def test_refuses_changed_or_wrong_baseline(condition):
    a=inputs("lakeview_dental" if condition=="clinic" else "westside_health")
    now=NOW
    if condition=="changed_identity":
        next(x for x in a.inventory.assets if x.asset_id=="WH-LT01").os_version="not the baseline"
    if condition=="missing_telnet":a.inventory.services=[]
    if condition=="naive_clock":now=NOW.replace(tzinfo=None)
    with pytest.raises((InputError,ValueError)):
        build_westside_post_fix(a,now=now)


def test_synthetic_label_and_unresolved_coverage_survive_txt():
    a,e=build_westside_post_fix(inputs("westside_health"),now=NOW)
    report=build_assessment_report(score(a,e))
    report["assessment_context"]={"input_mode":"Synthetic Westside post-fix fixture", "notice":NOTICE}
    text=render_assessment_text(report)
    assert "SYNTHETIC POST-FIX SCENARIO ONLY" in text
    assert "not completed work" in text
    assert "Score status: provisional" in text
    assert "Overall score: 99/100" in text
    assert "Q18: Unknown" in text
    assert "coverage" in text.lower()
