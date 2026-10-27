from copy import deepcopy
from pathlib import Path

import pytest

from clinicshield.checklist_input import Checklist, read_checklist
from clinicshield.input_limits import InputError
from clinicshield.rule_engine import evaluate_checklist_rule
from clinicshield.rule_handlers import staff_security_training
from clinicshield.rule_loader import load_rule
from clinicshield.rule_models import RuleDefinition


ROOT = Path(__file__).resolve().parents[1]


def make_checklist(answer):
    return Checklist(answers={"Q25": answer}, followups={})


def test_no_reports_training_gap():
    result = staff_security_training(make_checklist("No"))

    assert result is not None
    assert result.rule_id == "R23"
    assert result.entity_id == "assessment"
    assert result.status == "confirmed"
    assert result.evidence == (("Q25", "No"),)


def test_unknown_requires_review():
    result = staff_security_training(make_checklist("Unknown"))

    assert result is not None
    assert result.status == "needs_review"
    assert result.evidence == (("Q25", "Unknown"),)


def test_yes_does_not_trigger():
    assert staff_security_training(make_checklist("Yes")) is None


@pytest.mark.parametrize(
    "answer",
    ["", "no", " No ", "Maybe", None, True, 0, [], {}],
)
def test_rejects_invalid_answer(answer):
    with pytest.raises(InputError, match="valid Q25"):
        staff_security_training(make_checklist(answer))


def test_rejects_missing_q25():
    with pytest.raises(InputError, match="valid Q25"):
        staff_security_training(Checklist(answers={}, followups={}))


@pytest.mark.parametrize("answer", ["Yes", "No", "Unknown"])
def test_does_not_modify_checklist(answer):
    checklist = make_checklist(answer)
    original = deepcopy(checklist)

    staff_security_training(checklist)

    assert checklist == original


@pytest.mark.parametrize(
    "answer,status,severity",
    [
        ("No", "confirmed", "Medium"),
        ("Unknown", "needs_review", "Info"),
    ],
)
def test_yaml_rule_runs_through_engine(answer, status, severity):
    rule = load_rule(ROOT / "rules" / "R23.yaml")

    finding = evaluate_checklist_rule(rule, make_checklist(answer))

    assert finding is not None
    assert finding.observation.rule_id == "R23"
    assert finding.observation.status == status
    assert finding.observation.evidence == (("Q25", answer),)
    assert finding.severity == severity
    assert finding.rule.kind == "checklist"
    assert finding.rule.review_status == "draft"


def test_engine_uses_configured_severity():
    rule = load_rule(ROOT / "rules" / "R23.yaml")
    data = rule.model_dump()
    data["severity"] = "High"
    configured = RuleDefinition.model_validate(data)

    finding = evaluate_checklist_rule(
        configured, make_checklist("No")
    )

    assert finding is not None
    assert finding.severity == "High"


def test_yes_produces_no_engine_finding():
    rule = load_rule(ROOT / "rules" / "R23.yaml")

    assert evaluate_checklist_rule(
        rule, make_checklist("Yes")
    ) is None


@pytest.mark.parametrize(
    "clinic",
    [
        "lakeview_dental",
        "southside_counseling",
        "westside_health",
    ],
)
def test_sample_checklists_do_not_trigger(clinic):
    rule = load_rule(ROOT / "rules" / "R23.yaml")
    folder = ROOT / "samples" / clinic
    checklist = read_checklist(
        (folder / "checklist.json").read_bytes(),
        (folder / "followups.json").read_bytes(),
    )

    assert evaluate_checklist_rule(rule, checklist) is None


def test_does_not_invent_affected_staff_or_topics():
    result = staff_security_training(make_checklist("No"))

    assert result is not None
    assert dict(result.evidence) == {"Q25": "No"}