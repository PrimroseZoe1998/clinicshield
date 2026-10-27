from copy import deepcopy
from pathlib import Path

import pytest

from clinicshield.checklist_input import Checklist, read_checklist
from clinicshield.input_limits import InputError
from clinicshield.rule_engine import evaluate_checklist_rule
from clinicshield.rule_handlers import backup_safeguards
from clinicshield.rule_loader import load_rule


ROOT = Path(__file__).resolve().parents[1]


def make_checklist(backups, restore_testing):
    return Checklist(
        answers={"Q10": backups, "Q11": restore_testing},
        followups={},
    )


@pytest.mark.parametrize(
    "backups,restore_testing,expected",
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
def test_all_answer_combinations(backups, restore_testing, expected):
    result = backup_safeguards(
        make_checklist(backups, restore_testing)
    )

    if expected is None:
        assert result is None
    else:
        assert result is not None
        assert result.rule_id == "R16"
        assert result.entity_id == "assessment"
        assert result.status == expected
        assert result.evidence == (
            ("Q10", backups),
            ("Q11", restore_testing),
        )


@pytest.mark.parametrize("field", ["Q10", "Q11"])
@pytest.mark.parametrize("value", ["", "no", None, True, [], {}])
def test_rejects_invalid_answers(field, value):
    checklist = make_checklist("Yes", "Yes")
    checklist.answers[field] = value

    with pytest.raises(InputError, match=f"valid {field}"):
        backup_safeguards(checklist)


@pytest.mark.parametrize("field", ["Q10", "Q11"])
def test_rejects_missing_answers(field):
    checklist = make_checklist("Yes", "Yes")
    del checklist.answers[field]

    with pytest.raises(InputError, match=f"valid {field}"):
        backup_safeguards(checklist)


def test_does_not_invent_specific_q10_faults():
    result = backup_safeguards(make_checklist("No", "Yes"))

    assert result is not None
    assert dict(result.evidence) == {"Q10": "No", "Q11": "Yes"}


def test_preserves_unknown_alongside_confirmed_gap():
    result = backup_safeguards(make_checklist("Unknown", "No"))

    assert result is not None
    assert result.status == "confirmed"
    assert dict(result.evidence)["Q10"] == "Unknown"


def test_does_not_modify_checklist():
    checklist = make_checklist("No", "Unknown")
    original = deepcopy(checklist)

    backup_safeguards(checklist)

    assert checklist == original


@pytest.mark.parametrize(
    "backups,restore_testing,severity",
    [
        ("No", "Yes", "High"),
        ("Yes", "No", "High"),
        ("Unknown", "Yes", "Info"),
        ("No", "Unknown", "High"),
    ],
)
def test_yaml_rule_runs_through_engine(
    backups, restore_testing, severity
):
    rule = load_rule(ROOT / "rules" / "R16.yaml")

    finding = evaluate_checklist_rule(
        rule, make_checklist(backups, restore_testing)
    )

    assert finding is not None
    assert finding.observation.rule_id == "R16"
    assert finding.severity == severity
    assert finding.rule.kind == "checklist"
    assert finding.rule.review_status == "draft"


def test_both_yes_produce_no_engine_finding():
    rule = load_rule(ROOT / "rules" / "R16.yaml")

    assert evaluate_checklist_rule(
        rule, make_checklist("Yes", "Yes")
    ) is None


@pytest.mark.parametrize(
    "clinic,expected_evidence",
    [
        ("lakeview_dental", {"Q10": "Yes", "Q11": "No"}),
        ("southside_counseling", {"Q10": "No", "Q11": "Yes"}),
        ("westside_health", {"Q10": "Yes", "Q11": "No"}),
    ],
)
def test_matches_sample_checklists(clinic, expected_evidence):
    rule = load_rule(ROOT / "rules" / "R16.yaml")
    folder = ROOT / "samples" / clinic
    checklist = read_checklist(
        (folder / "checklist.json").read_bytes(),
        (folder / "followups.json").read_bytes(),
    )

    finding = evaluate_checklist_rule(rule, checklist)

    assert finding is not None
    assert finding.observation.status == "confirmed"
    assert dict(finding.observation.evidence) == expected_evidence