from decimal import Decimal


EFFORT_LABELS = {
    1: "Under an hour and free",
    2: "A day of work or a small cost",
    3: "Vendor involvement, budget, or several weeks",
}


def render_assessment_text(report: dict) -> str:
    """Format assessment results as plain text without writing files."""
    score = report["score"]
    lines = [
        "ClinicShield assessment",
        f"Assessment time: {report['evaluated_at']}",
        "",
        f"Overall score: {score['final']}/100 — {score['band']}",
        f"Score status: {score['status'].replace('_', ' ')}",
        f"Safeguards score: {score['safeguards']:.1f}/100",
        f"Exposure score: {score['exposure']:.1f}/100",
        "Overall weighting: 60% Safeguards and 40% Exposure.",
    ]

    lines.extend(report.get("cache_messages", []))

    context = report.get("assessment_context")
    if context is not None:
        lines[1:1] = [f"Input mode: {context['input_mode']}", context["notice"], ""]

    example = report.get("example_context")
    if example is not None:
        lines[1:1] = [
            f"Fictional clinic: {example['clinic']}",
            f"Evidence mode: {example['evidence_mode']}",
            example["notice"],
            "",
        ]
        
    if score["critical_ceiling"] is not None:
        lines.append(
            f"A confirmed Critical finding limits the overall score "
            f"to {score['critical_ceiling']}."
        )

    lines.extend([
        "",
        "What this score covers",
        "The score reflects the supplied evidence and assessed scope.",
        "Missing coverage or an informational finding does not establish safety.",
    ])
    for limitation in score["limitations"]:
        lines.append(f"- {limitation}")

    policy = report["freshness_policy"]
    lines.extend([
        "",
        "Evidence age policy",
        f"Public feeds: {policy['public_feed_max_age_seconds'] / 86400:g} days",
        "Administrator observations: "
        f"{policy['administrator_observation_max_age_seconds'] / 86400:g} days",
    ])

    if report["coverage_issues"]:
        lines.extend(["", "Coverage requiring attention"])
        for issue in report["coverage_issues"]:
            lines.append(
                f"- {issue['source_entry_id']}: {issue['message']}"
            )

    if report["checklist_conflicts"]:
        lines.extend(["", "Answers that need reconciliation"])
        for conflict in report["checklist_conflicts"]:
            lines.append(
                f"- {conflict['rule_id']} at {conflict['source_entry_id']} "
                f"disagrees with a Yes answer to {conflict['question_id']}. "
                "Review both evidence sources."
            )

    for section, confirmed in (
        ("Findings from supplied evidence", True),
        ("Items requiring verification", False),
    ):
        selected = [
            finding for finding in report["findings"]
            if (
                finding["status"] == "confirmed_from_supplied_evidence"
            ) is confirmed
        ]
        lines.extend(["", section])

        if not selected:
            lines.append("No items in this section within the assessed scope.")
            continue

        for number, finding in enumerate(selected, start=1):
            lines.extend([
                "",
                f"{number}. {' / '.join(finding['titles'])}",
                f"Rules: {', '.join(finding['rule_ids'])}",
                f"Entity: {finding['scoring_entity_id']}",
                f"Severity: {finding['severity']}",
                f"Scoring category: {finding['scoring_category']}",
            ])

            if finding["scoring_category"] == "administrative":
                lines.append(
                    "No additional Exposure deduction; checklist Safeguards "
                    "answers are scored once."
                )
            elif not confirmed:
                lines.append("No confirmed-risk Exposure deduction.")
            else:
                lines.append(
                    f"Exposure risk points before entity caps and size "
                    f"adjustment: {finding['exposure_points']:g}"
                )

            lines.append("Evidence:")
            for source in finding["evidence"]:
                lines.append(
                    f"  {source['rule_id']} — "
                    f"{source['status'].replace('_', ' ')}"
                )
                for key, value in source["details"].items():
                    if value:
                        label = key.replace("_", " ").capitalize()
                        lines.append(f"    {label}: {value}")

            lines.append("Recommended actions:")
            lines.extend(
                f"  - {action}" for action in finding["recommendations"]
            )
            lines.append(f"Responsible roles: {', '.join(finding['owners'])}")
            lines.append("Estimated effort: " + "; ".join(
                EFFORT_LABELS[value] for value in finding["effort_values"]
            ))
            lines.append("Estimated cost: " + ", ".join(
                value.replace("_", " ")
                for value in finding["cost_estimates"]
            ))

            for context in finding["epss_context"]:
                if context["current_score"] is not None:
                    percent = Decimal(context["current_score"]) * 100
                    lines.append(
                        f"EPSS 30-day exploitation probability: {percent:.2f}% "
                        f"as of {context['score_date']}."
                    )
                    lines.append(
                        "EPSS is prioritization context, not proof of "
                        "applicability or exploitation of this organization."
                    )
                else:
                    lines.append(
                        f"Current EPSS score unavailable: {context['status']}."
                    )

            for reference in finding["framework_references"]:
                label = (
                    "Reviewed framework reference"
                    if reference["review_status"] == "reviewed"
                    else "Framework reference pending validation"
                )
                lines.append(
                    f"{label}: {reference['framework']} — "
                    f"{reference['reference']}"
                )

    return "\n".join(lines) + "\n"