from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from clinicshield.epss_models import EpssRecord


@pytest.fixture
def record_data():
    return {
        "cve": "CVE-2026-12345",
        "epss": "0.123456789",
        "percentile": "0.987654321",
        "score_date": "2026-10-26",
    }


def test_preserves_scores_and_publication_date(record_data):
    record = EpssRecord(**record_data)

    assert record.cve == "CVE-2026-12345"
    assert record.epss == Decimal("0.123456789")
    assert record.percentile == Decimal("0.987654321")
    assert record.score_date == date(2026, 10, 26)


@pytest.mark.parametrize("field", ["epss", "percentile"])
@pytest.mark.parametrize("value", ["0", "1"])
def test_accepts_score_boundaries(record_data, field, value):
    record_data[field] = value

    assert getattr(EpssRecord(**record_data), field) == Decimal(value)


@pytest.mark.parametrize("field", ["epss", "percentile"])
@pytest.mark.parametrize(
    "value",
    ["-0.0001", "1.0001", "NaN", "Infinity", "-Infinity", "invalid"],
)
def test_rejects_invalid_scores(record_data, field, value):
    record_data[field] = value

    with pytest.raises(ValidationError):
        EpssRecord(**record_data)


@pytest.mark.parametrize("field", ["epss", "percentile"])
@pytest.mark.parametrize("value", [True, False])
def test_rejects_boolean_scores(record_data, field, value):
    record_data[field] = value

    with pytest.raises(ValidationError):
        EpssRecord(**record_data)


@pytest.mark.parametrize(
    "cve",
    ["", "CVE-2026-123", "cve-2026-12345", "OTHER-2026-12345"],
)
def test_rejects_invalid_cve_identifiers(record_data, cve):
    record_data["cve"] = cve

    with pytest.raises(ValidationError):
        EpssRecord(**record_data)


@pytest.mark.parametrize(
    "value",
    ["2026-02-30", "not-a-date"],
)
def test_rejects_invalid_publication_date(record_data, value):
    record_data["score_date"] = value

    with pytest.raises(ValidationError):
        EpssRecord(**record_data)


@pytest.mark.parametrize(
    "field",
    ["cve", "epss", "percentile", "score_date"],
)
def test_requires_all_fields(record_data, field):
    del record_data[field]

    with pytest.raises(ValidationError):
        EpssRecord(**record_data)


def test_rejects_unexpected_fields(record_data):
    record_data["unexpected"] = "value"

    with pytest.raises(ValidationError):
        EpssRecord(**record_data)


def test_json_round_trip_preserves_record(record_data):
    record = EpssRecord(**record_data)

    restored = EpssRecord.model_validate_json(record.model_dump_json())

    assert restored == record


def test_record_is_frozen(record_data):
    record = EpssRecord(**record_data)

    with pytest.raises(ValidationError):
        record.epss = Decimal("0")