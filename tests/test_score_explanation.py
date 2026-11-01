import json
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from fractions import Fraction
from pathlib import Path
import pytest
from clinicshield.assessment_input import read_assessment
from clinicshield.assessment_evidence import AssessmentFreshnessPolicy
from clinicshield.assessment_scoring import score_assessment
from clinicshield.assessment_report import build_assessment_report
from clinicshield.sample_evidence import build_sample_evidence
from clinicshield.report_text import render_assessment_text
from clinicshield.score_explanation import build_score_explanation
from clinicshield.scoring import combine_scores

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)


def inputs(clinic="lakeview_dental"):
    p=ROOT/"samples"/clinic
    return read_assessment(checklist_json=(p/"checklist.json").read_bytes(),
        followups_json=(p/"followups.json").read_bytes(), assets_csv=(p/"assets.csv").read_bytes(),
        software_csv=(p/"software.csv").read_bytes(),
        services_csv=(p/"services.csv").read_bytes() if (p/"services.csv").exists() else None)


def run(a,clinic="lakeview_dental"):
    return score_assessment(a, build_sample_evidence(clinic,a,now=NOW),
        AssessmentFreshnessPolicy(administrator_observation_max_age=timedelta(days=30)),rules_directory=ROOT/"rules",now=NOW)


def fraction(data):
    return Fraction(data["numerator"],data["denominator"])


@pytest.mark.parametrize("clinic,expected",[("lakeview_dental",65),
    ("southside_counseling",82),("westside_health",80)])
def test_export_arithmetic_reconciles_and_scores_unchanged(clinic,expected):
    a=inputs(clinic);before=deepcopy(a);result=run(a,clinic)
    report=json.loads(json.dumps(build_assessment_report(result)))
    x=report["score_explanation"];s=x["safeguards"];e=x["exposure"];c=x["combined"]
    assert a==before
    assert sum(q["earned"] for q in s["questions"])==s["earned_weight"]
    assert sum(q["available"] for q in s["questions"])==s["applicable_weight"]
    assert fraction(s["score"])==Fraction(100*s["earned_weight"],s["applicable_weight"])
    assert sum((fraction(row["after_cap"]) for row in e["entities"]),Fraction())==fraction(e["capped_total"])
    assert fraction(e["capped_total"])*fraction(e["size_factor"])==fraction(e["adjusted_points"])
    assert max(0,100-fraction(e["adjusted_points"]))==fraction(e["score"])
    assert fraction(c["raw"])==Fraction(3,5)*fraction(s["score"])+Fraction(2,5)*fraction(e["score"])
    assert c["final"]==report["score"]["final"]==expected
    assert "Why this score" in render_assessment_text(report)
    for row in e["technical_groups"]:
        product=Fraction(row["base_points"])
        for multiplier in row["multipliers"].values():product*=fraction(multiplier)
        assert product==fraction(row["risk_points"])


def test_one_answer_change_has_exact_safeguards_effect_without_extra_exposure():
    a=inputs();a.checklist.answers["Q02"]="No";before=run(a)
    a.checklist.answers["Q02"]="Yes";after=run(a)
    assert after.safeguards.score-before.safeguards.score==Fraction(300,47)
    assert before.grouped_scoring.exposure==after.grouped_scoring.exposure
    assert after.combined.raw_score-before.combined.raw_score==Fraction(180,47)


def test_q23_exclusion_unknown_and_q24_single_count():
    a=inputs();a.checklist.medical_devices_present="No";a.checklist.answers["Q02"]="Unknown"
    result=run(a);s=result.explanation["safeguards"]
    assert s["applicable_weight"]==46
    q23=next(q for q in s["questions"] if q["question_id"]=="Q23")
    assert q23["available"]==q23["earned"]==0 and not q23["applicable"]
    assert "Q02" in s["unknown_questions"]
    assert next(q for q in s["questions"] if q["question_id"]=="Q02")["earned"]==0
    assert len(s["questions"])==25
    assert not any(q["question_id"] in {"Q24a","Q24b"} for q in s["questions"])


def test_shared_os_risk_has_one_contribution_and_all_entities_included():
    result=run(inputs());e=result.explanation["exposure"]
    rows=[row for row in e["technical_groups"] if "R08" in row["rule_ids"]]
    assert len(rows)==1 and rows[0]["rule_ids"]==["R03","R08"]
    assert len(e["entities"])==result.grouped_scoring.exposure.entity_count
    assert any(fraction(row["before_cap"])==0 for row in e["entities"])


def test_critical_ceiling_and_rounding_are_retained():
    a=inputs()
    a.checklist.answers={key:"Yes" for key in a.checklist.answers}
    a.checklist.followups={key:"Yes" for key in a.checklist.followups}
    result=run(a)
    combined=combine_scores(result.safeguards,result.grouped_scoring.exposure,
        open_critical_findings=("synthetic-critical-group",))
    x=build_score_explanation(a.checklist,result.safeguards,result.grouped_scoring,
        combined,result.evaluation.scoring_inventory.entities,result.groups)
    assert x["combined"]["critical_ceiling"]==69
    assert x["combined"]["critical_findings"]==["synthetic-critical-group"]
    assert x["combined"]["rounded"]==combined.rounded_score
    assert combined.rounded_score>69
    assert x["combined"]["final"]==69


def test_cap_explanation_uses_grouped_points_before_and_after_cap():
    from dataclasses import replace
    from clinicshield.grouped_scoring import score_finding_groups
    a=inputs();result=run(a)
    base=next(g for g in result.groups if g.scoring_category=="technical" and g.has_confirmed_gap)
    groups=[]
    for i in range(5):
        issue=f"synthetic-distinct-risk-{i}"
        groups.append(replace(base,issue_key=issue,occurrences=tuple(
            replace(o,issue_key=issue) for o in base.occurrences)))
    entities=result.evaluation.scoring_inventory.entities
    grouped=score_finding_groups(entities,tuple(groups))
    combined=combine_scores(result.safeguards,grouped.exposure,open_critical_findings=grouped.critical_findings)
    x=build_score_explanation(a.checklist,result.safeguards,grouped,combined,entities,tuple(groups))
    row=next(row for row in x["exposure"]["entities"] if row["entity_id"]==base.scoring_entity_id)
    assert fraction(row["before_cap"])>25
    assert fraction(row["after_cap"])==25
    assert fraction(x["exposure"]["adjusted_points"])==25
