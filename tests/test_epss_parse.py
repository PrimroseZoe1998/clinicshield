from datetime import date
from decimal import Decimal

import pytest

from clinicshield import epss_parse
from clinicshield.epss_parse import parse_epss_csv


METADATA = "#model_version:v2026.06.15,score_date:2026-10-26\n"
HEADER = "cve,epss,percentile\n"
ROW = "CVE-2026-12345,0.123456789,0.987654321\n"


def test_parses_scores_and_metadata():
    dataset = parse_epss_csv(METADATA + HEADER + ROW)

    assert dataset.model_version == "v2026.06.15"
    assert dataset.score_date == date(2026, 10, 26)
    assert len(dataset.records) == 1
    record = dataset.records[0]
    assert record.cve == "CVE-2026-12345"
    assert record.epss == Decimal("0.123456789")
    assert record.percentile == Decimal("0.987654321")
    assert record.score_date == dataset.score_date


def test_accepts_multiple_records():
    text = METADATA + HEADER + ROW
    text += "CVE-2026-67890,0,1\n"

    assert len(parse_epss_csv(text).records) == 2


def test_accepts_windows_line_endings():
    text = (METADATA + HEADER + ROW).replace("\n", "\r\n")

    assert len(parse_epss_csv(text).records) == 1


@pytest.mark.parametrize(
    "metadata",
    [
        "",
        "model_version:v1,score_date:2026-10-26\n",
        "#score_date:2026-10-26\n",
        "#model_version:v1\n",
        "#model_version:,score_date:2026-10-26\n",
        "#model_version:v1,score_date:\n",
        "#model_version:v1,model_version:v2,score_date:2026-10-26\n",
        "#model_version:v1,score_date:2026-10-26,broken\n",
    ],
)
def test_rejects_invalid_metadata(metadata):
    with pytest.raises(ValueError):
        parse_epss_csv(metadata + HEADER + ROW)


@pytest.mark.parametrize(
    "score_date",
    ["2026-02-30", "20261026", "not-a-date"],
)
def test_rejects_invalid_score_date(score_date):
    metadata = f"#model_version:v1,score_date:{score_date}\n"

    with pytest.raises(ValueError):
        parse_epss_csv(metadata + HEADER + ROW)


@pytest.mark.parametrize(
    "header",
    [
        "",
        "cve,percentile,epss\n",
        "cve,epss\n",
        "cve,epss,percentile,extra\n",
    ],
)
def test_rejects_unexpected_columns(header):
    with pytest.raises(ValueError):
        parse_epss_csv(METADATA + header + ROW)


@pytest.mark.parametrize(
    "row",
    [
        "CVE-2026-12345,0.1\n",
        "CVE-2026-12345,0.1,0.9,extra\n",
        "invalid,0.1,0.9\n",
        "CVE-2026-12345,-0.1,0.9\n",
        "CVE-2026-12345,0.1,1.1\n",
        "CVE-2026-12345,NaN,0.9\n",
        "\n",
    ],
)
def test_rejects_invalid_rows(row):
    with pytest.raises(ValueError):
        parse_epss_csv(METADATA + HEADER + row)


def test_rejects_duplicate_cves():
    with pytest.raises(ValueError, match="Duplicate"):
        parse_epss_csv(METADATA + HEADER + ROW + ROW)


def test_rejects_empty_dataset():
    with pytest.raises(ValueError, match="no score records"):
        parse_epss_csv(METADATA + HEADER)


def test_rejects_malformed_csv():
    with pytest.raises(ValueError, match="Malformed"):
        parse_epss_csv(METADATA + HEADER + '"unterminated')


def test_accepts_exact_character_limit(monkeypatch):
    text = METADATA + HEADER + ROW
    monkeypatch.setattr(epss_parse, "MAX_CSV_CHARACTERS", len(text))

    assert len(parse_epss_csv(text).records) == 1


def test_rejects_oversized_text(monkeypatch):
    text = METADATA + HEADER + ROW
    monkeypatch.setattr(epss_parse, "MAX_CSV_CHARACTERS", len(text) - 1)

    with pytest.raises(ValueError, match="size limit"):
        parse_epss_csv(text)


def test_accepts_exact_record_limit(monkeypatch):
    monkeypatch.setattr(epss_parse, "MAX_RECORDS", 1)

    assert len(parse_epss_csv(METADATA + HEADER + ROW).records) == 1


def test_rejects_excess_records(monkeypatch):
    monkeypatch.setattr(epss_parse, "MAX_RECORDS", 1)
    text = METADATA + HEADER + ROW
    text += "CVE-2026-67890,0.1,0.9\n"

    with pytest.raises(ValueError, match="record limit"):
        parse_epss_csv(text)