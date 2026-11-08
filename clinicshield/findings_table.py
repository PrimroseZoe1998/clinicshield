"""Read-only findings presentation; does not change scores or action ranks."""
import json
from clinicshield.scoring import SEVERITY_POINTS

CONFIRMED = "confirmed_from_supplied_evidence"


def ordered_findings(report):
    return sorted(report["findings"], key=lambda f: (
        f["status"] != CONFIRMED,
        -SEVERITY_POINTS[f["severity"]],
        -f["exposure_points"],
        f["scoring_entity_id"], f["issue_key"],
    ))


def finding_rows(report, status="All findings"):
    """Stable references across filters connect table rows to detail expanders."""
    rows = []
    for index, finding in enumerate(ordered_findings(report), 1):
        confirmed = finding["status"] == CONFIRMED
        if status == "Confirmed findings" and not confirmed:
            continue
        if status == "Needs review" and confirmed:
            continue
        evidence = "\n".join(
            f"{item['rule_id']} | {item['source_entity_id']} | {item['status']} | "
            + json.dumps(item["details"], ensure_ascii=False, sort_keys=True)
            for item in finding["evidence"]
        )
        rows.append({
            "Ref": f"F{index:03d}",
            "Severity": finding["severity"],
            "Status": "Confirmed from supplied evidence" if confirmed else "Needs review",
            "Finding": " / ".join(finding["titles"]),
            "Entity": finding["scoring_entity_id"],
            "Rules": ", ".join(finding["rule_ids"]),
            "Exposure points before caps": finding["exposure_points"],
            "Evidence": evidence,
        })
    return rows
