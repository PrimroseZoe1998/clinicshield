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


def fake_ui(monkeypatch, values, step=2):
    from clinicshield.guided_assessment import new_state, set_checklist
    from clinicshield.checklist_input import read_checklist
    state = new_state()
    state["source"] = ("Upload inventory", "lakeview_dental", False)
    state["step"] = step
    state["uploads"] = {k:v for k,v in values.items() if k not in ("checklist_json", "followups_json")}
    if values.get("checklist_json"):
        set_checklist(state, read_checklist(values["checklist_json"], values.get("followups_json")))
    ui = MagicMock()
    ui.session_state = {"guided":state}
    ui.radio.side_effect = lambda label, options, **kwargs: options[kwargs.get("index",0)]
    ui.selectbox.side_effect = lambda label, options, **kwargs: options[kwargs.get("index",0)]
    ui.file_uploader.return_value = None
    ui.number_input.return_value = 30
    ui.checkbox.return_value = False
    ui.button.side_effect = lambda label, **kwargs: label in ("Generate assessment", "Continue to Checklist")
    ui.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
    monkeypatch.setattr(app, "st", ui)
    return ui


def test_upload_ui_generates_results_and_all_downloads(monkeypatch):
    values = inputs()
    ui = fake_ui(monkeypatch, values)
    app.main()
    assert not ui.error.called
    state = ui.session_state["guided"]
    assert state["step"] == 3 and state["report"] is not None
    app.main()
    assert ui.metric.called is False  # Metrics live in the three columns.
    state["step"] = 4
    app.main()
    downloads = {call.args[0]: call.kwargs for call in ui.download_button.call_args_list}
    assert downloads["Download assessment (PDF)"]["data"].startswith(b"%PDF-")
    assert downloads["Download findings (CSV)"]["mime"] == "text/csv"
    saved = json.loads(downloads["Save checklist (JSON)"]["data"])
    assert saved["answers"] == json.loads(values["checklist_json"])
    assert saved["followups"] == json.loads(values["followups_json"])
    ui.subheader.assert_any_call("Fix First plan")


def test_invalid_upload_ui_stays_on_upload_and_displays_safe_error(monkeypatch):
    ui = fake_ui(monkeypatch, {},step=1)
    app.main()
    assert ui.error.called
    assert ui.session_state["guided"]["step"] == 1
    assert ui.session_state["guided"]["report"] is None


@pytest.mark.parametrize("format,field,bad", [
    ("CSV", "assets_csv", b"invalid,columns\nPRIVATE_SENTINEL,value"),
    ("JSON", "assets_json", b'{"PRIVATE_SENTINEL":'),
    ("Excel workbook", "workbook_xlsx", b"PRIVATE_SENTINEL"),
    ("CSV", "nmap_xml", b"<PRIVATE_SENTINEL"),
])
def test_rejected_inventory_clears_stale_report_without_echoing_data(
    monkeypatch, format, field, bad
):
    values = inputs(format=format)
    values[field] = bad
    if field == "nmap_xml":
        values["scan_authorized"] = True
    ui = fake_ui(monkeypatch, values, step=1)
    state = ui.session_state["guided"]
    state["format"] = format
    state["report"] = {"stale": "PRIVATE_SENTINEL"}
    if field == "nmap_xml":
        ui.checkbox.side_effect = lambda label, **kwargs: label == "I confirm this scan was authorized"
    app.main()
    assert state["step"] == 1
    assert state["report"] is None
    assert ui.error.called
    assert "PRIVATE_SENTINEL" not in str(ui.error.call_args_list)
    assert all("template" in call.args[0] for call in ui.download_button.call_args_list)


@pytest.mark.parametrize("error_type", [ValueError, OSError])
def test_inventory_failure_uses_generic_message_and_clears_report(monkeypatch, error_type):
    from clinicshield import guided_ui

    def fail(state):
        raise error_type("PRIVATE_SENTINEL")

    ui = fake_ui(monkeypatch, inputs(), step=1)
    ui.session_state["guided"]["report"] = {"old": True}
    monkeypatch.setattr(guided_ui, "validate_inventory_step", fail)
    app.main()
    assert ui.session_state["guided"]["report"] is None
    assert ui.session_state["guided"]["step"] == 1
    assert "PRIVATE_SENTINEL" not in str(ui.error.call_args_list)
    assert "inventory could not be read" in ui.error.call_args.args[0]


def test_combined_upload_limit_rejected_in_guided_ui(monkeypatch):
    from clinicshield import input_limits
    ui = fake_ui(monkeypatch, inputs(), step=1)
    monkeypatch.setattr(input_limits, "MAX_ASSESSMENT_BYTES", 1)
    app.main()
    assert ui.session_state["guided"]["step"] == 1
    assert ui.session_state["guided"]["report"] is None
    assert "combined assessment" in ui.error.call_args.args[0]


@pytest.mark.parametrize("removed", [False, True])
def test_upload_callback_replaces_or_removes_bytes_and_invalidates_report(monkeypatch, removed):
    ui = fake_ui(monkeypatch, inputs(), step=1)
    state = ui.session_state["guided"]
    state["report"] = {"old": True}
    state["filenames"]["assets_csv"] = "old.csv"
    ui.button.return_value = False
    ui.button.side_effect = lambda *args, **kwargs: False

    def uploader(label, **kwargs):
        if label == "Assets inventory (CSV)":
            ui.session_state[kwargs["key"]] = (
                None if removed else SimpleNamespace(
                    name="replacement.csv", getvalue=lambda: b"replacement"
                )
            )
            kwargs["on_change"]()
        return None

    ui.file_uploader.side_effect = uploader
    app.main()
    assert state["report"] is None
    if removed:
        assert "assets_csv" not in state["uploads"]
        assert "assets_csv" not in state["filenames"]
    else:
        assert state["uploads"]["assets_csv"] == b"replacement"
        assert state["filenames"]["assets_csv"] == "replacement.csv"


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


def test_saved_bundle_upload_ui_exposes_downloads(monkeypatch):
    from clinicshield.report_exports import render_checklist_json
    values = inputs()
    saved = render_checklist_json(app.generate_uploaded(values, 30)).encode()
    values["checklist_json"] = saved
    values.pop("followups_json")
    ui = fake_ui(monkeypatch, values)
    app.main()
    assert not ui.error.called
    ui.session_state["guided"]["step"] = 4
    app.main()
    downloads = {call.args[0]: call.kwargs for call in ui.download_button.call_args_list}
    assert json.loads(downloads["Save checklist (JSON)"]["data"]) == json.loads(saved)
