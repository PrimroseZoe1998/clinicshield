"""State and validation helpers for the five-screen in-memory assessment."""
import json
from pathlib import Path

from clinicshield.assessment_input import read_assessment
from clinicshield.checklist_input import QUESTION_IDS, derive_q24, read_checklist


def new_state():
    return {"step": 0, "source": None, "uploads": {}, "filenames": {},
            "options": {}, "answers": {q: "Unknown" for q in sorted(QUESTION_IDS)},
            "followups": {"Q24a": "Unknown", "Q24b": "Unknown"},
            "medical_devices_present": "Unknown", "report": None, "revision": 0}


def invalidate(state):
    state["report"] = None


def select_source(state, root, mode, clinic, scenario):
    source = (mode, clinic, scenario)
    if state["source"] == source:
        return
    fresh = new_state()
    fresh["source"] = source
    fresh["revision"] = state["revision"] + 1
    if mode == "Fictional example":
        folder = Path(root) / "samples" / clinic
        checklist = read_checklist((folder / "checklist.json").read_bytes(),
                                   (folder / "followups.json").read_bytes())
        fresh["answers"] = checklist.answers
        fresh["followups"] = checklist.followups
        for kind in ("assets", "software", "services"):
            path = folder / f"{kind}.csv"
            if path.exists():
                fresh["uploads"][f"{kind}_csv"] = path.read_bytes()
    state.clear()
    state.update(fresh)


def set_checklist(state, checklist):
    changed = (state["answers"] != checklist.answers or
               state["followups"] != checklist.followups or
               state["medical_devices_present"] != checklist.medical_devices_present)
    state["answers"] = dict(checklist.answers)
    state["followups"] = dict(checklist.followups)
    state["medical_devices_present"] = checklist.medical_devices_present
    if changed:
        invalidate(state)


def assessment_inputs(state):
    answers = dict(state["answers"])
    answers["Q24"] = derive_q24(state["followups"])
    return {**state["uploads"],
            "checklist_json": json.dumps(answers).encode(),
            "followups_json": json.dumps(state["followups"]).encode(),
            "medical_devices_present": state["medical_devices_present"]}


def validate_inventory_step(state):
    """Validate inventory before continuing, using current/default checklist answers."""
    return read_assessment(**assessment_inputs(state))


def load_saved_checklist(state, data, followups=None):
    checklist = read_checklist(data, followups)
    set_checklist(state, checklist)
    state["revision"] += 1
