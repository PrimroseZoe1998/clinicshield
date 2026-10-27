from copy import deepcopy
from pathlib import Path

import pytest

from clinicshield.checklist_input import Checklist, read_checklist
from clinicshield.input_limits import InputError
from clinicshield.rule_engine import evaluate_checklist_rule
from clinicshield.rule_handlers import documented_risk_analysis
from clinicshield.rule_loader import load_rule


ROOT = Path(__file__).resolve().parents[1]


def make_checklist(answer):
    return Checklist(
        answers={"Q24": "No"},
        followups={"Q24a": "No", "Q24b": answer},
    )


def test_no_reports_risk_analysis_gap():
    result = documented_risk_analysis(make_checklist("No"))

    assert result is not None
    assert result.rule_id == "R22"
    assert result.entity_id == "assessment"
    assert result.status == "confirmed"
    assert result.evidence == (("Q24b", "No"),)


def test_unknown_requires_review():
    result = documented_risk_analysis(make_checklist("Unknown"))

    assert result is not None
    assert result.status == "needs_review"
    assert result.evidence == (("Q24b", "Unknown"),)


def test_yes_does_not_trigger():
    assert documented_risk_analysis(make_checklist("Yes")) is None


@pytest.mark.parametrize(
    "answer",
    ["", "no", " No ", "Maybe", None, True, 0, [], {}],
)
def test_rejects_invalid_followup(answer):
    with pytest.raises(InputError, match="valid Q24b"):
        documented_risk_analysis(make_checklist(answer))


def test_does_not_infer_missing_q24b_from_combined_answer():
    checklist = Checklist(
        answers={"Q24": "No"},
        followups={"Q24a": "No"},
    )

    with pytest.raises(InputError, match="valid Q24b"):
        documented_risk_analysis(checklist)


@pytest.mark.parametrize("q24a", ["Yes", "No", "Unknown"])
def test_q24a_gap_does_not_imply_risk_analysis_gap(q24a):
    checklist = Checklist(
        answers={"Q24": "No" if q24a == "No" else q24a},
        followups={"Q24a": q24a, "Q24b": "Yes"},
    )

    assert documented_risk_analysis(checklist) is None


def test_q24b_gap_triggers_when_security_official_is_present():
    checklist = Checklist(
        answers={"Q24": "No"},
        followups={"Q24a": "Yes", "Q24b": "No"},
    )

    result = documented_risk_analysis(checklist)

    assert result is not None
    assert result.evidence == (("Q24b", "No"),)


@pytest.mark.parametrize("answer", ["Yes", "No", "Unknown"])
def test_does_not_modify_checklist(answer):
    checklist = make_checklist(answer)
    original = deepcopy(checklist)

    documented_risk_analysis(checklist)

    assert checklist == original


@pytest.mark.parametrize(
    "answer,status,severity",
    [
        ("No", "confirmed", "High"),
        ("Unknown", "needs_review", "Info"),
    ],
)
def test_yaml_rule_runs_through_engine(answer, status, severity):
    rule = load_rule(ROOT / "rules" / "R22.yaml")

    finding = evaluate_checklist_rule(rule, make_checklist(answer))

    assert finding is not None
    assert finding.observation.status == status
    assert finding.observation.evidence == (("Q24b", answer),)
    assert finding.severity == severity
    assert finding.rule.kind == "checklist"
    assert finding.rule.review_status == "draft"


def test_yes_produces_no_engine_finding():
    rule = load_rule(ROOT / "rules" / "R22.yaml")

    assert evaluate_checklist_rule(
        rule, make_checklist("Yes")
    ) is None


@pytest.mark.parametrize(
    "clinic,should_trigger",
    [
        ("lakeview_dental", False),
        ("southside_counseling", True),
        ("westside_health", False),
    ],
)
def test_matches_sample_checklists(clinic, should_trigger):
    rule = load_rule(ROOT / "rules" / "R22.yaml")
    folder = ROOT / "samples" / clinic
    checklist = read_checklist(
        (folder / "checklist.json").read_bytes(),
        (folder / "followups.json").read_bytes(),
    )

    finding = evaluate_checklist_rule(rule, checklist)

    if should_trigger:
        assert finding is not None
        assert finding.observation.status == "confirmed"
        assert finding.observation.evidence == (("Q24b", "No"),)
    else:
        assert finding is None