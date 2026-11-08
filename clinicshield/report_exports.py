"""In-memory assessment exports. No uploaded data is persisted."""
import csv
import io
import json

from clinicshield.checklist_input import read_checklist


CSV_FIELDS = (
    "evaluated_at", "score_status", "score_limitations", "coverage_issues",
    "example_context", "scoring_entity_id", "issue_key", "rule_ids", "titles",
    "status", "severity", "scoring_category", "exposure_points_before_entity_cap",
    "unknown_scoring_conditions", "evidence", "recommendations", "owners",
    "effort_values", "cost_estimates", "framework_references", "epss_context",
)


def _cell(value):
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    text = str(value) if value is not None else ""
    # Quoting alone does not stop spreadsheet formula interpretation.
    if text.lstrip().startswith(("=", "+", "-", "@")) or text.startswith(("\t", "\r", "\n")):
        text = "'" + text
    return text


def render_findings_csv(report: dict) -> str:
    """One row per grouped finding, retaining evidence and uncertainty as JSON cells."""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for finding in report["findings"]:
        row = {key: finding.get(key, "") for key in CSV_FIELDS}
        row.update(
            evaluated_at=report["evaluated_at"],
            score_status=report["score"]["status"],
            score_limitations=report["score"]["limitations"],
            coverage_issues=report["coverage_issues"],
            example_context=report.get("example_context", {}),
            exposure_points_before_entity_cap=finding["exposure_points"],
        )
        writer.writerow({key: _cell(value) for key, value in row.items()})
    return output.getvalue()


def render_checklist_json(report: dict) -> str:
    """Export a validated, reusable checklist bundle with no inventory or evidence."""
    data = json.dumps(report["checklist_export"], ensure_ascii=False, indent=2, sort_keys=True)
    read_checklist(data.encode("utf-8"))
    return data + "\n"
