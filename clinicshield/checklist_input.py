import json
from dataclasses import dataclass

from clinicshield.ingest import InputError


ANSWERS = {"Yes", "No", "Unknown"}
QUESTION_IDS = {f"Q{number:02d}" for number in range(1, 26)}
FOLLOWUP_IDS = {"Q24a", "Q24b"}


@dataclass
class Checklist:
    answers: dict[str, str]
    followups: dict[str, str]


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError("JSON keys must be unique.")
        result[key] = value
    return result


def read_answers(data: bytes, expected_keys: set[str]) -> dict[str, str]:
    if not isinstance(data, bytes):
        raise InputError("Provide checklist JSON data as bytes.")

    try:
        text = data.decode("utf-8-sig")
        values = json.loads(text, object_pairs_hook=unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError):
        raise InputError("Provide valid UTF-8 checklist JSON.") from None

    if not isinstance(values, dict):
        raise InputError("Checklist JSON must contain an object.")

    if set(values) != expected_keys:
        raise InputError(
            "Checklist JSON must contain exactly the required question IDs."
        )

    cleaned = {}
    for key, value in values.items():
        if not isinstance(value, str) or value.strip() not in ANSWERS:
            raise InputError(
                "Checklist answers must be Yes, No, or Unknown."
            )
        cleaned[key] = value.strip()

    return cleaned


def derive_q24(followups: dict[str, str]) -> str:
    if "No" in followups.values():
        return "No"
    if all(value == "Yes" for value in followups.values()):
        return "Yes"
    return "Unknown"


def read_checklist(
    data: bytes,
    followup_data: bytes | None = None,
) -> Checklist:
    """Validate checklist answers without logging uploaded content."""
    answers = read_answers(data, QUESTION_IDS)

    if followup_data is None:
        raise InputError(
            "Provide Q24a and Q24b follow-up answers. "
            "They cannot be inferred from the combined Q24 answer."
        )

    followups = read_answers(followup_data, FOLLOWUP_IDS)
    combined = derive_q24(followups)

    if answers["Q24"] != combined:
        raise InputError(
            "Q24 conflicts with its follow-up answers. "
            "Use Yes when both are Yes, No when either is No, "
            "and Unknown otherwise."
        )

    return Checklist(answers=answers, followups=followups)