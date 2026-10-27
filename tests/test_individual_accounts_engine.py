from pathlib import Path

import pytest

from clinicshield import rule_engine
from clinicshield.checklist_input import Checklist, read_checklist
from clinicshield.rule_engine import evaluate_checklist_rule
from clinicshield.rule_handlers import RuleObservation
from clinicshield.rule_loader import load_rule
from clinicshield.rule_models import RuleDefinition


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def rule():
    return load_rule(ROOT / "rules" / "R14.yaml")


def make_checklist(answer):
    return Checklist(answers={"Q06": answer}, followups={})


def change_rule(rule, **changes):
    data = rule.model_dump()
    data.update(changes)
    return RuleDefinition.model_validate(data)


def test_yaml_rule_produces_reported_gap(rule):
    finding = evaluate_checklist_rule(rule, make_checklist("No"))

    assert finding is not None
    assert finding.observation.rule_id == "R14"
    assert finding.observation.entity_id == "assessment"
    assert finding.observation.status == "confirmed"
    assert finding.severity == "High"
    assert finding.rule.kind == "checklist"
    assert finding.rule.review_status == "draft"
    assert finding.observation.evidence == (("Q06", "No"),)


def test_unknown_uses_unknown_severity(rule):
    finding = evaluate_checklist_rule(rule, make_checklist("Unknown"))

    assert finding is not None
    assert finding.observation.status == "needs_review"
    assert finding.severity == "Info"


def test_yes_does_not_trigger(rule):
    assert evaluate_checklist_rule(
        rule, make_checklist("Yes")
    ) is None


@pytest.mark.parametrize(
    "answer,expected",
    [("No", "Medium"), ("Unknown", "Low")],
)
def test_severity_comes_from_definition(rule, answer, expected):
    configured = change_rule(
        rule, severity="Medium", unknown_severity="Low"
    )

    finding = evaluate_checklist_rule(
        configured, make_checklist(answer)
    )

    assert finding is not None
    assert finding.severity == expected


@pytest.mark.parametrize(
    "changes",
    [
        {"rule_id": "R15"},
        {"handler": "unregistered_handler"},
        {"kind": "technical"},
    ],
)
def test_rejects_unregistered_combinations(rule, changes):
    configured = change_rule(rule, **changes)

    with pytest.raises(ValueError, match="registration"):
        evaluate_checklist_rule(configured, make_checklist("No"))


def test_rejects_missing_required_evidence(rule):
    configured = change_rule(
        rule, evidence_fields=("Q06", "missing_field")
    )

    with pytest.raises(ValueError, match="required evidence"):
        evaluate_checklist_rule(configured, make_checklist("No"))


def test_rejects_wrong_handler_rule_id(rule, monkeypatch):
    def incorrect_handler(checklist):
        return RuleObservation(
            rule_id="R15",
            entity_id="assessment",
            status="confirmed",
            evidence=(),
        )

    monkeypatch.setitem(
        rule_engine.CHECKLIST_HANDLERS,
        ("R14", "individual_accounts", "checklist"),
        incorrect_handler,
    )

    with pytest.raises(ValueError, match="different rule ID"):
        evaluate_checklist_rule(rule, make_checklist("No"))


@pytest.mark.parametrize(
    "clinic,should_trigger",
    [
        ("lakeview_dental", False),
        ("southside_counseling", False),
        ("westside_health", True),
    ],
)
def test_matches_sample_checklists(rule, clinic, should_trigger):
    folder = ROOT / "samples" / clinic
    checklist = read_checklist(
        (folder / "checklist.json").read_bytes(),
        (folder / "followups.json").read_bytes(),
    )

    finding = evaluate_checklist_rule(rule, checklist)

    if should_trigger:
        assert finding is not None
        assert finding.observation.status == "confirmed"
        assert finding.observation.evidence == (("Q06", "No"),)
    else:
        assert finding is None