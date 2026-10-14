import csv
import io
import json
from pathlib import Path

import pytest

from clinicshield import json_input
from clinicshield.assessment_input import read_assessment
from clinicshield.input_limits import MAX_UPLOAD_BYTES, InputError
from clinicshield.json_input import read_inventory_json


PROJECT = Path(__file__).resolve().parents[1]
SAMPLES = PROJECT / "samples"


def encoded(value):
    return json.dumps(value).encode("utf-8")


def service_row(**changes):
    row = {
        "asset_id": "TEST-01",
        "port": 8080,
        "protocol": "tcp",
        "service": "http",
        "exposure": "unknown",
    }
    return {**row, **changes}


def csv_as_json(path):
    text = path.read_text(encoding="utf-8-sig")
    return encoded(list(csv.DictReader(io.StringIO(text))))


def assessment_values():
    folder = SAMPLES / "lakeview_dental"
    return {
        "assets_json": csv_as_json(folder / "assets.csv"),
        "software_json": csv_as_json(folder / "software.csv"),
        "services_json": csv_as_json(folder / "services.csv"),
        "checklist_json": (folder / "checklist.json").read_bytes(),
        "followups_json": (folder / "followups.json").read_bytes(),
    }


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
def test_reads_sample_inventories_as_json(clinic, kind, count):
    path = SAMPLES / clinic / f"{kind}.csv"
    assert len(read_inventory_json(csv_as_json(path), kind)) == count


def test_accepts_numeric_port_and_utf8_bom():
    data = b"\xef\xbb\xbf" + encoded([service_row()])
    records = read_inventory_json(data, "services")
    assert records[0].port == 8080


def test_accepts_header_aliases():
    row = service_row()
    row["Port number"] = row.pop("port")
    records = read_inventory_json(encoded([row]), "services")
    assert records[0].port == 8080


def test_rejects_alias_collision():
    row = service_row()
    row["Port number"] = 8080
    with pytest.raises(InputError, match="unique"):
        read_inventory_json(encoded([row]), "services")


@pytest.mark.parametrize("value", [{}, "text", None, 1])
def test_requires_array(value):
    with pytest.raises(InputError, match="array of objects"):
        read_inventory_json(encoded(value), "services")


def test_rejects_empty_array():
    with pytest.raises(InputError, match="at least one entry"):
        read_inventory_json(b"[]", "services")


@pytest.mark.parametrize("value", [None, "text", 1, []])
def test_requires_object_entries(value):
    with pytest.raises(InputError, match="must be an object"):
        read_inventory_json(encoded([value]), "services")


@pytest.mark.parametrize("data", [b"", b"[", b"\xff"])
def test_rejects_invalid_json(data):
    with pytest.raises(InputError, match="valid UTF-8"):
        read_inventory_json(data, "services")


def test_rejects_duplicate_keys():
    data = b'[{"port":80,"port":8080}]'
    with pytest.raises(InputError, match="keys must be unique"):
        read_inventory_json(data, "services")


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_rejects_nonstandard_numbers(constant):
    data = f'[{{"port":{constant}}}]'.encode("utf-8")
    with pytest.raises(InputError, match="NaN or Infinity"):
        read_inventory_json(data, "services")


def test_rejects_overflowing_float():
    data = encoded([service_row()]).replace(b"8080", b"1e400")
    with pytest.raises(InputError, match="finite"):
        read_inventory_json(data, "services")


@pytest.mark.parametrize("value", [{"nested": "value"}, ["value"]])
def test_rejects_nested_field_values(value):
    with pytest.raises(InputError, match="objects or arrays"):
        read_inventory_json(
            encoded([service_row(product=value)]), "services"
        )


def test_checks_privacy_headers_in_later_entries():
    rows = [
        service_row(),
        service_row(patient_name="PRIVATE_SENTINEL"),
    ]
    with pytest.raises(InputError) as error:
        read_inventory_json(encoded(rows), "services")
    assert "personal information" in str(error.value)
    assert "PRIVATE_SENTINEL" not in str(error.value)


def test_rejects_invalid_fields_safely():
    with pytest.raises(InputError) as error:
        read_inventory_json(
            encoded([service_row(port="PRIVATE_SENTINEL")]),
            "services",
        )
    assert "invalid fields" in str(error.value)
    assert "PRIVATE_SENTINEL" not in str(error.value)


def test_rejects_missing_required_fields():
    row = service_row()
    del row["exposure"]
    with pytest.raises(InputError, match="Missing required fields"):
        read_inventory_json(encoded([row]), "services")


def test_rejects_unsupported_fields():
    with pytest.raises(InputError, match="unsupported fields"):
        read_inventory_json(
            encoded([service_row(extra="value")]), "services"
        )


def test_rejects_duplicate_asset_ids():
    path = SAMPLES / "lakeview_dental" / "assets.csv"
    rows = json.loads(csv_as_json(path))
    with pytest.raises(InputError, match="Asset IDs must be unique"):
        read_inventory_json(encoded([rows[0], rows[0]]), "assets")


def test_enforces_upload_limit():
    with pytest.raises(InputError, match="size limit"):
        read_inventory_json(
            b"x" * (MAX_UPLOAD_BYTES + 1), "services"
        )


def test_enforces_entry_limit(monkeypatch):
    monkeypatch.setattr(json_input, "MAX_INVENTORY_ROWS", 1)
    with pytest.raises(InputError, match="too many entries"):
        read_inventory_json(
            encoded([service_row(), service_row()]), "services"
        )


def test_enforces_value_length_limit(monkeypatch):
    monkeypatch.setattr(json_input, "MAX_CELL_CHARACTERS", 10)
    with pytest.raises(InputError, match="length limit"):
        read_inventory_json(
            encoded([service_row(product="x" * 11)]), "services"
        )


def test_rejects_non_bytes_input():
    with pytest.raises(InputError, match="as bytes"):
        read_inventory_json("[]", "services")


def test_rejects_unknown_kind():
    with pytest.raises(InputError, match="Choose assets"):
        read_inventory_json(b"[]", "unknown")


def test_assessment_accepts_json_inventories():
    result = read_assessment(**assessment_values())
    assert len(result.inventory.assets) == 11
    assert len(result.inventory.software) == 4
    assert len(result.inventory.services) == 3


def test_assessment_accepts_csv_and_json_for_different_inventories():
    values = assessment_values()
    del values["assets_json"]
    values["assets_csv"] = (
        SAMPLES / "lakeview_dental" / "assets.csv"
    ).read_bytes()

    assert len(read_assessment(**values).inventory.assets) == 11


@pytest.mark.parametrize("kind", ["assets", "software", "services"])
def test_assessment_rejects_duplicate_inventory_formats(kind):
    values = assessment_values()
    values[f"{kind}_csv"] = b"unused"
    with pytest.raises(InputError, match="each inventory once"):
        read_assessment(**values)


def test_assessment_rejects_workbook_with_json_inventories():
    values = assessment_values()
    values["workbook_xlsx"] = b"unused"
    with pytest.raises(InputError, match="either an Excel workbook"):
        read_assessment(**values)


def test_assessment_accepts_json_with_authorized_scan():
    values = assessment_values()
    values["nmap_xml"] = (SAMPLES / "lab_scan.xml").read_bytes()
    values["scan_authorized"] = True
    result = read_assessment(**values)

    assert len(result.inventory.services) == 4
    assert result.inventory.unmatched_service_rows == [4]