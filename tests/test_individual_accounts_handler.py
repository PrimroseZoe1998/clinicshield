from copy import deepcopy

import pytest

from clinicshield.checklist_input import Checklist
from clinicshield.input_limits import InputError
from clinicshield.rule_handlers import individual_accounts


def make_checklist(answer):
    return Checklist(
        answers={"Q06": answer},
        followups={},
    )


def test_no_reports_individual_account_gap():
    result = individual_accounts(make_checklist("No"))

    assert result is not None
    assert result.rule_id == "R14"
    assert result.entity_id == "assessment"
    assert result.status == "confirmed"
    assert result.evidence == (("Q06", "No"),)


def test_unknown_requires_review():
    result = individual_accounts(make_checklist("Unknown"))

    assert result is not None
    assert result.status == "needs_review"
    assert result.evidence == (("Q06", "Unknown"),)


def test_yes_does_not_trigger():
    assert individual_accounts(make_checklist("Yes")) is None


@pytest.mark.parametrize(
    "answer",
    ["", "no", " No ", "Maybe", None, True, 0, [], {}],
)
def test_rejects_invalid_answer(answer):
    with pytest.raises(InputError, match="valid Q06"):
        individual_accounts(make_checklist(answer))


def test_rejects_missing_q06():
    checklist = Checklist(answers={}, followups={})

    with pytest.raises(InputError, match="valid Q06"):
        individual_accounts(checklist)


def test_other_answers_do_not_override_q06():
    checklist = Checklist(
        answers={"Q06": "Yes", "Q01": "No", "Q07": "Unknown"},
        followups={},
    )

    assert individual_accounts(checklist) is None


def test_does_not_invent_affected_account_details():
    result = individual_accounts(make_checklist("No"))

    assert result is not None
    assert dict(result.evidence) == {"Q06": "No"}


@pytest.mark.parametrize("answer", ["Yes", "No", "Unknown"])
def test_does_not_modify_checklist(answer):
    checklist = make_checklist(answer)
    original = deepcopy(checklist)

    individual_accounts(checklist)

    assert checklist == original