from pathlib import Path

import pytest

from clinicshield.finding_groups import (
    FindingOccurrence,
    group_findings,
)
from clinicshield.input_limits import InputError
from clinicshield.rule_engine import RuleFinding
from clinicshield.rule_handlers import RuleObservation
from clinicshield.rule_loader import load_rule
from clinicshield.rule_models import RuleDefinition


ROOT = Path(__file__).resolve().parents[1]


def make_occurrence(
    *,
    rule_id="R12",
    entity_id="cloud:email",
    issue_key="email-mfa",
    category="administrative",
    basis="Same email service and MFA safeguard.",
    status="confirmed",
    severity=None,
    unknown_severity=None,
    evidence=(("source", "inventory"),),
):
    rule = load_rule(ROOT / "rules" / f"{rule_id}.yaml")
    data = rule.model_dump()
    if severity is not None:
        data["severity"] = severity
    if unknown_severity is not None:
        data["unknown_severity"] = unknown_severity
    rule = RuleDefinition.model_validate(data)

    return FindingOccurrence(
        finding=RuleFinding(
            rule=rule,
            observation=RuleObservation(
                rule_id=rule_id,
                entity_id="software:1",
                status=status,
                evidence=evidence,
            ),
        ),
        scoring_entity_id=entity_id,
        issue_key=issue_key,
        scoring_category=category,
        grouping_basis=basis,
    )


def test_same_issue_groups_without_losing_sources():
    inventory = make_occurrence(
        evidence=(("mfa_enabled", "N"), ("source", "inventory")),
    )
    checklist = make_occurrence(
        evidence=(("Q01", "No"), ("source", "checklist")),
    )

    groups = group_findings((inventory, checklist))

    assert len(groups) == 1
    assert groups[0].occurrences == (inventory, checklist)
    assert groups[0].severity == "High"
    assert groups[0].has_confirmed_gap
    assert groups[0].scoring_category == "administrative"


def test_identical_occurrences_do_not_create_extra_groups():
    item = make_occurrence()

    groups = group_findings((item, item))

    assert len(groups) == 1
    assert len(groups[0].occurrences) == 2
    assert groups[0].severity == "High"


def test_same_fix_does_not_merge_distinct_risks():
    exposure = make_occurrence(
        rule_id="R06",
        entity_id="device:1",
        issue_key="remote-admin-exposure",
        category="technical",
        basis="Internet exposure is a distinct risk.",
    )
    telnet = make_occurrence(
        rule_id="R09",
        entity_id="device:1",
        issue_key="telnet-service",
        category="technical",
        basis="Telnet is a distinct service risk.",
    )

    assert len(group_findings((exposure, telnet))) == 2


def test_same_issue_on_different_entities_stays_separate():
    first = make_occurrence(entity_id="cloud:first")
    second = make_occurrence(entity_id="cloud:second")

    assert len(group_findings((first, second))) == 2


def test_group_uses_highest_confirmed_severity():
    high = make_occurrence(severity="High")
    critical = make_occurrence(severity="Critical")

    group = group_findings((high, critical))[0]

    assert group.severity == "Critical"
    assert group.has_confirmed_gap


def test_unknown_evidence_cannot_raise_confirmed_severity():
    confirmed = make_occurrence(severity="Medium")
    unknown = make_occurrence(
        status="needs_review",
        unknown_severity="Critical",
    )

    group = group_findings((confirmed, unknown))[0]

    assert group.severity == "Medium"
    assert len(group.occurrences) == 2


def test_unknown_only_group_is_info_even_if_metadata_is_higher():
    unknown = make_occurrence(
        status="needs_review",
        unknown_severity="High",
    )

    group = group_findings((unknown,))[0]

    assert group.severity == "Info"
    assert not group.has_confirmed_gap


def test_conflicting_categories_for_same_issue_are_rejected():
    administrative = make_occurrence(category="administrative")
    technical = make_occurrence(category="technical")

    with pytest.raises(InputError, match="conflicting scoring categories"):
        group_findings((administrative, technical))


@pytest.mark.parametrize(
    "changes",
    [
        {"entity_id": ""},
        {"entity_id": "   "},
        {"issue_key": ""},
        {"issue_key": None},
        {"basis": ""},
        {"basis": "   "},
    ],
)
def test_requires_explicit_group_identity_and_rationale(changes):
    item = make_occurrence(**changes)

    with pytest.raises(InputError, match="explicit identifiers and basis"):
        group_findings((item,))


def test_rejects_unknown_scoring_category():
    with pytest.raises(InputError, match="scoring category"):
        group_findings((make_occurrence(category="other"),))


def test_rejects_mismatched_rule_and_observation():
    item = make_occurrence()
    malformed = FindingOccurrence(
        finding=RuleFinding(
            rule=item.finding.rule,
            observation=RuleObservation(
                rule_id="R13",
                entity_id="software:1",
                status="confirmed",
                evidence=(),
            ),
        ),
        scoring_entity_id=item.scoring_entity_id,
        issue_key=item.issue_key,
        scoring_category=item.scoring_category,
        grouping_basis=item.grouping_basis,
    )

    with pytest.raises(InputError, match="IDs must match"):
        group_findings((malformed,))


def test_groups_have_deterministic_order():
    later = make_occurrence(entity_id="cloud:z")
    earlier = make_occurrence(entity_id="cloud:a")

    first = group_findings((later, earlier))
    second = group_findings((earlier, later))

    assert [
        (g.scoring_entity_id, g.issue_key) for g in first
    ] == [
        (g.scoring_entity_id, g.issue_key) for g in second
    ]


def test_empty_input_produces_no_groups():
    assert group_findings(()) == ()


def test_grouping_preserves_input_metadata():
    item = make_occurrence()
    original = item.finding.rule.model_dump()

    group = group_findings((item,))[0]

    assert item.finding.rule.model_dump() == original
    assert group.occurrences[0].grouping_basis == item.grouping_basis
    assert group.occurrences[0].finding is item.finding