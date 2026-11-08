from pathlib import Path
import pytest
import requests
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def open_app():
    return AppTest.from_file(ROOT / "app.py", default_timeout=30).run()


def click(app, label):
    next(b for b in app.button if b.label == label).click().run()
    assert not app.exception
    return app


def sample_to_checklist(app):
    click(app, "Continue to Upload")
    click(app, "Continue to Checklist")
    assert not app.error


def test_start_has_privacy_and_sample_choice():
    app = open_app()
    assert not app.exception
    assert app.title[0].value == "ClinicShield"
    assert any("not saved to disk" in item.value for item in app.info)
    assert not app.metric
    assert not app.get("download_button")


@pytest.mark.parametrize("clinic,score", [("Lakeview Family Dental",65),("Southside Counseling Collective",82),("Westside Community Health",80)])
def test_five_screen_scenario_and_downloads(clinic,score):
    app = open_app()
    app.selectbox[0].select(clinic).run()
    app.checkbox[0].set_value(True).run()
    sample_to_checklist(app)
    assert len(app.selectbox) == 27  # applicability + 24 direct questions + two Q24 follow-ups
    assert any("Why we ask" in c.value for c in app.caption)
    click(app,"Generate assessment")
    assert not app.error
    assert app.metric[0].value == f"{score}/100"
    assert any("Provisional score" in w.value for w in app.warning)
    assert not app.get("download_button")
    click(app,"Continue to Fix First")
    assert [b.label for b in app.get("download_button")] == [
        "Download assessment (PDF)","Download findings (CSV)","Save checklist (JSON)","Download readable assessment"]
    click(app,"Back")
    assert len(app.metric) == 3


def test_answer_edit_clears_old_report_and_survives_back_navigation():
    app = open_app()
    sample_to_checklist(app)
    click(app,"Generate assessment")
    click(app,"Back")
    next(s for s in app.selectbox if s.label == "Q02 answer").select("No").run()
    assert app.session_state["guided"]["report"] is None
    click(app,"Back")
    click(app,"Continue to Checklist")
    assert next(s for s in app.selectbox if s.label == "Q02 answer").value == "No"
    click(app,"Generate assessment")
    assert app.metric


def test_q24_derived_and_q23_not_applicable():
    app = open_app()
    sample_to_checklist(app)
    app.selectbox[0].select("No").run()
    assert not any(s.label == "Q23 answer" for s in app.selectbox)
    next(s for s in app.selectbox if s.label.startswith("Q24a:")).select("No").run()
    assert any("Q24 derived answer: No" in t.value for t in app.text)
    click(app,"Generate assessment")
    saved=app.session_state["guided"]["report"]["checklist_export"]
    assert saved["answers"]["Q24"] == "No"
    assert saved["medical_devices_present"] == "No"


def test_changing_source_resets_answers_and_report():
    app = open_app()
    sample_to_checklist(app)
    click(app,"Generate assessment")
    click(app,"Back")
    click(app,"Back")
    click(app,"Back")
    app.selectbox[0].select("Westside Community Health").run()
    assert app.session_state["guided"]["report"] is None
    assert app.session_state["guided"]["answers"]["Q06"] == "No"


def test_upload_requires_inventory_before_checklist():
    app = open_app()
    app.radio[0].set_value("Upload inventory").run()
    click(app,"Continue to Upload")
    click(app,"Continue to Checklist")
    assert app.error
    assert app.session_state["guided"]["step"] == 1


def test_sample_path_stays_offline(monkeypatch):
    def fail(*args,**kwargs):
        pytest.fail("Sample path must stay offline")
    monkeypatch.setattr(requests.sessions.Session,"request",fail)
    app=open_app()
    sample_to_checklist(app)
    click(app,"Generate assessment")
    assert app.metric


def test_new_assessment_clears_previous_session_answers():
    app=open_app()
    sample_to_checklist(app)
    click(app,"Generate assessment")
    click(app,"Continue to Fix First")
    click(app,"Start a new assessment")
    assert app.session_state["guided"]["step"] == 0
    assert app.session_state["guided"]["report"] is None


def test_findings_table_filters_preserve_scores_and_link_details():
    app=open_app()
    sample_to_checklist(app)
    click(app,"Generate assessment")
    before=app.metric[0].value
    table=app.dataframe[0].value
    assert not table.empty
    assert {"Ref","Severity","Status","Entity","Evidence"} <= set(table.columns)
    ref=table.iloc[0]["Ref"]
    assert any(e.label.startswith(ref+" |") for e in app.expander)
    next(s for s in app.selectbox if s.label=="Show findings").select("Needs review").run()
    assert not app.exception
    assert set(app.dataframe[0].value["Status"])=={"Needs review"}
    assert app.metric[0].value==before
