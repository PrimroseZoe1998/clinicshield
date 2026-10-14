import csv
import io
from pathlib import Path

import pytest

from clinicshield.ingest import InputError, read_csv


SAMPLES = Path(__file__).resolve().parents[1] / "samples"


def make_csv(headers, rows):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(headers)
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


SERVICE_HEADERS = [
    "asset_id", "port", "protocol", "service", "exposure"
]
SERVICE_ROW = ["TEST-01", "8080", "tcp", "http", "internal"]


@pytest.mark.parametrize(
    "clinic,kind,count",
    [
        ("lakeview_dental", "assets", 11),
        ("southside_counseling", "assets", 9),
        ("westside_health", "assets", 35),
        ("lakeview_dental", "software", 4),
        ("southside_counseling", "software", 5),
        ("westside_health", "software", 5),
        ("lakeview_dental", "services", 3),
        ("westside_health", "services", 3),
    ],
)
def test_sample_csv_files(clinic, kind, count):
    data = (SAMPLES / clinic / f"{kind}.csv").read_bytes()
    assert len(read_csv(data, kind)) == count


def test_accepts_utf8_bom_and_trimmed_headers():
    headers = [f" {name} " for name in SERVICE_HEADERS]
    data = b"\xef\xbb\xbf" + make_csv(headers, [SERVICE_ROW])
    records = read_csv(data, "services")
    assert records[0].port == 8080


def test_accepts_quoted_commas_and_newlines():
    data = make_csv(
        SERVICE_HEADERS + ["product"],
        [SERVICE_ROW + ["Example, server\nsecond line"]],
    )
    records = read_csv(data, "services")
    assert records[0].product == "Example, server\nsecond line"


def test_skips_blank_records():
    data = make_csv(
        SERVICE_HEADERS,
        [[""] * len(SERVICE_HEADERS), SERVICE_ROW],
    )
    assert len(read_csv(data, "services")) == 1


@pytest.mark.parametrize(
    "data",
    [
        b"",
        make_csv(SERVICE_HEADERS, []),
        make_csv(SERVICE_HEADERS, [[""] * len(SERVICE_HEADERS)]),
    ],
)
def test_rejects_empty_input(data):
    with pytest.raises(InputError):
        read_csv(data, "services")


def test_rejects_non_utf8_input():
    with pytest.raises(InputError):
        read_csv(b"\xff\xfe", "services")


@pytest.mark.parametrize("kind", ["unknown", "Assets"])
def test_rejects_unknown_input_kind(kind):
    with pytest.raises(InputError):
        read_csv(b"", kind)


def test_rejects_non_bytes_input():
    with pytest.raises(InputError):
        read_csv("text", "services")


@pytest.mark.parametrize(
    "headers",
    [
        SERVICE_HEADERS + ["port"],
        SERVICE_HEADERS + [""],
        SERVICE_HEADERS + ["unexpected_column"],
        SERVICE_HEADERS[:-1],
    ],
)
def test_rejects_invalid_headers(headers):
    with pytest.raises(InputError):
        read_csv(make_csv(headers, []), "services")


def test_rejects_personal_information_headers():
    data = make_csv(
        SERVICE_HEADERS + ["patient_name"],
        [SERVICE_ROW + ["PRIVATE_SENTINEL"]],
    )
    with pytest.raises(InputError) as error:
        read_csv(data, "services")
    assert "personal information" in str(error.value)
    assert "PRIVATE_SENTINEL" not in str(error.value)


@pytest.mark.parametrize(
    "row",
    [SERVICE_ROW[:-1], SERVICE_ROW + ["extra"]],
)
def test_rejects_wrong_number_of_values(row):
    with pytest.raises(InputError, match="wrong number of values"):
        read_csv(make_csv(SERVICE_HEADERS, [row]), "services")


def test_validation_error_does_not_expose_values():
    row = SERVICE_ROW.copy()
    row[1] = "PRIVATE_SENTINEL"
    with pytest.raises(InputError) as error:
        read_csv(make_csv(SERVICE_HEADERS, [row]), "services")
    assert "invalid fields" in str(error.value)
    assert "PRIVATE_SENTINEL" not in str(error.value)


def test_rejects_unclosed_csv_quote():
    data = (
        ",".join(SERVICE_HEADERS)
        + '\n"TEST-01,8080,tcp,http,internal'
    ).encode("utf-8")
    with pytest.raises(InputError, match="formatting"):
        read_csv(data, "services")


def test_rejects_duplicate_asset_ids():
    data = (SAMPLES / "lakeview_dental" / "assets.csv").read_bytes()
    reader = csv.reader(io.StringIO(data.decode("utf-8-sig")))
    headers = next(reader)
    row = next(reader)
    duplicate_data = make_csv(headers, [row, row])
    with pytest.raises(InputError, match="Asset IDs must be unique"):
        read_csv(duplicate_data, "assets")