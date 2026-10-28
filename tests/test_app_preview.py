from pathlib import Path

import pytest
import requests
from streamlit.testing.v1 import AppTest

from clinicshield import assessment_input


ROOT = Path(__file__).resolve().parents[1]


def open_app():
    return AppTest.from_file(
        ROOT / "app.py",
        default_timeout=30,
    ).run()


def test_initial_screen_identifies_fictional_preview():
    app = open_app()

    assert not app.exception
    assert app.title[0].value == "ClinicShield"
    assert any(
        "fictional clinic inventories" in item.value
        for item in app.info
    )
    assert not app.metric
    assert "assessment_report" not in app.session_state


@pytest.mark.parametrize(
    "clinic",
    [
        "Lakeview Family Dental",
        "Southside Counseling Collective",
        "Westside Community Health",
    ],
)
def test_generates_each_sample_assessment(clinic):
    app = open_app()
    app.selectbox[0].select(clinic).run()
    app.button[0].click().run()

    assert not app.exception
    assert not app.error
    assert len(app.metric) == 3

    report = app.session_state["assessment_report"]
    assert report["score"]["status"] == "provisional"
    assert report["findings"]
    assert report["coverage_issues"]
    assert app.metric[0].value == f"{report['score']['final']}/100"
    assert any(
        "Provisional score" in item.value
        for item in app.warning
    )


def test_changing_clinic_clears_previous_report():
    app = open_app()
    app.button[0].click().run()
    assert app.metric

    app.selectbox[0].select("Westside Community Health").run()

    assert not app.exception
    assert not app.metric
    assert "assessment_report" not in app.session_state


def test_changing_policy_clears_previous_report():
    app = open_app()
    app.button[0].click().run()
    assert app.metric

    app.number_input[0].set_value(14).run()

    assert not app.exception
    assert not app.metric
    assert "assessment_report" not in app.session_state


def test_selected_observation_policy_reaches_report():
    app = open_app()
    app.number_input[0].set_value(14).run()
    app.button[0].click().run()

    assert not app.exception
    policy = app.session_state["assessment_report"]["freshness_policy"]
    assert policy["administrator_observation_max_age_seconds"] == (
        14 * 24 * 60 * 60
    )
    assert policy["public_feed_max_age_seconds"] == 8 * 24 * 60 * 60


def test_generated_report_has_readable_download():
    app = open_app()
    app.button[0].click().run()

    assert not app.exception
    buttons = app.get("download_button")
    assert len(buttons) == 1
    assert buttons[0].label == "Download readable assessment"


def test_preview_does_not_make_network_requests(monkeypatch):
    def unexpected_request(*args, **kwargs):
        pytest.fail("The sample preview must run offline.")

    monkeypatch.setattr(
        requests.sessions.Session,
        "request",
        unexpected_request,
    )

    app = open_app()
    app.button[0].click().run()

    assert not app.exception
    assert app.metric


def test_expected_input_failure_shows_safe_message(monkeypatch):
    def fail_read(*args, **kwargs):
        raise ValueError("internal test details must not be displayed")

    monkeypatch.setattr(assessment_input, "read_assessment", fail_read)

    app = open_app()
    app.button[0].click().run()

    assert not app.exception
    assert len(app.error) == 1
    assert "example could not be evaluated" in app.error[0].value
    assert "internal test details" not in app.error[0].value
    assert not app.metric