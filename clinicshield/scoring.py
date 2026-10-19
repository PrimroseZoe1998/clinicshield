from dataclasses import dataclass
from fractions import Fraction

from clinicshield.checklist_input import ANSWERS, QUESTION_IDS, Checklist
from clinicshield.input_limits import InputError


ESSENTIAL_QUESTIONS = {
    "Q01", "Q02", "Q06", "Q07", "Q08", "Q10",
    "Q11", "Q17", "Q20", "Q21", "Q25",
}


@dataclass(frozen=True)
class SafeguardsScore:
    earned_weight: int
    applicable_weight: int
    excluded_questions: tuple[str, ...]
    unknown_questions: tuple[str, ...]

    @property
    def score(self) -> Fraction:
        return Fraction(100 * self.earned_weight, self.applicable_weight)


def score_safeguards(checklist: Checklist) -> SafeguardsScore:
    if set(checklist.answers) != QUESTION_IDS:
        raise InputError("Scoring requires all 25 checklist answers.")

    for answer in checklist.answers.values():
        if not isinstance(answer, str) or answer not in ANSWERS:
            raise InputError("Checklist answers must be Yes, No, or Unknown.")

    presence = checklist.medical_devices_present
    if not isinstance(presence, str) or presence not in ANSWERS:
        raise InputError(
            "Medical device presence must be Yes, No, or Unknown."
        )

    earned = 0
    total = 0
    excluded = []
    unknown = []

    for question in sorted(QUESTION_IDS):
        if question == "Q23" and not checklist.q23_applicable:
            excluded.append(question)
            continue

        weight = 3 if question in ESSENTIAL_QUESTIONS else 1
        total += weight
        answer = checklist.answers[question]

        if answer == "Yes":
            earned += weight
        elif answer == "Unknown":
            unknown.append(question)

    return SafeguardsScore(
        earned_weight=earned,
        applicable_weight=total,
        excluded_questions=tuple(excluded),
        unknown_questions=tuple(unknown),
    )

SEVERITY_POINTS = {
    "Critical": 10,
    "High": 6,
    "Medium": 3,
    "Low": 1,
    "Info": 0,
}


def technical_risk_points(
    severity: str,
    *,
    touches_phi: str,
    internet_facing: str,
    medical_device: bool,
) -> Fraction:
    if not isinstance(severity, str) or severity not in SEVERITY_POINTS:
        raise InputError("Choose a supported finding severity.")

    for value in (touches_phi, internet_facing):
        if not isinstance(value, str) or value not in {"Y", "N", "Unknown"}:
            raise InputError("Asset conditions must be Y, N, or Unknown.")

    if type(medical_device) is not bool:
        raise InputError("Medical device status must be a boolean.")

    points = Fraction(SEVERITY_POINTS[severity])

    if touches_phi in {"Y", "Unknown"}:
        points *= Fraction(3, 2)

    if internet_facing == "Y":
        points *= Fraction(3, 2)

    if medical_device:
        points *= Fraction(5, 4)

    return points