"""Five-screen Streamlit journey. Assessment state stays in the current session."""
import json
from datetime import datetime, timezone
from pathlib import Path

from clinicshield.assessment_evidence import AssessmentEvidence
from clinicshield.checklist_input import Checklist, derive_q24
from clinicshield.guided_assessment import (
    new_state, select_source, invalidate, set_checklist, assessment_inputs,
    validate_inventory_step, load_saved_checklist,
)
from clinicshield.input_limits import InputError
from clinicshield.sample_evidence import build_sample_evidence

STEPS = ("Start", "Upload", "Checklist", "Results", "Fix First")
CHOICES = ["Unknown", "Yes", "No"]


def run_guided_app(st, root, clinics, evaluate, render_results, render_fix_first):
    st.set_page_config(page_title="ClinicShield", layout="wide")
    st.title("ClinicShield")
    if "guided" not in st.session_state:
        st.session_state["guided"] = new_state()
    state = st.session_state["guided"]
    step = state["step"]
    st.caption(f"Step {step + 1} of 5: {STEPS[step]}")
    st.progress((step + 1) / 5)

    def go(target):
        state["step"] = target
        st.rerun()

    def back(target):
        if st.button("Back", key="back"):
            go(target)

    def choose(label, value, key):
        return st.selectbox(label, CHOICES, index=CHOICES.index(value), key=key)

    def file_input(label, field, suffix, *, options=False):
        store = state["options"] if options else state["uploads"]
        key = f"file-{field}-{state['revision']}"
        def save():
            upload = st.session_state.get(key)
            if upload is None:
                store.pop(field, None)
                state["filenames"].pop(field, None)
            else:
                store[field] = upload.getvalue()
                state["filenames"][field] = upload.name
            invalidate(state)
        st.file_uploader(label, type=[suffix], key=key, on_change=save)
        if field in store:
            st.caption("Loaded: " + state["filenames"].get(field, "file"))

    if step == 0:
        st.subheader("Start your checkup")
        st.info("Do not upload patient data, passwords or recovery codes. Your inputs stay in this session: they are not saved to disk, and ClinicShield does not scan your network.")
        old = state["source"]
        mode = st.radio("Assessment source", ["Fictional example", "Upload inventory"],
                        index=1 if old and old[0] == "Upload inventory" else 0)
        clinic = next(iter(clinics.values()))
        scenario = False
        if mode == "Fictional example":
            names = list(clinics)
            selected = next((name for name in names if old and clinics[name] == old[1]), names[0])
            name = st.selectbox("Choose a fictional clinic", names, index=names.index(selected))
            clinic = clinics[name]
            st.info("Try fictional clinic inventories. These do not assess a real organization.")
            scenario = st.checkbox("Include documented fictional scenario evidence", value=bool(old and old[2]))
            if scenario:
                st.warning("Synthetic scenario evidence is enabled for demonstration, not verified security improvement.")
        select_source(state, root, mode, clinic, scenario)
        if st.button("Continue to Upload", type="primary"):
            go(1)
        return

    mode, clinic, scenario = state["source"]
    if step == 1:
        st.subheader("Upload inventories" if mode == "Upload inventory" else "Review sample inputs")
        if mode == "Fictional example":
            st.write(f"Sample inventory loaded: {clinic}. Review its answers on the next screen.")
        else:
            formats = ["CSV", "JSON", "Excel workbook"]
            fmt = st.radio("Inventory format", formats, index=formats.index(state.get("format", "CSV")))
            if state.get("format", fmt) != fmt:
                state["uploads"] = {}
                state["filenames"] = {}
                state["revision"] += 1
                invalidate(state)
            state["format"] = fmt
            st.caption("Assets and software are required. Network services are optional. Missing coverage stays visible.")
            for kind in ("assets", "software", "services"):
                st.download_button(f"Download {kind} CSV template", (Path(root) / "templates" / f"{kind}.csv").read_bytes(), file_name=f"{kind}.csv", mime="text/csv")
            if fmt == "Excel workbook":
                st.download_button("Download workbook template", (Path(root) / "templates/clinicshield_inventory.xlsx").read_bytes(), file_name="clinicshield_inventory.xlsx")
                file_input("Inventory workbook (XLSX)", "workbook_xlsx", "xlsx")
            else:
                for kind in ("assets", "software", "services"):
                    suffix = fmt.lower()
                    file_input(f"{kind.title()} inventory ({fmt})", f"{kind}_{suffix}", suffix)
            with st.expander("Optional existing network scan"):
                st.caption("Upload an existing Nmap XML file only for a network you own or are authorized to assess. ClinicShield does not run scans.")
                file_input("Nmap scan (XML)", "nmap_xml", "xml")
                authorized = st.checkbox("I confirm this scan was authorized", value=state["uploads"].get("scan_authorized", False))
                if authorized != state["uploads"].get("scan_authorized", False):
                    invalidate(state)
                state["uploads"]["scan_authorized"] = authorized
        with st.expander("Advanced evidence options"):
            previous = dict(state["options"])
            opts = state["options"]
            opts["observation_days"] = int(st.number_input("Administrator observation age limit in days", min_value=1, max_value=365, value=opts.get("observation_days",30)))
            st.caption("This limit is illustrative. Public-feed freshness uses the provisional eight-day limit.")
            opts["use_caches"] = st.checkbox("Load saved public-feed caches", value=opts.get("use_caches",False))
            if opts["use_caches"]:
                opts["cache_directory"] = st.text_input("Public-feed cache folder", value=opts.get("cache_directory",str(Path(root)/"data/cache")))
                st.caption("Reads saved public feeds locally. No feeds are downloaded and no applicability is inferred.")
                if not scenario:
                    file_input("Reviewed OS lifecycle mappings (JSON)","lifecycle_mappings","json",options=True)
                    file_input("Reviewed NVD software mappings (JSON)","nvd_mappings","json",options=True)
            if not scenario:
                file_input("Reviewed CVE applicability evidence (JSON)","applicability_json","json",options=True)
            if previous != opts:
                invalidate(state)
        back(0)
        if st.button("Continue to Checklist", type="primary"):
            try:
                validate_inventory_step(state)
            except InputError as exc:
                st.error(str(exc))
            except (ValueError, OSError):
                st.error("The inventory could not be read. Check file formats, required columns and asset links.")
            else:
                go(2)
        return

    if step == 2:
        st.subheader("Security practices checklist")
        st.caption("Choose Unknown when you have not checked. Yes represents a safer practice; Unknown earns no Safeguards points.")
        with st.expander("Load saved checklist answers"):
            saved = st.file_uploader("Checklist answers (JSON)", type=["json"], key="saved-checklist")
            follow = st.file_uploader("Follow-up answers (legacy JSON only)", type=["json"], key="saved-followups")
            if st.button("Load answers"):
                try:
                    if saved is None:
                        raise InputError("Choose a saved checklist file first.")
                    load_saved_checklist(state, saved.getvalue(), follow.getvalue() if follow else None)
                except InputError as exc:
                    st.error(str(exc))
                else:
                    st.rerun()
        prefix = f"answer-{state['revision']}-"
        presence = choose("Are network-connected medical devices present?", state["medical_devices_present"],prefix+"presence")
        questions = json.loads((Path(__file__).parent / "checklist_questions.json").read_text(encoding="utf-8"))
        answers = dict(state["answers"])
        followups = dict(state["followups"])
        section = None
        for q in questions:
            if q["section"] != section:
                section = q["section"]
                st.subheader(section)
            st.markdown(f"**{q['id']} - {q['title']}**")
            st.write(q["question"])
            if q["explanation"]:
                st.caption(q["explanation"])
            st.caption("Why we ask: " + q["why"])
            if q["id"] == "Q24":
                followups["Q24a"] = choose("Q24a: Is one named person responsible for security?",followups["Q24a"],prefix+"Q24a")
                followups["Q24b"] = choose("Q24b: Is a risk analysis documented within the last 12 months?",followups["Q24b"],prefix+"Q24b")
                answers["Q24"] = derive_q24(followups)
                st.text("Q24 derived answer: " + answers["Q24"] + " (scored once)")
            elif q["id"] == "Q23" and presence == "No":
                st.info("Q23 is not applicable because no network-connected medical devices are present.")
            else:
                answers[q["id"]] = choose(q["id"] + " answer", answers[q["id"]],prefix+q["id"])
        set_checklist(state, Checklist(answers, followups, presence))
        back(1)
        if st.button("Generate assessment", type="primary"):
            try:
                assessment = validate_inventory_step(state)
                now = datetime.now(timezone.utc)
                evidence = build_sample_evidence(clinic,assessment,now=now) if mode == "Fictional example" and scenario else AssessmentEvidence()
                opts = state["options"]
                report = evaluate(assessment,evidence,opts.get("observation_days",30),now=now,
                    cache_directory=opts.get("cache_directory") if opts.get("use_caches") else None,
                    lifecycle_mappings=opts.get("lifecycle_mappings") if opts.get("use_caches") and not scenario else None,
                    nvd_mappings=opts.get("nvd_mappings") if opts.get("use_caches") and not scenario else None,
                    applicability_json=opts.get("applicability_json") if not scenario else None)
                if mode == "Fictional example":
                    report["example_context"] = {"clinic":clinic,"evidence_mode":"documented fictional scenario" if scenario else "fictional inventory only",
                        "notice":"Demonstration only; not an assessment of a real clinic. Any scenario evidence is synthetic; timestamps represent fixture generation rather than real-world verification. Edited answers may differ from the original sample benchmark."}
                else:
                    report["assessment_context"] = {"input_mode":"uploaded inventory","notice":"Inputs have not been independently verified. Scores remain provisional."}
                state["report"] = report
            except InputError as exc:
                invalidate(state)
                st.error(str(exc))
            except (ValueError,OSError):
                invalidate(state)
                st.error("The assessment could not be evaluated. Check inventory formats, answers and optional evidence.")
            else:
                go(3)
        return

    report = state["report"]
    if report is None:
        st.info("Review inputs and generate an assessment before viewing results.")
        if st.button("Return to Checklist"):
            go(2)
        return
    if step == 3:
        render_results(report)
        back(2)
        if st.button("Continue to Fix First", type="primary"):
            go(4)
    else:
        render_fix_first(report, "uploaded" if mode == "Upload inventory" else clinic)
        back(3)
        if st.button("Start a new assessment"):
            st.session_state["guided"] = new_state()
            # Clear widget state too, including uploaded files, before another assessment.
            for key in list(st.session_state):
                if key != "guided":
                    del st.session_state[key]
            st.rerun()
