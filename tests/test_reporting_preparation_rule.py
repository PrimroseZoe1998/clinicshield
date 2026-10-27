from copy import deepcopy
from pathlib import Path

import pytest

from clinicshield.checklist_input import Checklist, read_checklist
from clinicshield.input_limits import InputError
from clinicshield.rule_engine import evaluate_checklist_rule
from clinicshield.rule_handlers import reporting_preparation
from clinicshield.rule_loader import load_rule


ROOT = Path(__file__).resolve().parents[1]


def make_checklist(reporting, notification):
    return Checklist(
        answers={"Q21": reporting, "Q22": notification},
        followups={},
    )


@pytest.mark.parametrize(
    "reporting,notification,expected",
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
def test_all_answer_combinations(reporting, notification, expected):
    result = reporting_preparation(
        make_checklist(reporting, notification)
    )

    if expected is None:
        assert result is None
    else:
        assert result is not None
        assert result.rule_id == "R21"
        assert result.entity_id == "assessment"
        assert result.status == expected
        assert result.evidence == (
            ("Q21", reporting),
            ("Q22", notification),
        )


@pytest.mark.parametrize("field", ["Q21", "Q22"])
@pytest.mark.parametrize("value", ["", "no", None, True, [], {}])
def test_rejects_invalid_answers(field, value):
    checklist = make_checklist("Yes", "Yes")
    checklist.answers[field] = value

    with pytest.raises(InputError, match=f"valid {field}"):
        reporting_preparation(checklist)


@pytest.mark.parametrize("field", ["Q21", "Q22"])
def test_rejects_missing_answers(field):
    checklist = make_checklist("Yes", "Yes")
    del checklist.answers[field]

    with pytest.raises(InputError, match=f"valid {field}"):
        reporting_preparation(checklist)


def test_preserves_unknown_alongside_reported_gap():
    result = reporting_preparation(make_checklist("No", "Unknown"))

    assert result is not None
    assert result.status == "confirmed"
    assert dict(result.evidence) == {
        "Q21": "No",
        "Q22": "Unknown",
    }


def test_does_not_invent_breach_details():
    result = reporting_preparation(make_checklist("No", "No"))

    assert result is not None
    assert dict(result.evidence) == {"Q21": "No", "Q22": "No"}


def test_does_not_modify_checklist():
    checklist = make_checklist("Unknown", "No")
    original = deepcopy(checklist)

    reporting_preparation(checklist)

    assert checklist == original


@pytest.mark.parametrize(
    "reporting,notification,severity",
    [
        ("No", "Yes", "Medium"),
        ("Yes", "No", "Medium"),
        ("Unknown", "Yes", "Info"),
        ("No", "Unknown", "Medium"),
    ],
)
def test_yaml_rule_runs_through_engine(
    reporting, notification, severity
):
    rule = load_rule(ROOT / "rules" / "R21.yaml")

    finding = evaluate_checklist_rule(
        rule, make_checklist(reporting, notification)
    )

    assert finding is not None
    assert finding.observation.rule_id == "R21"
    assert finding.severity == severity
    assert finding.rule.kind == "checklist"
    assert finding.rule.review_status == "draft"


def test_both_yes_produce_no_engine_finding():
    rule = load_rule(ROOT / "rules" / "R21.yaml")

    assert evaluate_checklist_rule(
        rule, make_checklist("Yes", "Yes")
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
    rule = load_rule(ROOT / "rules" / "R21.yaml")
    folder = ROOT / "samples" / clinic
    checklist = read_checklist(
        (folder / "checklist.json").read_bytes(),
        (folder / "followups.json").read_bytes(),
    )

    assert evaluate_checklist_rule(rule, checklist) is None