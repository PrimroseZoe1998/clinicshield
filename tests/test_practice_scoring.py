from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import json
import pytest
from test_score_explanation import inputs, run
from clinicshield.practice_scoring import PRACTICES, build_practice_scores
from clinicshield.assessment_report import build_assessment_report
from clinicshield.grouped_scoring import score_finding_groups
from clinicshield.report_text import render_assessment_text


def fraction(n):
    return Fraction(n["numerator"],n["denominator"])


def area(data,identifier):
    return next(p for p in data["practices"] if p["practice_id"]==identifier)


def test_mapping_is_unique_and_complete():
    questions=[q for _,_,qs,_ in PRACTICES for q in qs]
    rules=[q for _,_,_,rs in PRACTICES for q in rs]
    assert len(questions)==len(set(questions))==25
    assert set(questions)=={f"Q{i:02}" for i in range(1,26)}
    assert len(rules)==len(set(rules))==24
    assert set(rules)=={f"R{i:02}" for i in range(1,25)}


@pytest.mark.parametrize("clinic,expected",[("lakeview_dental",65),("southside_counseling",82),("westside_health",80)])
def test_practice_export_preserves_global_score_and_reconstructs_safeguards(clinic,expected):
    result=run(inputs(clinic),clinic);before=deepcopy(result)
    report=build_assessment_report(result)
    data=json.loads(json.dumps(report))["practice_scores"]
    assert result==before
    assert report["score"]["final"]==expected
    assert sum(p["safeguards"]["earned_weight"] for p in data["practices"])==result.safeguards.earned_weight
    assert sum(p["safeguards"]["applicable_weight"] for p in data["practices"])==result.safeguards.applicable_weight
    assert "Practice-area results (draft)" in render_assessment_text(report)
    assert "not an official HICP crosswalk" in data["notice"]
    assert all(p["status"] in {"draft_provisional","not_applicable"} for p in data["practices"])


def test_administrative_only_and_unknown_technical_do_not_create_perfect_exposure():
    result=run(inputs("southside_counseling"),"southside_counseling")
    data=build_practice_scores(result)
    assert all(p["exposure"]["score"] is None for p in data["practices"])
    assert all(p["combined"]["score"] is None for p in data["practices"])
    assert area(data,7)["review_group_count"]>0
    assert area(data,8)["safeguards"]["score"] is not None


def test_q23_exclusion_unknown_and_q24_single_weight():
    a=inputs();a.checklist.medical_devices_present="No";a.checklist.answers["Q02"]="Unknown"
    data=build_practice_scores(run(a))
    assert sum(p["safeguards"]["applicable_weight"] for p in data["practices"])==46
    assert area(data,9)["safeguards"]["score"] is None
    assert area(data,1)["safeguards"]["unknown_questions"]==["Q02"]
    assert area(data,1)["safeguards"]["earned_weight"]==0
    assert area(data,10)["question_ids"]==["Q24","Q25"]
    assert area(data,10)["safeguards"]["applicable_weight"]==4


def test_no_applicable_questions_or_evidence_is_not_applicable():
    a=inputs();a.checklist.medical_devices_present="No";result=run(a)
    groups=tuple(g for g in result.groups if not any(o.finding.rule.rule_id=="R11" for o in g.occurrences))
    grouped=score_finding_groups(result.evaluation.scoring_inventory.entities,groups)
    data=build_practice_scores(replace(result,groups=groups,grouped_scoring=grouped))
    assert area(data,9)["status"]=="not_applicable"
    assert area(data,9)["combined"]["score"] is None


def test_grouped_os_risk_counted_once_and_uses_full_inventory_size_factor():
    result=run(inputs("westside_health"),"westside_health")
    data=build_practice_scores(result);p=area(data,7);e=p["exposure"]
    assert e["entity_count"]==result.grouped_scoring.exposure.entity_count>20
    assert fraction(e["size_factor"])==Fraction(20,e["entity_count"])
    assert len(e["entities"])==e["entity_count"]
    assert any(fraction(x["before_cap"])==0 for x in e["entities"])
    assert fraction(e["adjusted_points"])==sum((fraction(x["after_cap"]) for x in e["entities"]),Fraction())*fraction(e["size_factor"])
    lake=area(build_practice_scores(run(inputs())),7)["exposure"]
    assert len(lake["technical_groups"])==3


def test_practice_cap_retains_precap_points():
    result=run(inputs());base=next(g for g in result.groups if g.has_confirmed_gap and any(o.finding.rule.rule_id=="R05" for o in g.occurrences))
    groups=[]
    for i in range(5):
        key=f"synthetic-risk-{i}"
        groups.append(replace(base,issue_key=key,occurrences=tuple(replace(o,issue_key=key) for o in base.occurrences)))
    grouped=score_finding_groups(result.evaluation.scoring_inventory.entities,tuple(groups))
    data=build_practice_scores(replace(result,groups=tuple(groups),grouped_scoring=grouped))
    e=area(data,2)["exposure"]
    assert fraction(e["adjusted_points"])==25
    row=next(x for x in e["entities"] if x["entity_id"]==base.scoring_entity_id)
    assert fraction(row["before_cap"])==45 and fraction(row["after_cap"])==25


def test_critical_ceiling_stays_in_its_practice():
    result=run(inputs());groups=[]
    for group in result.groups:
        occurrences=tuple(replace(o,finding=replace(o.finding,rule=o.finding.rule.model_copy(update={"severity":"Critical"})))
                          if o.finding.rule.rule_id=="R05" else o for o in group.occurrences)
        groups.append(replace(group,occurrences=occurrences))
    grouped=score_finding_groups(result.evaluation.scoring_inventory.entities,tuple(groups))
    data=build_practice_scores(replace(result,groups=tuple(groups),grouped_scoring=grouped))
    assert area(data,2)["combined"]["rounded"]>69
    assert area(data,2)["combined"]["score"]==69
    assert area(data,2)["combined"]["critical_findings"]
    assert area(data,7)["combined"]["critical_ceiling"] is None
    assert area(data,7)["combined"]["score"] is not None


def test_inventory_only_lakeview_keeps_overall_80_and_draft_labels():
    from app import generate_example
    report=generate_example("lakeview_dental",30,False)
    assert report["score"]["final"]==80
    p=area(report["practice_scores"],2)
    assert p["status"]=="draft_provisional"
    assert fraction(p["safeguards"]["score"])==Fraction(200,3)
    assert fraction(p["exposure"]["score"])==91
    assert area(report["practice_scores"],7)["combined"]["score"] is None
