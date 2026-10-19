from fractions import Fraction

import pytest

from clinicshield.checklist_input import Checklist
from clinicshield.scoring import score_safeguards


def checklist(answer="Yes", presence="Unknown", **changes):
    answers = {f"Q{number:02d}": answer for number in range(1, 26)}
    answers.update(changes)
    return Checklist(
        answers=answers,
        followups={"Q24a": answer, "Q24b": answer},
        medical_devices_present=presence,
    )


def test_all_yes_scores_100():
    result = score_safeguards(checklist())
    assert result.earned_weight == 47
    assert result.applicable_weight == 47
    assert result.score == 100
    assert result.excluded_questions == ()
    assert result.unknown_questions == ()


@pytest.mark.parametrize("answer", ["No", "Unknown"])
def test_no_or_unknown_earns_zero(answer):
    result = score_safeguards(checklist(answer))
    assert result.earned_weight == 0
    assert result.applicable_weight == 47
    assert result.score == 0


@pytest.mark.parametrize("answer", ["Yes", "No", "Unknown"])
def test_explicit_absence_excludes_q23(answer):
    result = score_safeguards(checklist(presence="No", Q23=answer))
    assert result.earned_weight == 46
    assert result.applicable_weight == 46
    assert result.score == 100
    assert result.excluded_questions == ("Q23",)
    assert "Q23" not in result.unknown_questions


@pytest.mark.parametrize("presence", ["Yes", "Unknown"])
def test_q23_remains_scored_without_explicit_absence(presence):
    result = score_safeguards(checklist(presence=presence, Q23="Unknown"))
    assert result.earned_weight == 46
    assert result.applicable_weight == 47
    assert result.score == Fraction(4600, 47)
    assert result.unknown_questions == ("Q23",)


@pytest.mark.parametrize(
    "question,weight",
    [
        ("Q01", 3), ("Q02", 3), ("Q03", 1), ("Q04", 1),
        ("Q05", 1), ("Q06", 3), ("Q07", 3), ("Q08", 3),
        ("Q09", 1), ("Q10", 3), ("Q11", 3), ("Q12", 1),
        ("Q13", 1), ("Q14", 1), ("Q15", 1), ("Q16", 1),
        ("Q17", 3), ("Q18", 1), ("Q19", 1), ("Q20", 3),
        ("Q21", 3), ("Q22", 1), ("Q23", 1), ("Q24", 1),
        ("Q25", 3),
    ],
)
def test_each_reviewed_question_weight(question, weight):
    result = score_safeguards(checklist(**{question: "No"}))
    assert result.earned_weight == 47 - weight
    assert result.applicable_weight == 47