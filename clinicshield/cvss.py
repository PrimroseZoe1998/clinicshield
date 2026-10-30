"""Offline interpretation of source-reported CVSS 3.1 base assessments."""
import json
import math

BASE = {"AV": "NALP", "AC": "LH", "PR": "NLH", "UI": "NR",
        "S": "UC", "C": "HLN", "I": "HLN", "A": "HLN"}
OPTIONAL = {"E": "XHFPU", "RL": "XUWTO", "RC": "XCRU",
            "CR": "XHML", "IR": "XHML", "AR": "XHML",
            "MAV": "XNALP", "MAC": "XLH", "MPR": "XNLH", "MUI": "XNR",
            "MS": "XUC", "MC": "XNLH", "MI": "XNLH", "MA": "XNLH"}


def severity(score):
    if score == 0:
        return "NONE"
    if score < 4:
        return "LOW"
    if score < 7:
        return "MEDIUM"
    if score < 9:
        return "HIGH"
    return "CRITICAL"


def valid_vector(vector):
    if not isinstance(vector, str) or len(vector) > 512:
        return False
    parts = vector.split("/")
    if parts[0] != "CVSS:3.1":
        return False
    values = {}
    for part in parts[1:]:
        pair = part.split(":")
        if len(pair) != 2:
            return False
        key, value = pair
        allowed = {**BASE, **OPTIONAL}.get(key, "")
        if key in values or len(value) != 1 or value not in allowed:
            return False
        values[key] = value
    return BASE.keys() <= values.keys()


def interpret_cvss(record):
    """Retain every supported source assessment; never infer applicability/risk."""
    metrics = record.get("metrics")
    if metrics is None or metrics == {}:
        return "CVSS unavailable: no source metrics supplied; not a zero score."
    if not isinstance(metrics, dict):
        return "CVSS requires review: invalid metrics container."
    assessments, issues = [], []
    for key, rows in metrics.items():
        if key != "cvssMetricV31":
            issues.append("Unsupported metric family; raw cache retained.")
            continue
        if not isinstance(rows, list) or not rows:
            issues.append("CVSS 3.1 assessment list missing or invalid.")
            continue
        if len(rows) > 100:
            issues.append("CVSS 3.1 assessment limit exceeded; list not interpreted.")
            continue
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("cvssData"), dict):
                issues.append("Malformed CVSS 3.1 assessment.")
                continue
            data = row["cvssData"]
            score, source = data.get("baseScore"), row.get("source")
            valid_score = (type(score) in (int, float) and 0 <= score <= 10
                           and math.isfinite(score) and round(score, 1) == score)
            if (not valid_score or data.get("version") != "3.1"
                    or not valid_vector(data.get("vectorString"))
                    or not isinstance(source, str) or not source.strip() or len(source) > 200
                    or row.get("type") not in ("Primary", "Secondary")):
                issues.append("Malformed CVSS 3.1 source, type, score, version or vector.")
                continue
            rating = severity(score)
            if data.get("baseSeverity") != rating:
                issues.append("CVSS 3.1 source severity disagrees with score band.")
                continue
            assessments.append({"version": "3.1", "source": source,
                                "type": row["type"], "base_score": score,
                                "severity": rating, "vector": data["vectorString"]})
    return json.dumps({"status": "requires_review" if issues else "available",
                       "assessments": assessments, "issues": issues,
                       "limits": "Source-reported base scores; not recalculated from vectors. "
                       "No applicability, exploitation probability or clinic risk inferred. "
                       "Source freshness and applicability are assessed separately; "
                       "ClinicShield rule severity and score are unchanged."}, sort_keys=True)
