from clinicshield.report_pdf import render_assessment_pdf
from clinicshield.report_exports import render_findings_csv, render_checklist_json
from clinicshield.practice_scoring import practice_lines
from clinicshield.score_explanation import explanation_lines
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
    report["checklist_export"] = {
        "checklist_schema_version": 1,
        "answers": dict(assessment.checklist.answers),
        "followups": dict(assessment.checklist.followups),
        "medical_devices_present": assessment.checklist.medical_devices_present,
    }
    report["cache_messages"] = list(cache_messages)
    return report


def generate_uploaded(
    uploads, observation_days, *, cache_directory=None,
    lifecycle_mappings=None, applicability_json=None, nvd_mappings=None,
):
    required = ("checklist_json",)
    if any(uploads.get(key) is None for key in required):
        raise InputError("Provide checklist JSON. Legacy answers also need a follow-up JSON file.")
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


def render_results(report):
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

    if "score_explanation" in report:
        with st.expander("Why this score"):
            for line in explanation_lines(report["score_explanation"]):
                st.text(line)

    if "practice_scores" in report:
        with st.expander("Practice-area results (draft)"):
            for line in practice_lines(report["practice_scores"]):
                st.text(line)

    with st.expander("Coverage and answers requiring review", expanded=True):
        for issue in report["coverage_issues"]:
            st.text(f"{issue['source_entry_id']}: {issue['message']}")
        for conflict in report["checklist_conflicts"]:
            st.text(
                f"{conflict['rule_id']} at {conflict['source_entry_id']} "
                f"disagrees with a Yes answer to {conflict['question_id']}."
            )

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



def render_fix_first(report, clinic):
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
                    for request in action.get("provider_requests", []):
                        st.caption("Copyable request to the responsible provider or lead")
                        st.code(request, language=None)
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

    st.download_button(
        "Download assessment (PDF)",
        data=render_assessment_pdf(report),
        file_name=f"clinicshield-{clinic}-assessment.pdf",
        mime="application/pdf",
    )

    st.download_button(
        "Download findings (CSV)",
        data=render_findings_csv(report),
        file_name=f"clinicshield-{clinic}-findings.csv",
        mime="text/csv",
    )
    st.caption(
        "CSV includes confirmed and review findings. Exposure points are before "
        "entity caps; they are not predicted score improvement or risk reduction."
    )
    st.download_button(
        "Save checklist (JSON)",
        data=render_checklist_json(report),
        file_name=f"clinicshield-{clinic}-checklist.json",
        mime="application/json",
    )
    st.caption("Saved checklist includes follow-ups and medical-device presence for reuse.")

    st.download_button(
        "Download readable assessment",
        data=render_assessment_text(report),
        file_name=f"clinicshield-{clinic}-assessment.txt",
        mime="text/plain",
    )


def main():
    from clinicshield.guided_ui import run_guided_app
    run_guided_app(st, ROOT, CLINICS, evaluate_supplied_assessment, render_results, render_fix_first)


if __name__ == "__main__":
    main()
