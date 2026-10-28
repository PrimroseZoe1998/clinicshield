from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from clinicshield.checklist_input import Checklist, QUESTION_IDS
from clinicshield.finding_groups import FindingOccurrence, group_findings
from clinicshield.grouped_scoring import score_finding_groups
from clinicshield.input_limits import InputError
from clinicshield.inventory import ScoringEntity
from clinicshield.rule_engine import RuleFinding
from clinicshield.rule_handlers import RuleObservation
from clinicshield.rule_loader import load_rule
from clinicshield.scoring import combine_scores, score_safeguards


ROOT = Path(__file__).resolve().parents[1]


def make_entity(**changes):
    data = {
        "entity_id": "device:1",
        "kind": "device",
        "touches_phi": "N",
        "internet_facing": "N",
        "medical_device": False,
    }
    data.update(changes)
    return ScoringEntity(**data)


def make_occurrence(
    *,
    rule_id="R05",
    entity_id="device:1",
    issue_key="encryption",
    category="technical",
    status="confirmed",
    source="inventory",
):
    return FindingOccurrence(
        finding=RuleFinding(
            rule=load_rule(ROOT / "rules" / f"{rule_id}.yaml"),
            observation=RuleObservation(
                rule_id=rule_id,
                entity_id="source-entry:1",
                status=status,
                evidence=(("source", source),),
            ),
        ),
        scoring_entity_id=entity_id,
        issue_key=issue_key,
        scoring_category=category,
        grouping_basis="Explicit same-risk association for this test.",
    )


def score(*occurrences, entities=None):
    if entities is None:
        entities = (make_entity(),)
    return score_finding_groups(
        entities, group_findings(tuple(occurrences))
    )


def test_high_technical_group_contributes_once():
    result = score(make_occurrence())

    assert result.exposure.adjusted_points == Fraction(6)
    assert result.exposure.score == Fraction(94)
    assert len(result.technical_findings) == 1


def test_duplicate_evidence_cannot_inflate_exposure():
    first = make_occurrence(source="inventory")
    second = make_occurrence(source="administrator observation")

    single = score(first)
    combined = score(first, second)

    assert combined.exposure == single.exposure
    assert len(combined.technical_findings) == 1


def test_distinct_risks_are_not_collapsed():
    result = score(
        make_occurrence(issue_key="encryption"),
        make_occurrence(
            rule_id="R09",
            issue_key="telnet",
        ),
    )

    assert len(result.technical_findings) == 2
    assert result.exposure.adjusted_points == Fraction(12)
    assert result.exposure.score == Fraction(88)


def test_same_group_uses_highest_severity_without_summing():
    result = score(
        make_occurrence(rule_id="R02", issue_key="same-cve"),
        make_occurrence(rule_id="R01", issue_key="same-cve"),
    )

    assert len(result.technical_findings) == 1
    assert result.exposure.adjusted_points == Fraction(10)
    assert len(result.critical_findings) == 1


def test_unresolved_group_adds_no_exposure_or_critical_ceiling():
    result = score(make_occurrence(
        rule_id="R01", status="needs_review"
    ))

    assert result.exposure.score == Fraction(100)
    assert result.technical_findings == ()
    assert result.critical_findings == ()
    assert len(result.review_groups) == 1


def test_mixed_group_preserves_review_without_extra_points():
    result = score(
        make_occurrence(status="confirmed"),
        make_occurrence(
            status="needs_review",
            source="unresolved observation",
        ),
    )

    assert result.exposure.adjusted_points == Fraction(6)
    assert len(result.review_groups) == 1
    assert len(result.review_groups[0].occurrences) == 2


def test_administrative_group_does_not_add_exposure():
    result = score(make_occurrence(
        rule_id="R14",
        entity_id="assessment",
        issue_key="individual-accounts",
        category="administrative",
    ))

    assert result.exposure.score == Fraction(100)
    assert result.technical_findings == ()
    assert len(result.administrative_groups) == 1


def test_administrative_review_remains_visible():
    result = score(make_occurrence(
        rule_id="R14",
        entity_id="assessment",
        issue_key="individual-accounts",
        category="administrative",
        status="needs_review",
    ))

    assert result.exposure.score == Fraction(100)
    assert len(result.administrative_groups) == 1
    assert len(result.review_groups) == 1


def test_existing_asset_multipliers_still_apply():
    result = score(
        make_occurrence(),
        entities=(make_entity(touches_phi="Y"),),
    )

    assert result.exposure.adjusted_points == Fraction(9)


def test_unknown_asset_conditions_remain_explicit():
    result = score(
        make_occurrence(),
        entities=(make_entity(
            touches_phi="Unknown",
            internet_facing="Unknown",
            medical_device=None,
        ),),
    )

    assert set(
        result.technical_findings[0].unknown_conditions
    ) == {"touches_phi", "internet_facing", "medical_device"}


def test_critical_group_reaches_combined_score_ceiling():
    result = score(make_occurrence(
        rule_id="R01", issue_key="CVE-2026-12345"
    ))
    checklist = Checklist(
        answers={question: "Yes" for question in QUESTION_IDS},
        followups={"Q24a": "Yes", "Q24b": "Yes"},
    )

    combined = combine_scores(
        score_safeguards(checklist),
        result.exposure,
        open_critical_findings=result.critical_findings,
    )

    assert combined.critical_ceiling == 69
    assert combined.final_score == 69


def test_duplicate_groups_are_rejected_before_scoring():
    group = group_findings((make_occurrence(),))[0]

    with pytest.raises(InputError, match="Duplicate finding groups"):
        score_finding_groups(
            (make_entity(),), (group, group)
        )


def test_conflicting_group_identity_is_rejected():
    group = group_findings((make_occurrence(),))[0]
    inconsistent = replace(group, issue_key="different-risk")

    with pytest.raises(InputError, match="identity is inconsistent"):
        score_finding_groups((make_entity(),), (inconsistent,))


def test_unknown_technical_entity_is_rejected():
    with pytest.raises(InputError, match="unknown entity"):
        score(make_occurrence(entity_id="device:missing"))


def test_duplicate_scoring_entities_are_rejected():
    entity = make_entity()

    with pytest.raises(InputError, match="must be unique"):
        score_finding_groups((entity, entity), ())


def test_no_findings_preserves_inventory_entity_count():
    result = score(
        entities=(
            make_entity(),
            make_entity(entity_id="device:2"),
        )
    )

    assert result.exposure.entity_count == 2
    assert result.exposure.score == Fraction(100)
    assert result.critical_findings == ()