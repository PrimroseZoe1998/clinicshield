import json
import builtins
import io
import logging

import pytest

from clinicshield.ingest import InputError, read_csv


@pytest.mark.parametrize("port", ["8080", "PRIVATE_SENTINEL"])
def test_csv_does_not_write_or_log(monkeypatch, capsys, caplog, port):
    data = (
        "asset_id,port,protocol,service,exposure\n"
        f"PRIVATE_SENTINEL,{port},tcp,http,internal\n"
    ).encode()

    def reject_file_access(*args, **kwargs):
        pytest.fail("CSV ingestion attempted filesystem access")

    with caplog.at_level(logging.DEBUG):
        with monkeypatch.context() as guard:
            guard.setattr(builtins, "open", reject_file_access)
            guard.setattr(io, "open", reject_file_access)

            if port == "8080":
                records = read_csv(data, "services")
                assert len(records) == 1
            else:
                with pytest.raises(InputError) as error:
                    read_csv(data, "services")
                assert "PRIVATE_SENTINEL" not in str(error.value)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
    assert not caplog.records

    import json
from pathlib import Path

from clinicshield.json_input import read_inventory_json
from clinicshield.nmap_input import read_nmap
from clinicshield.workbook import read_workbook


@pytest.mark.parametrize("format_name", ["json", "excel", "nmap"])
@pytest.mark.parametrize("invalid", [False, True])
def test_other_readers_do_not_write_or_log(
    monkeypatch, capsys, caplog, format_name, invalid
):
    project = Path(__file__).resolve().parents[1]

    if format_name == "json":
        data = json.dumps([{
            "asset_id": "PRIVATE_SENTINEL",
            "port": "PRIVATE_SENTINEL" if invalid else 8080,
            "protocol": "tcp",
            "service": "http",
            "exposure": "internal",
        }]).encode()
        reader = lambda: read_inventory_json(data, "services")

    elif format_name == "excel":
        data = (
            b"PRIVATE_SENTINEL"
            if invalid
            else (project / "templates" /
                  "clinicshield_inventory.xlsx").read_bytes()
        )
        reader = lambda: read_workbook(data)

    else:
        port = "PRIVATE_SENTINEL" if invalid else "8080"
        data = f"""
        <nmaprun scanner="nmap">
          <host>
            <status state="up"/>
            <address addr="192.0.2.2" addrtype="ipv4"/>
            <ports>
              <port protocol="tcp" portid="{port}">
                <state state="open"/>
                <service name="http" product="PRIVATE_SENTINEL"/>
              </port>
            </ports>
          </host>
        </nmaprun>
        """.encode()
        reader = lambda: read_nmap(data, authorized=True)

    def reject_file_access(*args, **kwargs):
        pytest.fail("Ingestion attempted filesystem access")

    with caplog.at_level(logging.DEBUG):
        with monkeypatch.context() as guard:
            guard.setattr(builtins, "open", reject_file_access)
            guard.setattr(io, "open", reject_file_access)

            if invalid:
                with pytest.raises(InputError) as error:
                    reader()
                assert "PRIVATE_SENTINEL" not in str(error.value)
            else:
                assert reader()

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
    assert not caplog.records

import csv
import os
import tempfile

from openpyxl import Workbook

from clinicshield.assessment_input import read_assessment


def privacy_assessment_inputs(clinic, format_name):
    project = Path(__file__).resolve().parents[1]
    folder = project / "samples" / clinic
    values = {
        "checklist_json": (folder / "checklist.json").read_bytes(),
        "followups_json": (folder / "followups.json").read_bytes(),
    }

    inventories = {}
    for kind in ("assets", "software", "services"):
        path = folder / f"{kind}.csv"
        if path.exists():
            inventories[kind] = path.read_bytes()

    if format_name == "csv":
        for kind, data in inventories.items():
            values[f"{kind}_csv"] = data

    elif format_name == "json":
        for kind, data in inventories.items():
            rows = csv.DictReader(
                io.StringIO(data.decode("utf-8-sig"))
            )
            values[f"{kind}_json"] = json.dumps(list(rows)).encode()

    else:
        book = Workbook()
        book.remove(book.active)
        try:
            for kind, data in inventories.items():
                sheet = book.create_sheet(kind)
                rows = csv.reader(
                    io.StringIO(data.decode("utf-8-sig"))
                )
                for row in rows:
                    sheet.append(row)

            stream = io.BytesIO()
            book.save(stream)
            values["workbook_xlsx"] = stream.getvalue()
        finally:
            book.close()

    return values

@pytest.mark.parametrize(
    "clinic",
    ["lakeview_dental", "southside_counseling", "westside_health"],
)
@pytest.mark.parametrize("format_name", ["csv", "json", "excel"])
@pytest.mark.parametrize("invalid", [False, True])
@pytest.mark.parametrize("with_scan", [False, True])
def test_full_assessment_does_not_write_or_log(
    monkeypatch, capsys, caplog, clinic, format_name, invalid, with_scan
):
    values = privacy_assessment_inputs(clinic, format_name)
    if with_scan:
        project = Path(__file__).resolve().parents[1]
        values["nmap_xml"] = (
            project / "samples" / "lab_scan.xml"
        ).read_bytes()
        values["scan_authorized"] = True

    if invalid:
        answers = json.loads(values["checklist_json"])
        answers["Q01"] = "PRIVATE_SENTINEL"
        values["checklist_json"] = json.dumps(answers).encode()

    def reject_file_access(*args, **kwargs):
        pytest.fail("Assessment ingestion attempted filesystem access")

    def reject_temp_file(*args, **kwargs):
        pytest.fail("Assessment ingestion attempted temporary-file creation")

    caplog.clear()
    capsys.readouterr()

    with caplog.at_level(logging.DEBUG):
        with monkeypatch.context() as guard:
            guard.setattr(builtins, "open", reject_file_access)
            guard.setattr(io, "open", reject_file_access)
            guard.setattr(os, "open", reject_file_access)
            guard.setattr(os, "write", reject_file_access)

            for name in (
                "TemporaryFile",
                "NamedTemporaryFile",
                "SpooledTemporaryFile",
                "mkstemp",
                "mkdtemp",
            ):
                guard.setattr(tempfile, name, reject_temp_file)

            if invalid:
                with pytest.raises(InputError) as error:
                    read_assessment(**values)
                assert "PRIVATE_SENTINEL" not in str(error.value)
            else:
                result = read_assessment(**values)
                assert result.inventory.assets
                assert len(result.checklist.answers) == 25

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
    assert not caplog.records