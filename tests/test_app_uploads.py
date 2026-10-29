import csv
import io
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import requests

import app
from clinicshield.input_limits import InputError
from clinicshield.report_text import render_assessment_text


ROOT = Path(__file__).resolve().parents[1]


def inputs(clinic="lakeview_dental", format="CSV"):
    folder = ROOT / "samples" / clinic
    values = {key + "_json": (folder / (key + ".json")).read_bytes()
              for key in ("checklist", "followups")}
    if format == "Excel workbook":
        values["workbook_xlsx"] = (ROOT / "templates" / "clinicshield_inventory.xlsx").read_bytes()
    else:
        for kind in ("assets", "software", "services"):
            path = folder / f"{kind}.csv"
            if not path.exists():
                continue
            data = path.read_bytes()
            if format == "JSON":
                data = json.dumps(list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))).encode()
            values[f"{kind}_{format.lower()}"] = data
    return values


@pytest.mark.parametrize("format", ["CSV", "JSON", "Excel workbook"])
@pytest.mark.parametrize("clinic", ["lakeview_dental", "southside_counseling", "westside_health"])
def test_uploaded_formats_generate_provisional_reports(clinic, format):
    report = app.generate_uploaded(inputs(clinic, format), 30)
    assert "example_context" not in report
    assert report["assessment_context"]["input_mode"] == "uploaded inventory"
    assert report["score"]["status"] == "provisional"
    text = render_assessment_text(report)
    assert "Input mode: uploaded inventory" in text
    assert "Fictional clinic:" not in text
    assert "not been independently verified" in text


@pytest.mark.parametrize("missing", ["assets_csv", "software_csv", "checklist_json", "followups_json"])
def test_required_uploads_are_not_replaced_by_samples(missing):
    values = inputs()
    del values[missing]
    with pytest.raises(InputError):
        app.generate_uploaded(values, 30)


def test_invalid_inventory_rejected():
    values = inputs()
    values["assets_csv"] = b"invalid,columns\nprivate,value"
    with pytest.raises(InputError):
        app.generate_uploaded(values, 30)


def test_upload_evaluation_does_not_write_files_or_request_network(monkeypatch):
    values = inputs()
    def forbidden(*args, **kwargs):
        pytest.fail("Assessment generation must not write files or request network data.")
    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    monkeypatch.setattr(requests.sessions.Session, "request", forbidden)
    monkeypatch.setattr(app, "build_sample_evidence", forbidden)
    report = app.generate_uploaded(values, 30)
    assert report["findings"]


def fake_ui(monkeypatch, values):
    ui = MagicMock()
    ui.session_state = {}
    ui.radio.side_effect = lambda label, options: "Upload inventory" if label == "Assessment source" else "CSV"
    labels = {"Assets inventory (CSV)": "assets_csv", "Software inventory (CSV)": "software_csv",
              "Services inventory (CSV) (optional)": "services_csv",
              "Checklist answers (JSON)": "checklist_json", "Follow-up answers (JSON)": "followups_json"}
    def upload(label, **kwargs):
        data = values.get(labels.get(label))
        return SimpleNamespace(getvalue=lambda: data) if data is not None else None
    ui.file_uploader.side_effect = upload
    ui.selectbox.return_value = "Unknown"
    ui.number_input.return_value = 30
    ui.checkbox.return_value = False
    ui.button.return_value = True
    ui.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
    monkeypatch.setattr(app, "st", ui)
    return ui


def test_upload_ui_generates_download_and_clears_stale_report(monkeypatch):
    values = inputs()
    ui = fake_ui(monkeypatch, values)
    app.main()
    assert not ui.error.called
    assert "assessment_report" in ui.session_state
    assert "uploaded inventory" in ui.download_button.call_args.kwargs["data"]
    assert ui.download_button.call_args.kwargs["file_name"] == "clinicshield-uploaded-assessment.txt"
    ui.button.return_value = False
    values["assets_csv"] = b"changed inventory"
    app.main()
    assert "assessment_report" not in ui.session_state


def test_invalid_upload_ui_shows_safe_error_without_previous_report(monkeypatch):
    ui = fake_ui(monkeypatch, {})
    ui.session_state["assessment_report"] = {"old": "report"}
    app.main()
    assert "assessment_report" not in ui.session_state
    assert "uploaded assessment could not be evaluated" in ui.error.call_args.args[0]
    assert not ui.download_button.called


def test_original_scenario_unchanged():
    assert app.generate_example("lakeview_dental", 30, True)["score"]["final"] == 65


def test_missing_services_remains_unassessed():
    values = inputs()
    values.pop("services_csv")
    report = app.generate_uploaded(values, 30)
    assert any(item["topic"] == "services" for item in report["coverage_issues"])


def test_uploaded_evidence_uses_current_inventory_links():
    with pytest.raises(InputError, match="unknown asset"):
        app.generate_uploaded(inputs(), 30, cache_directory=ROOT / "missing-cache", lifecycle_mappings=json.dumps([
            {"asset_id": "ORPHAN", "review_status": "reviewed", "mapping": {
                "os_name": "Example OS", "os_version": "1.0", "product": "example-os",
                "release_name": "1", "mapping_basis": "Fictional test only.",
            }}
        ]).encode())
