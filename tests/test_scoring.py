from fractions import Fraction

import pytest

from clinicshield.checklist_input import Checklist
from clinicshield.scoring import score_safeguards
from clinicshield.input_limits import InputError
from clinicshield.scoring import technical_risk_points
from clinicshield.scoring import ExposureFinding, score_exposure
from clinicshield.inventory import ScoringEntity
from clinicshield.scoring import evaluate_technical_finding
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

@pytest.mark.parametrize(
    "severity,expected",
    [
        ("Critical", 10),
        ("High", 6),
        ("Medium", 3),
        ("Low", 1),
        ("Info", 0),
    ],
)
def test_base_technical_risk_points(severity, expected):
    assert technical_risk_points(
        severity,
        touches_phi="N",
        internet_facing="N",
        medical_device=False,
    ) == expected


@pytest.mark.parametrize("phi", ["Y", "Unknown"])
def test_phi_multiplier(phi):
    assert technical_risk_points(
        "High",
        touches_phi=phi,
        internet_facing="N",
        medical_device=False,
    ) == 9


@pytest.mark.parametrize(
    "exposure,expected",
    [("Y", 9), ("N", 6), ("Unknown", 6)],
)
def test_only_confirmed_internet_exposure_gets_multiplier(
    exposure, expected
):
    assert technical_risk_points(
        "High",
        touches_phi="N",
        internet_facing=exposure,
        medical_device=False,
    ) == expected


def test_medical_device_multiplier():
    assert technical_risk_points(
        "High",
        touches_phi="N",
        internet_facing="N",
        medical_device=True,
    ) == Fraction(15, 2)


def test_all_multipliers_preserve_exact_precision():
    assert technical_risk_points(
        "Critical",
        touches_phi="Y",
        internet_facing="Y",
        medical_device=True,
    ) == Fraction(225, 8)


@pytest.mark.parametrize(
    "changes",
    [
        {"severity": "invalid"},
        {"touches_phi": None},
        {"internet_facing": "yes"},
        {"medical_device": 1},
    ],
)
def test_rejects_invalid_risk_inputs(changes):
    values = {
        "severity": "High",
        "touches_phi": "N",
        "internet_facing": "N",
        "medical_device": False,
    }
    values.update(changes)

    with pytest.raises(InputError):
        technical_risk_points(**values)

def test_exposure_without_findings():
    result = score_exposure(["device:1"], [])
    assert result.entity_count == 1
    assert result.adjusted_points == 0
    assert result.score == 100      


def test_exposure_caps_each_entity_separately():
    result = score_exposure(
        ["device:1", "device:2"],
        [
            ExposureFinding("device:1", "R01", Fraction(20)),
            ExposureFinding("device:1", "R02", Fraction(20)),
            ExposureFinding("device:2", "R01", Fraction(6)),
        ],
    )
    assert result.capped_entity_points == (
        ("device:1", Fraction(25)),
        ("device:2", Fraction(6)),
    )
    assert result.adjusted_points == 31
    assert result.score == 69


def test_duplicate_evidence_counts_once():
    finding = ExposureFinding("device:1", "R01", Fraction(6))
    result = score_exposure(["device:1"], [finding, finding])
    assert result.adjusted_points == 6
    assert result.score == 94


def test_conflicting_duplicates_require_review():
    with pytest.raises(InputError, match="conflicting"):
        score_exposure(
            ["device:1"],
            [
                ExposureFinding("device:1", "R01", Fraction(6)),
                ExposureFinding("device:1", "R01", Fraction(9)),
            ],
        )


@pytest.mark.parametrize(
    "count,expected",
    [(20, Fraction(10)), (21, Fraction(200, 21)), (40, Fraction(5))],
)
def test_exposure_size_adjustment(count, expected):
    entities = [f"device:{number}" for number in range(count)]
    result = score_exposure(
        entities,
        [ExposureFinding("device:0", "R01", Fraction(10))],
    )
    assert result.entity_count == count
    assert result.adjusted_points == expected
    assert result.score == 100 - expected


def test_exposure_score_cannot_be_negative():
    entities = [f"device:{number}" for number in range(5)]
    findings = [
        ExposureFinding(entity, "R01", Fraction(25))
        for entity in entities
    ]
    assert score_exposure(entities, findings).score == 0


@pytest.mark.parametrize(
    "entities", [[], ["device:1", "device:1"], [""], [None]]
)
def test_rejects_invalid_exposure_entities(entities):
    with pytest.raises(InputError):
        score_exposure(entities, [])


def test_rejects_unknown_finding_entity():
    with pytest.raises(InputError, match="unknown entity"):
        score_exposure(
            ["device:1"],
            [ExposureFinding("device:2", "R01", Fraction(6))],
        )


@pytest.mark.parametrize("points", [-1, 1.5, True])
def test_rejects_invalid_exposure_points(points):
    with pytest.raises(InputError, match="Risk points"):
        score_exposure(
            ["device:1"],
            [ExposureFinding("device:1", "R01", points)],
        )

def test_evaluates_known_device_conditions():
    entity = ScoringEntity(
        entity_id="device:1",
        kind="device",
        touches_phi="Y",
        internet_facing="Y",
        medical_device=True,
    )
    result = evaluate_technical_finding(entity, "R01", "Critical")

    assert result.finding.entity_id == "device:1"
    assert result.finding.finding_id == "R01"
    assert result.finding.risk_points == Fraction(225, 8)
    assert result.unknown_conditions == ()


def test_unmatched_host_preserves_unknown_conditions():
    entity = ScoringEntity(
        entity_id="unmatched:1",
        kind="unmatched",
        touches_phi="Unknown",
        internet_facing="Unknown",
        medical_device=None,
    )
    result = evaluate_technical_finding(entity, "R01", "High")

    assert result.finding.risk_points == 9
    assert result.unknown_conditions == (
        "touches_phi",
        "internet_facing",
        "medical_device",
    )


def test_evaluated_finding_connects_to_exposure_score():
    entity = ScoringEntity(
        entity_id="cloud:1",
        kind="cloud",
        touches_phi="N",
        internet_facing="Unknown",
        medical_device=False,
    )
    evaluated = evaluate_technical_finding(entity, "R01", "High")
    result = score_exposure([entity.entity_id], [evaluated.finding])

    assert result.score == 94
    assert evaluated.unknown_conditions == ("internet_facing",)


@pytest.mark.parametrize("finding_id", ["", "   ", None])
def test_evaluation_rejects_missing_finding_id(finding_id):
    entity = ScoringEntity("device:1", "device", "N", "N", False)

    with pytest.raises(InputError, match="nonempty IDs"):
        evaluate_technical_finding(entity, finding_id, "High")