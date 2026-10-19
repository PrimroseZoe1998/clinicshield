import json
from pathlib import Path

import pytest

from clinicshield.checklist_input import read_checklist
from clinicshield.ingest import InputError


SAMPLES = Path(__file__).resolve().parents[1] / "samples"


def json_bytes(value):
    return json.dumps(value).encode("utf-8")


def answers(q24="Yes"):
    values = {f"Q{number:02d}": "Yes" for number in range(1, 26)}
    values["Q24"] = q24
    return values


def followups(first="Yes", second="Yes"):
    return {"Q24a": first, "Q24b": second}


@pytest.mark.parametrize(
    "clinic,expected",
    [
        ("lakeview_dental", "Yes"),
        ("southside_counseling", "No"),
        ("westside_health", "Yes"),
    ],
)
def test_sample_checklists(clinic, expected):
    folder = SAMPLES / clinic
    result = read_checklist(
        (folder / "checklist.json").read_bytes(),
        (folder / "followups.json").read_bytes(),
    )
    assert len(result.answers) == 25
    assert result.answers["Q24"] == expected


@pytest.mark.parametrize(
    "first,second,expected",
    [
        ("Yes", "Yes", "Yes"),
        ("Yes", "No", "No"),
        ("Yes", "Unknown", "Unknown"),
        ("No", "Yes", "No"),
        ("No", "No", "No"),
        ("No", "Unknown", "No"),
        ("Unknown", "Yes", "Unknown"),
        ("Unknown", "No", "No"),
        ("Unknown", "Unknown", "Unknown"),
    ],
)
def test_q24_combinations(first, second, expected):
    result = read_checklist(
        json_bytes(answers(expected)),
        json_bytes(followups(first, second)),
    )
    assert result.answers["Q24"] == expected
    assert len(result.answers) == 25
    assert len(result.followups) == 2


def test_trims_answers_and_accepts_utf8_bom():
    values = answers()
    values["Q01"] = " Unknown "
    result = read_checklist(
        b"\xef\xbb\xbf" + json_bytes(values),
        json_bytes(followups(" Yes ", "Yes")),
    )
    assert result.answers["Q01"] == "Unknown"
    assert result.followups["Q24a"] == "Yes"


def test_requires_missing_followups():
    with pytest.raises(InputError, match="cannot be inferred"):
        read_checklist(json_bytes(answers("No")))


@pytest.mark.parametrize("change", ["missing", "extra", "wrong_id"])
def test_rejects_invalid_question_ids(change):
    values = answers()
    if change == "missing":
        del values["Q01"]
    elif change == "extra":
        values["Q26"] = "Yes"
    else:
        values["Q1"] = values.pop("Q01")

    with pytest.raises(InputError, match="required question IDs"):
        read_checklist(json_bytes(values), json_bytes(followups()))


@pytest.mark.parametrize(
    "values",
    [
        {"Q24a": "Yes"},
        {"Q24a": "Yes", "Q24b": "Yes", "extra": "Yes"},
        {"Q24A": "Yes", "Q24b": "Yes"},
    ],
)
def test_rejects_invalid_followup_ids(values):
    with pytest.raises(InputError, match="required question IDs"):
        read_checklist(json_bytes(answers()), json_bytes(values))


@pytest.mark.parametrize(
    "value",
    ["yes", "Y", "NA", "", None, True, 1, [], {}],
)
def test_rejects_invalid_answers(value):
    values = answers()
    values["Q01"] = value
    with pytest.raises(InputError, match="Yes, No, or Unknown"):
        read_checklist(json_bytes(values), json_bytes(followups()))


def test_rejects_invalid_followup_answer_safely():
    with pytest.raises(InputError) as error:
        read_checklist(
            json_bytes(answers()),
            json_bytes(followups("PRIVATE_SENTINEL", "Yes")),
        )
    assert "PRIVATE_SENTINEL" not in str(error.value)


@pytest.mark.parametrize("value", [[], "text", 42, None])
def test_rejects_non_object_json(value):
    with pytest.raises(InputError, match="contain an object"):
        read_checklist(json_bytes(value), json_bytes(followups()))


@pytest.mark.parametrize("data", [b"", b"{", b"\xff"])
def test_rejects_invalid_json(data):
    with pytest.raises(InputError, match="valid UTF-8"):
        read_checklist(data, json_bytes(followups()))


def test_rejects_duplicate_checklist_keys():
    data = json_bytes(answers())
    data = data[:-1] + b', "Q01": "No"}'
    with pytest.raises(InputError, match="keys must be unique"):
        read_checklist(data, json_bytes(followups()))


def test_rejects_duplicate_followup_keys():
    data = b'{"Q24a":"Yes","Q24a":"No","Q24b":"Yes"}'
    with pytest.raises(InputError, match="keys must be unique"):
        read_checklist(json_bytes(answers()), data)


@pytest.mark.parametrize("target", ["checklist", "followups"])
def test_rejects_non_bytes_input(target):
    data = json_bytes(answers())
    extra = json_bytes(followups())
    if target == "checklist":
        data = "text"
    else:
        extra = "text"

    with pytest.raises(InputError, match="as bytes"):
        read_checklist(data, extra)

@pytest.mark.parametrize(
    "presence,expected",
    [("Yes", True), ("No", False), ("Unknown", True)],
)
def test_q23_applicability(presence, expected):
    result = read_checklist(
        json_bytes(answers()),
        json_bytes(followups()),
        medical_devices_present=presence,
    )
    assert result.q23_applicable is expected
    assert result.medical_devices_present == presence
    assert len(result.answers) == 25


def test_q23_defaults_to_applicable():
    result = read_checklist(
        json_bytes(answers()),
        json_bytes(followups()),
    )
    assert result.medical_devices_present == "Unknown"
    assert result.q23_applicable is True


@pytest.mark.parametrize(
    "presence", [None, False, 0, [], {}, "no", " No ", "invalid"]
)
def test_rejects_invalid_medical_device_presence(presence):
    with pytest.raises(InputError, match="Medical device presence"):
        read_checklist(
            json_bytes(answers()),
            json_bytes(followups()),
            medical_devices_present=presence,
        ) 