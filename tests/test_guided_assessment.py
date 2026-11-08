import copy
import json
from pathlib import Path
import pytest
import app
from clinicshield.checklist_input import Checklist
from clinicshield.guided_assessment import (
    new_state, select_source, set_checklist, load_saved_checklist,
    validate_inventory_step, assessment_inputs,
)
from clinicshield.input_limits import InputError
from clinicshield.report_exports import render_checklist_json

ROOT = Path(__file__).resolve().parents[1]


def sample_state(clinic="lakeview_dental"):
    state=new_state()
    select_source(state,ROOT,"Fictional example",clinic,False)
    return state


def test_catalog_has_all_reviewed_questions_and_reasons():
    catalog=json.loads((ROOT/"clinicshield/checklist_questions.json").read_text())
    assert [q["id"] for q in catalog] == [f"Q{i:02d}" for i in range(1,26)]
    assert all(q["question"] and q["why"] and q["section"] for q in catalog)
    assert len(set(q["section"] for q in catalog)) == 10


def test_sample_state_keeps_edits_until_source_changes():
    state=sample_state()
    checklist=validate_inventory_step(state).checklist
    checklist.answers["Q02"]="No"
    state["report"]={"old":True}
    set_checklist(state,checklist)
    assert state["report"] is None
    select_source(state,ROOT,"Fictional example","lakeview_dental",False)
    assert state["answers"]["Q02"]=="No"
    state["report"]={"old":True}
    select_source(state,ROOT,"Fictional example","westside_health",False)
    assert state["report"] is None
    assert state["answers"]["Q06"]=="No"


def test_upload_source_clears_sample_data_and_uses_unknown_defaults():
    state=sample_state()
    state["options"]={"applicability_json":b"old"}
    select_source(state,ROOT,"Upload inventory","lakeview_dental",False)
    assert state["uploads"]=={}
    assert state["options"]=={}
    assert set(state["answers"].values())=={"Unknown"}
    assert state["medical_devices_present"]=="Unknown"
    with pytest.raises(InputError):
        validate_inventory_step(state)


@pytest.mark.parametrize("clinic", list(app.CLINICS.values()))
def test_load_bundle_preserves_followups_applicability_and_invalidates_results(clinic):
    report=app.generate_example(clinic,30)
    report["checklist_export"]["medical_devices_present"]="No"
    saved=render_checklist_json(report).encode()
    state=sample_state()
    state["report"]={"old":True}
    load_saved_checklist(state,saved)
    assert state["report"] is None
    inputs=assessment_inputs(state)
    restored=validate_inventory_step(state)
    assert restored.checklist.answers==report["checklist_export"]["answers"]
    assert restored.checklist.followups==report["checklist_export"]["followups"]
    assert inputs["medical_devices_present"]=="No"


def test_failed_saved_import_does_not_replace_current_answers():
    state=sample_state()
    before=copy.deepcopy(state)
    with pytest.raises(InputError):
        load_saved_checklist(state,b'{"invalid":"private"}')
    assert state==before


def test_derived_q24_and_applicability_reach_scoring():
    state=sample_state()
    state["answers"]["Q24"]="Yes"
    state["followups"]={"Q24a":"Unknown","Q24b":"No"}
    state["medical_devices_present"]="No"
    assessment=validate_inventory_step(state)
    assert assessment.checklist.answers["Q24"]=="No"
    assert not assessment.checklist.q23_applicable
