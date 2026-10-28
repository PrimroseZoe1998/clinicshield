from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import streamlit as st

from clinicshield.assessment_evidence import (
    AssessmentEvidence,
    AssessmentFreshnessPolicy,
)
from clinicshield.assessment_input import read_assessment
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


def generate_example(clinic, observation_days):
    folder = ROOT / "samples" / clinic
    services = folder / "services.csv"

    assessment = read_assessment(
        checklist_json=(folder / "checklist.json").read_bytes(),
        followups_json=(folder / "followups.json").read_bytes(),
        assets_csv=(folder / "assets.csv").read_bytes(),
        software_csv=(folder / "software.csv").read_bytes(),
        services_csv=services.read_bytes() if services.exists() else None,
    )
    result = score_assessment(
        assessment,
        AssessmentEvidence(),
        AssessmentFreshnessPolicy(
            administrator_observation_max_age=timedelta(
                days=observation_days
            )
        ),
        rules_directory=ROOT / "rules",
        now=datetime.now(timezone.utc),
    )
    return build_assessment_report(result)


def main():
    st.set_page_config(page_title="ClinicShield", layout="wide")
    st.title("ClinicShield")
    st.info(
        "Example assessments using fictional clinic inventories. "
        "Scores are provisional and unresolved evidence remains visible."
    )
    st.caption(
        "This preview does not load threat-intelligence caches or "
        "administrator observations. It does not assess a real clinic."
    )

    clinic_name = st.selectbox(
        "Choose a fictional clinic",
        list(CLINICS),
    )
    clinic = CLINICS[clinic_name]
    observation_days = int(st.number_input(
        "Example administrator observation age limit in days",
        min_value=1,
        max_value=365,
        value=30,
    ))
    st.caption(
        "The observation limit is illustrative, not an approved policy. "
        "Public-feed freshness uses the provisional eight-day limit."
    )

    selection = (clinic, observation_days)
    if st.session_state.get("report_selection") != selection:
        st.session_state.pop("assessment_report", None)

    if st.button("Generate example assessment", type="primary"):
        try:
            report = generate_example(clinic, observation_days)
        except (ValueError, OSError):
            st.error(
                "The example could not be evaluated. "
                "Check the sample files and rule definitions."
            )
            return

        st.session_state["assessment_report"] = report
        st.session_state["report_selection"] = selection

    report = st.session_state.get("assessment_report")
    if report is None:
        return

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
        st.text(f"• {limitation}")

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
                f"{finding['severity']} · "
                f"{', '.join(finding['rule_ids'])} · "
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
                        "Reviewed reference"
                        if reference["review_status"] == "reviewed"
                        else "Reference pending validation"
                    )
                    st.text(
                        f"{status}: {reference['framework']} — "
                        f"{reference['reference']}"
                    )

    st.download_button(
        "Download readable assessment",
        data=render_assessment_text(report),
        file_name=f"clinicshield-{clinic}-assessment.txt",
        mime="text/plain",
    )


if __name__ == "__main__":
    main()