import csv
import io
import json
from pathlib import Path

import pytest

from clinicshield.assessment_input import read_assessment
from clinicshield.ingest import InputError


PROJECT = Path(__file__).resolve().parents[1]
SAMPLES = PROJECT / "samples"


def sample_inputs(clinic="lakeview_dental"):
    folder = SAMPLES / clinic
    values = {
        "assets_csv": (folder / "assets.csv").read_bytes(),
        "software_csv": (folder / "software.csv").read_bytes(),
        "checklist_json": (folder / "checklist.json").read_bytes(),
        "followups_json": (folder / "followups.json").read_bytes(),
    }
    services = folder / "services.csv"
    if services.exists():
        values["services_csv"] = services.read_bytes()
    return values


def change_csv(data, field, value):
    reader = csv.DictReader(
        io.StringIO(data.decode("utf-8-sig"), newline="")
    )
    headers = reader.fieldnames
    rows = list(reader)
    rows[0][field] = value

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


@pytest.mark.parametrize(
    "clinic,asset_count,software_count,service_count",
    [
        ("lakeview_dental", 11, 4, 3),
        ("southside_counseling", 9, 5, 0),
        ("westside_health", 35, 5, 3),
    ],
)
def test_reads_complete_sample_assessments(
    clinic, asset_count, software_count, service_count
):
    result = read_assessment(**sample_inputs(clinic))

    assert len(result.inventory.assets) == asset_count
    assert len(result.inventory.software) == software_count
    assert len(result.inventory.services) == service_count
    assert result.inventory.unmatched_service_rows == []
    assert len(result.checklist.answers) == 25


def test_reads_workbook_assessment():
    values = sample_inputs()
    result = read_assessment(
        workbook_xlsx=(
            PROJECT / "templates" / "clinicshield_inventory.xlsx"
        ).read_bytes(),
        checklist_json=values["checklist_json"],
        followups_json=values["followups_json"],
    )
    assert len(result.inventory.assets) == 3
    assert len(result.inventory.software) == 3
    assert len(result.inventory.services) == 3


@pytest.mark.parametrize(
    "field", ["assets_csv", "software_csv", "services_csv"]
)
def test_rejects_mixed_workbook_and_csv_inputs(field):
    values = sample_inputs()
    with pytest.raises(InputError, match="either an Excel workbook"):
        read_assessment(
            workbook_xlsx=b"unused",
            checklist_json=values["checklist_json"],
            followups_json=values["followups_json"],
            **{field: values[field]},
        )


@pytest.mark.parametrize(
    "missing", ["assets_csv", "software_csv", "both"]
)
def test_requires_complete_csv_inventories(missing):
    values = sample_inputs()
    if missing == "both":
        del values["assets_csv"]
        del values["software_csv"]
    else:
        del values[missing]

    with pytest.raises(InputError, match="both assets and software"):
        read_assessment(**values)


def test_requires_authorization_for_attached_scan():
    values = sample_inputs()
    values["nmap_xml"] = (SAMPLES / "lab_scan.xml").read_bytes()
    with pytest.raises(InputError, match="Confirm"):
        read_assessment(**values)


def test_preserves_and_flags_attached_scan_service():
    values = sample_inputs()
    values["nmap_xml"] = (SAMPLES / "lab_scan.xml").read_bytes()
    values["scan_authorized"] = True

    result = read_assessment(**values)

    assert len(result.inventory.services) == 4
    assert result.inventory.unmatched_service_rows == [4]
    scanned = result.inventory.services[-1]
    assert scanned.host == "192.0.2.2"
    assert scanned.port == 8080
    assert scanned.exposure == "unknown"
    assert len(result.inventory.assets) == 11


def test_accepts_scan_without_services_csv():
    values = sample_inputs("southside_counseling")
    values["nmap_xml"] = (SAMPLES / "lab_scan.xml").read_bytes()
    values["scan_authorized"] = True

    result = read_assessment(**values)
    assert len(result.inventory.services) == 1
    assert result.inventory.unmatched_service_rows == [1]


def test_validates_software_links_during_assessment():
    values = sample_inputs()
    values["software_csv"] = change_csv(
        values["software_csv"], "asset_id", "PRIVATE_SENTINEL"
    )
    with pytest.raises(InputError) as error:
        read_assessment(**values)
    assert "unknown asset" in str(error.value)
    assert "PRIVATE_SENTINEL" not in str(error.value)


def test_validates_checklist_conflicts_during_assessment():
    values = sample_inputs()
    answers = json.loads(values["checklist_json"])
    answers["Q24"] = "No"
    values["checklist_json"] = json.dumps(answers).encode("utf-8")

    with pytest.raises(InputError, match="conflicts"):
        read_assessment(**values)


def test_rejects_prohibited_csv_headers_during_assessment():
    values = sample_inputs()
    values["assets_csv"] = b"patient_name\nPRIVATE_SENTINEL\n"
    with pytest.raises(InputError) as error:
        read_assessment(**values)
    assert "personal information" in str(error.value)
    assert "PRIVATE_SENTINEL" not in str(error.value)


def test_rejects_supplied_empty_services_file():
    values = sample_inputs()
    values["services_csv"] = b""
    with pytest.raises(InputError, match="header row"):
        read_assessment(**values)

@pytest.mark.parametrize(
    "presence,expected",
    [("Yes", True), ("No", False), ("Unknown", True)],
)
def test_assessment_preserves_q23_applicability(presence, expected):
    result = read_assessment(
        **sample_inputs(),
        medical_devices_present=presence,
    )
    assert result.checklist.medical_devices_present == presence
    assert result.checklist.q23_applicable is expected 