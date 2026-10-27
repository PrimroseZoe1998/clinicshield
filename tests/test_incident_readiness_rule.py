from copy import deepcopy
from pathlib import Path

import pytest

from clinicshield.checklist_input import Checklist, read_checklist
from clinicshield.input_limits import InputError
from clinicshield.rule_engine import evaluate_checklist_rule
from clinicshield.rule_handlers import incident_readiness
from clinicshield.rule_loader import load_rule


ROOT = Path(__file__).resolve().parents[1]


def make_checklist(plan, responsibility):
    return Checklist(
        answers={"Q20": plan},
        followups={"Q24a": responsibility},
    )


@pytest.mark.parametrize(
    "plan,responsibility,expected",
    [
        ("Yes", "Yes", None),
        ("Yes", "No", "confirmed"),
        ("Yes", "Unknown", "needs_review"),
        ("No", "Yes", "confirmed"),
        ("No", "No", "confirmed"),
        ("No", "Unknown", "confirmed"),
        ("Unknown", "Yes", "needs_review"),
        ("Unknown", "No", "confirmed"),
        ("Unknown", "Unknown", "needs_review"),
    ],
)
def test_all_answer_combinations(plan, responsibility, expected):
    result = incident_readiness(make_checklist(plan, responsibility))

    if expected is None:
        assert result is None
    else:
        assert result is not None
        assert result.rule_id == "R20"
        assert result.entity_id == "assessment"
        assert result.status == expected
        assert result.evidence == (
            ("Q20", plan),
            ("Q24a", responsibility),
        )


@pytest.mark.parametrize("field", ["Q20", "Q24a"])
@pytest.mark.parametrize("value", ["", "no", None, True, [], {}])
def test_rejects_invalid_answers(field, value):
    checklist = make_checklist("Yes", "Yes")
    if field == "Q20":
        checklist.answers[field] = value
    else:
        checklist.followups[field] = value

    with pytest.raises(InputError, match=f"valid {field}"):
        incident_readiness(checklist)


@pytest.mark.parametrize("field", ["Q20", "Q24a"])
def test_rejects_missing_answers(field):
    checklist = make_checklist("Yes", "Yes")
    if field == "Q20":
        del checklist.answers[field]
    else:
        del checklist.followups[field]

    with pytest.raises(InputError, match=f"valid {field}"):
        incident_readiness(checklist)


def test_q24b_gap_does_not_trigger_r20():
    checklist = make_checklist("Yes", "Yes")
    checklist.answers["Q24"] = "No"
    checklist.followups["Q24b"] = "No"

    assert incident_readiness(checklist) is None


def test_does_not_infer_missing_q24a_from_q24_or_q24b():
    checklist = Checklist(
        answers={"Q20": "Yes", "Q24": "No"},
        followups={"Q24b": "No"},
    )

    with pytest.raises(InputError, match="valid Q24a"):
        incident_readiness(checklist)


def test_mixed_gap_and_unknown_preserves_both_answers():
    result = incident_readiness(make_checklist("No", "Unknown"))

    assert result is not None
    assert result.status == "confirmed"
    assert dict(result.evidence) == {
        "Q20": "No",
        "Q24a": "Unknown",
    }


def test_does_not_modify_checklist():
    checklist = make_checklist("Unknown", "No")
    original = deepcopy(checklist)

    incident_readiness(checklist)

    assert checklist == original


@pytest.mark.parametrize(
    "plan,responsibility,severity",
    [
        ("No", "Yes", "High"),
        ("Yes", "No", "High"),
        ("Unknown", "Yes", "Info"),
        ("No", "Unknown", "High"),
    ],
)
def test_yaml_rule_runs_through_engine(plan, responsibility, severity):
    rule = load_rule(ROOT / "rules" / "R20.yaml")

    finding = evaluate_checklist_rule(
        rule, make_checklist(plan, responsibility)
    )

    assert finding is not None
    assert finding.severity == severity
    assert finding.rule.kind == "checklist"
    assert finding.rule.review_status == "draft"


def test_both_yes_produce_no_engine_finding():
    rule = load_rule(ROOT / "rules" / "R20.yaml")

    assert evaluate_checklist_rule(
        rule, make_checklist("Yes", "Yes")
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
    rule = load_rule(ROOT / "rules" / "R20.yaml")
    folder = ROOT / "samples" / clinic
    checklist = read_checklist(
        (folder / "checklist.json").read_bytes(),
        (folder / "followups.json").read_bytes(),
    )

    finding = evaluate_checklist_rule(rule, checklist)

    if should_trigger:
        assert finding is not None
        assert finding.observation.status == "confirmed"
        assert dict(finding.observation.evidence) == {
            "Q20": "No",
            "Q24a": "No",
        }
    else:
        assert finding is None