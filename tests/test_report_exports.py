import copy
import csv
import io
import json
from pathlib import Path

import pytest
import app
from clinicshield.checklist_input import read_checklist
from clinicshield.input_limits import InputError
from clinicshield.report_exports import CSV_FIELDS, render_findings_csv, render_checklist_json

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("clinic", list(app.CLINICS.values()))
def test_exports_and_uploaded_round_trip(clinic):
    report = app.generate_example(clinic, 30, include_scenario=True)
    before = copy.deepcopy(report)
    saved = render_checklist_json(report)
    restored = read_checklist(saved.encode())
    assert restored.answers == report["checklist_export"]["answers"]
    assert restored.followups == report["checklist_export"]["followups"]
    assert restored.medical_devices_present == report["checklist_export"]["medical_devices_present"]
    rows = list(csv.DictReader(io.StringIO(render_findings_csv(report))))
    assert len(rows) == len(report["findings"])
    for row, finding in zip(rows, report["findings"]):
        assert json.loads(row["evidence"]) == finding["evidence"]
        assert json.loads(row["framework_references"]) == finding["framework_references"]
        assert row["status"] == finding["status"]
        assert row["score_status"] == "provisional"
        assert json.loads(row["example_context"])["evidence_mode"] == "documented fictional scenario"
    assert report == before
    folder = ROOT / "samples" / clinic
    uploads = {"checklist_json": saved.encode()}
    for kind in ("assets", "software", "services"):
        path = folder / f"{kind}.csv"
        if path.exists():
            uploads[kind + "_csv"] = path.read_bytes()
    uploaded = app.generate_uploaded(uploads, 30)
    inventory_only = app.generate_example(clinic, 30)
    assert uploaded["score"] == inventory_only["score"]
    assert uploaded["checklist_export"] == report["checklist_export"]


@pytest.mark.parametrize("presence", ["Yes", "No", "Unknown"])
def test_bundle_keeps_applicability_and_unknown_answers(presence):
    report = app.generate_example("lakeview_dental", 30)
    report["checklist_export"]["medical_devices_present"] = presence
    report["checklist_export"]["answers"]["Q01"] = "Unknown"
    restored = read_checklist(render_checklist_json(report).encode())
    assert restored.medical_devices_present == presence
    assert restored.answers["Q01"] == "Unknown"


@pytest.mark.parametrize("change", [
    {"checklist_schema_version": True},
    {"checklist_schema_version": 2},
    {"medical_devices_present": "invalid"},
    {"followups": {"Q24a": "Unknown", "Q24b": "Unknown"}},
    {"unexpected": "field"},
])
def test_invalid_bundles_rejected(change):
    report = app.generate_example("lakeview_dental", 30)
    data = report["checklist_export"] | change
    with pytest.raises(InputError):
        read_checklist(json.dumps(data).encode())


def test_bundle_rejects_conflicting_separate_inputs():
    report = app.generate_example("lakeview_dental", 30)
    report["checklist_export"]["medical_devices_present"] = "No"
    saved = render_checklist_json(report).encode()
    with pytest.raises(InputError):
        read_checklist(saved, b'{"Q24a":"Yes","Q24b":"Yes"}')
    with pytest.raises(InputError):
        read_checklist(saved, medical_devices_present="Yes")


@pytest.mark.parametrize("payload", ["=1+1", "+1", "-1", "@SUM(A1)", "  =1", "\t=1", "\r=1", "\n=1"])
def test_csv_formula_cells_neutralized_and_quotes_round_trip(payload):
    report = app.generate_example("lakeview_dental", 30)
    report["findings"][0]["scoring_entity_id"] = payload
    report["findings"][0]["issue_key"] = 'comma, quote" and\nnewline'
    row = next(csv.DictReader(io.StringIO(render_findings_csv(report))))
    assert row["scoring_entity_id"] == "'" + payload
    assert row["issue_key"] == 'comma, quote" and\nnewline'


def test_empty_findings_export_has_header():
    report = app.generate_example("lakeview_dental", 30)
    report["findings"] = []
    reader = csv.DictReader(io.StringIO(render_findings_csv(report)))
    assert reader.fieldnames == list(CSV_FIELDS)
    assert list(reader) == []
