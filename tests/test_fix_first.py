from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import pytest

from app import generate_example
from clinicshield.finding_groups import FindingGroup, FindingOccurrence
from clinicshield.fix_first import action_group, build_fix_first, rank_actions
from clinicshield.rule_engine import RuleFinding
from clinicshield.rule_handlers import RuleObservation
from clinicshield.rule_loader import load_rule
from clinicshield.report_text import render_assessment_text

ROOT = Path(__file__).resolve().parents[1]


def candidate(entity="device:A", rules=("R05",), **changes):
    item = {
        "entity_id": entity, "rule_ids": list(rules), "issue_keys": [entity],
        "recommendations": ["A test action"], "owners": ["IT"], "costs": ["none"],
        "points": Fraction(6), "effort": 2, "kev": False,
        "essential_questions": [], "touches_phi": False,
    }
    item.update(changes)
    return item


def test_priority_is_points_over_effort_not_severity_or_input_order():
    actions = rank_actions([
        candidate("slow-critical", points=Fraction(10), effort=3),
        candidate("quick-high", points=Fraction(6), effort=1),
    ])
    assert [item["entity_id"] for item in actions] == ["quick-high", "slow-critical"]
    assert actions[1]["priority_exact"] == "10/3"


def test_ties_follow_kev_essential_phi_rule_then_entity():
    items = [
        candidate("last", rules=("R24",)),
        candidate("phi", touches_phi=True),
        candidate("essential", essential_questions=["Q01"]),
        candidate("kev", kev=True),
        candidate("device:B", rules=("R03",)),
        candidate("device:A", rules=("R03",)),
    ]
    assert [a["entity_id"] for a in rank_actions(items)] == [
        "kev", "essential", "phi", "device:A", "device:B", "last",
    ]
    assert rank_actions(items) == rank_actions(list(reversed(items)))


def test_duplicates_do_not_sum_points_or_promote_cheapest_effort():
    items = [candidate(points=Fraction(6), effort=1),
             candidate(rules=("R08",), issue_keys=["other"], points=Fraction(9), effort=3)]
    original = deepcopy(items)
    result = rank_actions(items)
    assert len(result) == 1
    assert result[0]["points"] == 9
    assert result[0]["effort"] == 3
    assert result[0]["priority_exact"] == "3"
    assert result[0]["rule_ids"] == ["R05", "R08"]
    assert result[0]["issue_keys"] == ["device:A", "other"]
    assert items == original


def test_different_assets_and_distinct_remediations_remain_separate():
    result = rank_actions([
        candidate(), candidate("device:B"),
        candidate(recommendations=["A different action"]),
    ])
    assert len(result) == 3


@pytest.mark.parametrize("rules,effort,costs,expected", [
    (["R05"], 1, ["none"], "Do today free"),
    (["R05"], 2, ["low"], "This month low cost"),
    (["R05"], 1, ["unknown"], "Ask your vendor"),
    (["R05"], 1, ["none", "unknown"], "Ask your vendor"),
    (["R05"], 3, ["none"], "Ask your vendor"),
    (["R23"], 2, ["unknown"], "Policy and training"),
])
def test_groups_do_not_invent_free_or_low_cost(rules, effort, costs, expected):
    assert action_group(rules, effort, costs) == expected


def occurrence(rule_id, status="confirmed", **details):
    finding = RuleFinding(
        rule=load_rule(ROOT / "rules" / f"{rule_id}.yaml"),
        observation=RuleObservation(rule_id, "assessment", status, tuple(details.items())),
    )
    return FindingOccurrence(finding, "assessment", "test-issue", "administrative", "Test grouping")


def test_unresolved_evidence_does_not_supply_priority_effort_or_essential_tie():
    confirmed = occurrence("R20", Q20="Yes", Q24a="No")
    unresolved = occurrence("R23", "needs_review", Q25="No")
    group = FindingGroup("assessment", "test-issue", "administrative", (confirmed, unresolved))
    result = SimpleNamespace(
        groups=[group],
        evaluation=SimpleNamespace(scoring_inventory=SimpleNamespace(entities=[])),
        grouped_scoring=SimpleNamespace(technical_findings=[]),
    )
    plan = build_fix_first(result)
    assert plan["actions"][0]["points"] == 6
    assert plan["actions"][0]["rule_ids"] == ["R20"]
    assert not plan["actions"][0]["tie_breakers"]["essential_questions"]
    assert plan["verification_items"][0]["rule_ids"] == ["R23"]


@pytest.mark.parametrize("clinic,expected", [
    ("lakeview_dental", 65), ("southside_counseling", 82), ("westside_health", 80),
])
def test_scenario_scores_unchanged_and_plan_reaches_readable_download(clinic, expected):
    report = generate_example(clinic, 30, True)
    assert report["score"]["final"] == expected
    assert report["score"]["status"] == "provisional"
    assert all("R24" not in action["rule_ids"] for action in report["fix_first"]["actions"])
    assert any("R24" in item["rule_ids"] for item in report["fix_first"]["verification_items"])
    text = render_assessment_text(report)
    assert "Fix First plan" in text
    assert "Verify before planning remediation" in text
    assert "not an estimated score increase" in text


def test_os_support_is_one_action_with_both_rules_and_one_numerator():
    report = generate_example("lakeview_dental", 30, True)
    actions = [a for a in report["fix_first"]["actions"]
               if a["entity_id"] == "device:LV-SRV01" and "R03" in a["rule_ids"]]
    assert len(actions) == 1
    assert actions[0]["rule_ids"] == ["R03", "R08"]
    assert actions[0]["points"] == 9
    assert actions[0]["priority_exact"] == "3"


def test_empty_assessed_scope_has_no_invented_actions():
    result = SimpleNamespace(groups=[], evaluation=SimpleNamespace(
        scoring_inventory=SimpleNamespace(entities=[])),
        grouped_scoring=SimpleNamespace(technical_findings=[]))
    assert build_fix_first(result)["actions"] == []
    assert build_fix_first(result)["verification_items"] == []


@pytest.mark.parametrize("kev,applicable,expected", [
    ("listed", "match", True), ("unknown", "match", False),
    ("listed", "needs_review", False),
])
def test_kev_tie_requires_both_membership_and_applicability(kev, applicable, expected):
    finding = RuleFinding(
        load_rule(ROOT / "rules" / "R01.yaml"),
        RuleObservation("R01", "A", "confirmed", (("kev_status", kev), ("applicability", applicable))),
    )
    item = FindingOccurrence(finding, "device:A", "cve", "technical", "Test")
    result = SimpleNamespace(
        groups=[FindingGroup("device:A", "cve", "technical", (item,))],
        evaluation=SimpleNamespace(scoring_inventory=SimpleNamespace(entities=[])),
        grouped_scoring=SimpleNamespace(technical_findings=[SimpleNamespace(
            finding=SimpleNamespace(entity_id="device:A", finding_id="cve", risk_points=Fraction(10)))]),
    )
    action = build_fix_first(result)["actions"][0]
    assert action["tie_breakers"]["confirmed_kev"] is expected
