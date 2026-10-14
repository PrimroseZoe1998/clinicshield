import csv
import io
from pathlib import Path

import pytest
from openpyxl import load_workbook

from clinicshield.headers import map_headers
from clinicshield.ingest import read_csv
from clinicshield.input_limits import InputError
from clinicshield.workbook import read_workbook


PROJECT = Path(__file__).resolve().parents[1]
TEMPLATE = PROJECT / "templates" / "clinicshield_inventory.xlsx"


@pytest.mark.parametrize(
    "kind,header,expected",
    [
        ("assets", "Device", "asset_name"),
        ("assets", "Computer name", "asset_name"),
        ("software", "Software vendor", "vendor"),
        ("software", "Software name", "product"),
        ("software", "Software version", "version"),
        ("software", "Device ID", "asset_id"),
        ("services", "Device ID", "asset_id"),
        ("services", "Port number", "port"),
        ("services", "Transport", "protocol"),
        ("services", "Service name", "service"),
    ],
)
def test_supported_aliases(kind, header, expected):
    assert map_headers([header], kind) == [expected]


def test_normalizes_case_spaces_and_hyphens():
    assert map_headers(
        [" ASSET-ID ", " Port   Number ", "SERVICE-NAME"],
        "services",
    ) == ["asset_id", "port", "service"]


@pytest.mark.parametrize(
    "headers",
    [
        ["port", "Port number"],
        ["Device ID", "asset_id"],
        ["service", " SERVICE "],
    ],
)
def test_rejects_colliding_headers(headers):
    with pytest.raises(InputError, match="unique"):
        map_headers(headers, "services")


@pytest.mark.parametrize(
    "header",
    ["Patient name", "IP address", "DATE-OF-BIRTH", "email_address"],
)
def test_privacy_check_precedes_mapping(header):
    with pytest.raises(InputError, match="personal information"):
        map_headers([header], "services")


@pytest.mark.parametrize("header", ["", "   "])
def test_rejects_blank_headers(header):
    with pytest.raises(InputError, match="needs a name"):
        map_headers([header], "assets")


def test_rejects_non_text_headers():
    with pytest.raises(InputError, match="must be text"):
        map_headers([123], "assets")


def test_aliases_are_specific_to_inventory_kind():
    assert map_headers(["Device"], "software") == ["device"]


def test_csv_accepts_service_aliases():
    data = (
        b"Device ID,Port number,Transport,Service name,Exposure\n"
        b"TEST-01,8080,tcp,http,internal\n"
    )
    records = read_csv(data, "services")
    assert records[0].asset_id == "TEST-01"
    assert records[0].port == 8080


def test_csv_rejects_ambiguous_hostname():
    data = (
        b"asset_id,Hostname,port,protocol,service,exposure\n"
        b"TEST-01,example,8080,tcp,http,internal\n"
    )
    with pytest.raises(InputError, match="unsupported columns"):
        read_csv(data, "services")


def test_csv_rejects_alias_collision():
    data = (
        b"asset_id,port,Port number,protocol,service,exposure\n"
        b"TEST-01,8080,8080,tcp,http,internal\n"
    )
    with pytest.raises(InputError, match="unique"):
        read_csv(data, "services")


def test_csv_accepts_asset_name_alias():
    sample = PROJECT / "samples" / "lakeview_dental" / "assets.csv"
    reader = csv.reader(io.StringIO(sample.read_text(encoding="utf-8-sig")))
    rows = list(reader)
    index = rows[0].index("asset_name")
    rows[0][index] = "Computer name"

    stream = io.StringIO(newline="")
    csv.writer(stream).writerows(rows)
    records = read_csv(stream.getvalue().encode("utf-8"), "assets")
    assert len(records) == 11
    assert records[0].asset_name == rows[1][index]


def test_workbook_accepts_aliases():
    book = load_workbook(TEMPLATE)
    stream = io.BytesIO()
    replacements = {
        "assets": {"asset_name": "Computer name"},
        "software": {
            "vendor": "Software vendor",
            "product": "Software name",
            "version": "Software version",
            "asset_id": "Device ID",
        },
        "services": {
            "asset_id": "Device ID",
            "port": "Port number",
            "protocol": "Transport",
            "service": "Service name",
        },
    }

    try:
        for kind, aliases in replacements.items():
            for cell in book[kind][1]:
                if cell.value in aliases:
                    cell.value = aliases[cell.value]
        book.save(stream)
    finally:
        book.close()

    result = read_workbook(stream.getvalue())
    assert {kind: len(rows) for kind, rows in result.items()} == {
        "assets": 3,
        "software": 3,
        "services": 3,
    }