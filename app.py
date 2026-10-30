from datetime import datetime, timedelta, timezone
from hashlib import sha256
from decimal import Decimal
from pathlib import Path

import streamlit as st

from clinicshield.assessment_nvd import load_assessment_nvd
from clinicshield.nvd_cache import read_nvd_allowlist
from clinicshield.assessment_applicability import load_reviewed_applicability
from clinicshield.assessment_lifecycle import load_assessment_lifecycle, read_lifecycle_mappings
from clinicshield.assessment_cache import load_assessment_caches
from clinicshield.sample_evidence import build_sample_evidence
from clinicshield.assessment_evidence import (
    AssessmentEvidence,
    AssessmentFreshnessPolicy,
)
from clinicshield.assessment_input import read_assessment
from clinicshield.input_limits import InputError, validate_assessment_uploads
from clinicshield.assessment_report import build_assessment_report
from clinicshield.assessment_scoring import score_assessment
from clinicshield.report_text import render_assessment_text
from clinicshield.scoring import SEVERITY_POINTS


ROOT = Path(__file__).resolve().parent
CLINICS = {
    "Lakeview Family Dental": "lakeview_dental",
    "Southside Counseling Collective": "southside_counseling",
    "Westside Community Health": "westside_health",
}


def generate_example(clinic, observation_days, include_scenario=False, cache_directory=None, lifecycle_mappings=None, applicability_json=None, nvd_mappings=None):
    folder = ROOT / "samples" / clinic
    services = folder / "services.csv"

    assessment = read_assessment(
        checklist_json=(folder / "checklist.json").read_bytes(),
        followups_json=(folder / "followups.json").read_bytes(),
        assets_csv=(folder / "assets.csv").read_bytes(),
        software_csv=(folder / "software.csv").read_bytes(),
        services_csv=services.read_bytes() if services.exists() else None,
    )
    now = datetime.now(timezone.utc)
    evidence = (
        build_sample_evidence(clinic, assessment, now=now)
        if include_scenario else AssessmentEvidence()
    )

    report = evaluate_supplied_assessment(
        assessment, evidence, observation_days, now=now,
        cache_directory=cache_directory, lifecycle_mappings=lifecycle_mappings,
        applicability_json=applicability_json, nvd_mappings=nvd_mappings,
    )
    report["example_context"] = {
        "clinic": clinic,
        "evidence_mode": (
            "documented fictional scenario"
            if include_scenario else "fictional inventory only"
        ),
        "notice": (
            "Demonstration only; not an assessment of a real clinic. "
            "Any scenario evidence is synthetic, and its timestamps "
            "represent fixture generation rather than real-world verification. "
            + (
                "Saved public-feed caches were requested; see cache status. "
                "No CVE applicability is inferred from those feeds."
                if cache_directory is not None else
                "Live threat-intelligence caches are not loaded."
            )
        ),
    }
    return report



def evaluate_supplied_assessment(
    assessment, evidence, observation_days, *, now, cache_directory=None,
    lifecycle_mappings=None, applicability_json=None, nvd_mappings=None,
):
    cache_messages = ()
    if cache_directory is not None:
        evidence, cache_messages = load_assessment_caches(
            evidence, Path(cache_directory), now=now,
            max_age=timedelta(days=8),
        )

    if lifecycle_mappings is not None:
        if cache_directory is None:
            raise ValueError("Lifecycle mappings require a public-feed cache folder.")
        evidence, lifecycle_messages = load_assessment_lifecycle(
            assessment, evidence, read_lifecycle_mappings(lifecycle_mappings),
            Path(cache_directory), now=now, max_age=timedelta(days=8),
        )
        cache_messages += lifecycle_messages

    if applicability_json is not None:
        evidence = load_reviewed_applicability(assessment, evidence, applicability_json)

    if cache_directory is not None:
        try:
            allowlist = read_nvd_allowlist(ROOT / "config" / "nvd-allowlist.json")
        except (ValueError, OSError):
            if nvd_mappings is not None:
                raise InputError("NVD allowlist is unavailable or invalid.") from None
            cache_messages += ("NVD allowlist unavailable or invalid; coverage is unassessed.",)
        else:
            evidence, nvd_messages = load_assessment_nvd(
                assessment, evidence, Path(cache_directory), allowlist, nvd_mappings,
                now=now, max_age=timedelta(days=8),
            )
            cache_messages += nvd_messages
    elif nvd_mappings is not None:
        raise InputError("NVD mappings require a saved public-feed cache folder.")

    result = score_assessment(
        assessment,
        evidence,
        AssessmentFreshnessPolicy(
            administrator_observation_max_age=timedelta(
                days=observation_days
            )
        ),
        rules_directory=ROOT / "rules",
        now=now,
    )
    report = build_assessment_report(result)
    report["cache_messages"] = list(cache_messages)
    return report


def generate_uploaded(
    uploads, observation_days, *, cache_directory=None,
    lifecycle_mappings=None, applicability_json=None, nvd_mappings=None,
):
    required = ("checklist_json", "followups_json")
    if any(uploads.get(key) is None for key in required):
        raise InputError("Provide checklist and follow-up JSON files.")
    validate_assessment_uploads(
        *(value for value in uploads.values() if isinstance(value, bytes)),
        lifecycle_mappings, applicability_json, nvd_mappings,
    )
    assessment = read_assessment(**uploads)
    report = evaluate_supplied_assessment(
        assessment, AssessmentEvidence(), observation_days,
        now=datetime.now(timezone.utc), cache_directory=cache_directory,
        lifecycle_mappings=lifecycle_mappings, applicability_json=applicability_json, nvd_mappings=nvd_mappings,
    )
    report["assessment_context"] = {
        "input_mode": "uploaded inventory",
        "notice": (
            "Assessment based on supplied inventory, answers and optional evidence. "
            "Inputs have not been independently verified. Scores remain provisional."
        ),
    }
    return report


def upload_inventory_inputs():
    uploads = {}
    inventory_format = st.radio("Inventory format", ["CSV", "JSON", "Excel workbook"])
    if inventory_format == "Excel workbook":
        workbook = st.file_uploader("Inventory workbook (XLSX)", type=["xlsx"])
        uploads["workbook_xlsx"] = workbook.getvalue() if workbook else None
    else:
        suffix = inventory_format.lower()
        for kind in ("assets", "software", "services"):
            optional = " (optional)" if kind == "services" else ""
            file = st.file_uploader(
                f"{kind.title()} inventory ({inventory_format}){optional}", type=[suffix],
            )
            uploads[f"{kind}_{suffix}"] = file.getvalue() if file else None
    for key, label in (
        ("checklist_json", "Checklist answers (JSON)"),
        ("followups_json", "Follow-up answers (JSON)"),
    ):
        file = st.file_uploader(label, type=["json"])
        uploads[key] = file.getvalue() if file else None
    uploads["medical_devices_present"] = st.selectbox(
        "Are medical devices present?", ["Unknown", "Yes", "No"],
    )
    st.caption(
        "Assets and software plus checklist and follow-up answers are required. "
        "Services are optional; missing coverage stays visible. "
        "Uploaded inventories are evaluated in memory and are not saved to disk."
    )
    return uploads


def main():
    st.set_page_config(page_title="ClinicShield", layout="wide")
    st.title("ClinicShield")
    mode = st.radio("Assessment source", ["Fictional example", "Upload inventory"])
    is_upload = mode == "Upload inventory"
    uploads = {}
    if is_upload:
        st.info("Assess supplied inventories. Scores are provisional and missing evidence stays visible.")
        uploads = upload_inventory_inputs()
        clinic = "uploaded"
    else:
        st.info(
            "Example assessments using fictional clinic inventories. "
            "Scores are provisional and unresolved evidence remains visible."
        )
        st.caption(
            "This preview can use saved public-feed caches, but does not collect "
            "real administrator observations. Optional scenario evidence "
            "is fictional. This does not assess a real clinic."
        )
        clinic_name = st.selectbox("Choose a fictional clinic", list(CLINICS))
        clinic = CLINICS[clinic_name]
    observation_days = int(st.number_input(
        "Administrator observation age limit in days",
        min_value=1,
        max_value=365,
        value=30,
    ))
    st.caption(
        "The observation limit is illustrative, not an approved policy. "
        "Public-feed freshness uses the provisional eight-day limit."
    )

    include_scenario = False
    if not is_upload:
        include_scenario = st.checkbox(
            "Include documented fictional scenario evidence", value=False,
        )
    if include_scenario:
        st.warning(
            "Synthetic scenario evidence is enabled for demonstration. "
            "It is not verified vendor or administrator evidence."
        )

    use_caches = st.checkbox("Load saved public-feed caches", value=False)
    cache_directory = None
    lifecycle_mappings = None
    nvd_mappings = None
    if use_caches:
        cache_directory = st.text_input(
            "Public-feed cache folder", value=str(ROOT / "data" / "cache")
        )
        st.caption(
            "Reads kev.json and epss.json locally. No feeds are downloaded. "
            "Lifecycle mappings use eol-PRODUCT.json; NVD records use the nvd subfolder. No applicability is inferred without reviewed mappings."
        )

        if not include_scenario:
            mapping_upload = st.file_uploader(
                "Reviewed OS lifecycle mappings (JSON)", type=["json"], key=f"lifecycle-{mode}"
            )
            if mapping_upload is not None:
                lifecycle_mappings = mapping_upload.getvalue()
            st.caption(
                "Mappings must match the inventory OS and version exactly. "
                "Extended-support coverage remains unknown."
            )

            nvd_upload = st.file_uploader(
                "Reviewed NVD software mappings (JSON)", type=["json"], key=f"nvd-{mode}"
            )
            if nvd_upload is not None:
                nvd_mappings = nvd_upload.getvalue()
            st.caption(
                "Uses only repository-allowlisted CVEs from the local nvd folder. "
                "Exact reviewed mappings are required; unsupported configurations stay flagged."
            )

    applicability_json = None
    if not include_scenario:
        applicability_upload = st.file_uploader(
            "Reviewed CVE applicability evidence (JSON)", type=["json"], key=f"applicability-{mode}"
        )
        if applicability_upload is not None:
            applicability_json = applicability_upload.getvalue()
        st.caption(
            "Source records must identify the software entry, vendor, product, "
            "affected versions, source URL and timestamps. Unresolved matches stay flagged."
        )

    upload_selection = tuple(
        (key, sha256(value).hexdigest() if isinstance(value, bytes) else value)
        for key, value in sorted(uploads.items())
    )
    selection = (mode, clinic, observation_days, include_scenario, cache_directory,
                 lifecycle_mappings, applicability_json, nvd_mappings, upload_selection)
    if st.session_state.get("report_selection") != selection:
        st.session_state.pop("assessment_report", None)

    button_label = "Generate assessment" if is_upload else "Generate example assessment"
    if st.button(button_label, type="primary"):
        try:
            if is_upload:
                report = generate_uploaded(
                    uploads, observation_days, cache_directory=cache_directory,
                    lifecycle_mappings=lifecycle_mappings, applicability_json=applicability_json, nvd_mappings=nvd_mappings,
                )
            else:
                report = generate_example(
                    clinic, observation_days, include_scenario, cache_directory,
                    lifecycle_mappings, applicability_json, nvd_mappings,
                )
        except (ValueError, OSError):
            st.session_state.pop("assessment_report", None)
            if is_upload:
                st.error(
                    "The uploaded assessment could not be evaluated. "
                    "Provide valid assets/software or a workbook, checklist and follow-up answers. "
                    "Check file formats, required columns, asset links, evidence and size limits."
                )
            else:
                st.error(
                    "The example could not be evaluated. "
                    "Check the sample files, uploaded evidence and rule definitions."
                )
            return

        st.session_state["assessment_report"] = report
        st.session_state["report_selection"] = selection

    report = st.session_state.get("assessment_report")
    if report is None:
        return

    for message in report.get("cache_messages", []):
        st.warning(message)

    score = report["score"]
    st.subheader("Scores within the assessed scope")
    if score["status"] == "provisional":
        st.warning(
            "Provisional score: evidence, coverage, or rule-review "
            "decisions remain unresolved."
        )

    overall, safeguards, exposure = st.columns(3)
    overall.metric("Overall", f"{score['final']}/100", delta=None)
    safeguards.metric("Safeguards", f"{score['safeguards']:.1f}/100")
    exposure.metric("Exposure", f"{score['exposure']:.1f}/100")
    st.text(f"Band: {score['band']}")
    st.caption(
        "Overall weighting: 60% Safeguards and 40% Exposure. "
        "A high score does not resolve missing coverage."
    )

    if score["critical_ceiling"] is not None:
        st.warning(
            f"A confirmed Critical finding limits the overall score "
            f"to {score['critical_ceiling']}."
        )

    for limitation in score["limitations"]:
        st.text(f"- {limitation}")

    with st.expander("Coverage and answers requiring review", expanded=True):
        for issue in report["coverage_issues"]:
            st.text(f"{issue['source_entry_id']}: {issue['message']}")
        for conflict in report["checklist_conflicts"]:
            st.text(
                f"{conflict['rule_id']} at {conflict['source_entry_id']} "
                f"disagrees with a Yes answer to {conflict['question_id']}."
            )

    plan = report.get("fix_first")
    if plan is not None:
        st.subheader("Fix First plan")
        st.caption(plan["notice"])
        for heading in plan["groups"]:
            st.write(heading)
            actions = [item for item in plan["actions"] if item["group"] == heading]
            if not actions:
                st.caption("No confirmed actions assigned to this group.")
            for action in actions:
                label = f"#{action['rank']} | {', '.join(action['rule_ids'])} | {action['entity_id']}"
                with st.expander(label):
                    st.text(
                        f"Priority: {action['priority']:.3g} "
                        f"({action['points']:g} points / effort {action['effort']})"
                    )
                    for recommendation in action["recommendations"]:
                        st.text(recommendation)
                    st.text("Responsible roles: " + ", ".join(action["owners"]))
                    st.text("Estimated cost: " + ", ".join(action["costs"]))
                    ties = action["tie_breakers"]
                    st.caption(
                        f"Tie evidence: confirmed KEV={ties['confirmed_kev']}; "
                        f"reviewed Essential question links={', '.join(ties['essential_questions']) or 'none'}; "
                        f"confirmed patient-information scope={ties['confirmed_patient_information_scope']}."
                    )
        st.write("Verify before planning remediation")
        for item in plan["verification_items"]:
            st.text(f"{', '.join(item['rule_ids'])} | {item['entity_id']}: {item['notice']}")
        if not plan["verification_items"]:
            st.caption("No unresolved finding evidence in this assessment.")

    for heading, confirmed in (
        ("Findings from supplied evidence", True),
        ("Items requiring verification", False),
    ):
        st.subheader(heading)
        selected = [
            finding for finding in report["findings"]
            if (
                finding["status"] == "confirmed_from_supplied_evidence"
            ) is confirmed
        ]
        selected.sort(key=lambda finding: (
            -SEVERITY_POINTS[finding["severity"]],
            finding["scoring_entity_id"],
            finding["issue_key"],
        ))

        if not selected:
            st.caption("No items in this section within the assessed scope.")

        for finding in selected:
            label = (
                f"{finding['severity']} | "
                f"{', '.join(finding['rule_ids'])} | "
                f"{finding['scoring_entity_id']}"
            )
            with st.expander(label):
                st.text(" / ".join(finding["titles"]))
                st.text(f"Scoring category: {finding['scoring_category']}")

                if finding["scoring_category"] == "administrative":
                    st.caption(
                        "No additional Exposure deduction. "
                        "Checklist Safeguards answers are scored once."
                    )
                elif not confirmed:
                    st.caption("No confirmed-risk Exposure deduction.")
                else:
                    st.text(
                        "Exposure risk points before caps and size adjustment: "
                        f"{finding['exposure_points']:g}"
                    )

                st.write("Recommended actions")
                for action in finding["recommendations"]:
                    st.text(action)
                st.text("Responsible roles: " + ", ".join(finding["owners"]))
                st.text("Estimated effort: " + "; ".join(
                    {
                        1: "Under an hour and free",
                        2: "A day of work or a small cost",
                        3: "Vendor involvement, budget, or several weeks",
                    }[value]
                    for value in finding["effort_values"]
                ))
                st.text("Estimated cost: " + ", ".join(
                    value.replace("_", " ")
                    for value in finding["cost_estimates"]
                ))

                st.write("Supporting evidence")
                for source in finding["evidence"]:
                    st.text(
                        f"{source['rule_id']}: "
                        f"{source['status'].replace('_', ' ')}"
                    )
                    st.json(source["details"])

                for context in finding["epss_context"]:
                    if context["current_score"] is None:
                        st.caption("Current EPSS score is unavailable.")
                    else:
                        percent = Decimal(context["current_score"]) * 100
                        st.text(
                            f"EPSS 30-day exploitation probability: "
                            f"{percent:.2f}% as of {context['score_date']}"
                        )
                        st.caption(
                            "Prioritization context, not proof of applicability."
                        )

                for reference in finding["framework_references"]:
                    status = (
                        "Source-checked project mapping"
                        if reference["review_status"] == "reviewed"
                        else "Reference pending validation"
                    )
                    st.text(
                        f"{status}: {reference['framework']} : "
                        f"{reference['reference']}"
                    )
                    st.caption(reference["rationale"])
                    st.text("Source: " + reference["source"])

    st.download_button(
        "Download readable assessment",
        data=render_assessment_text(report),
        file_name=f"clinicshield-{clinic}-assessment.txt",
        mime="text/plain",
    )


if __name__ == "__main__":
    main()