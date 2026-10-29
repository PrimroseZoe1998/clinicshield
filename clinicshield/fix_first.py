from fractions import Fraction

from clinicshield.assessment_scoring import ScoredAssessment
from clinicshield.scoring import ESSENTIAL_QUESTIONS, SEVERITY_POINTS


ACTION_GROUPS = (
    "Do today free", "This month low cost", "Ask your vendor", "Policy and training",
)
POLICY_RULES = {"R17", "R20", "R21", "R22", "R23"}
PLAN_NOTICE = (
    "Priority is finding points divided by effort, not an estimated score increase. "
    "Entity caps, overlapping findings and the Critical ceiling affect score changes. "
    "Checklist priorities add no extra score deductions. Ranks compare across groups. "
    "Repeated actions use the highest points and highest effort, not summed priorities. "
    "Essential-goal ties use existing reviewed checklist relationships, with partial coverage; "
    "they do not establish full CPG compliance. Unknown costs require an estimate."
)


def action_group(rule_ids, effort, costs):
    if set(rule_ids) & POLICY_RULES:
        return "Policy and training"
    if effort == 1 and set(costs) == {"none"}:
        return "Do today free"
    if effort <= 2 and costs and set(costs) <= {"none", "low"}:
        return "This month low cost"
    return "Ask your vendor"


def rank_actions(candidates):
    """Consolidate identical action sets on one entity without summing risks."""
    merged = {}
    for candidate in candidates:
        key = (candidate["entity_id"], tuple(sorted(set(candidate["recommendations"]))))
        if key not in merged:
            merged[key] = {
                **candidate,
                "rule_ids": set(candidate["rule_ids"]),
                "issue_keys": set(candidate["issue_keys"]),
                "owners": set(candidate["owners"]),
                "costs": set(candidate["costs"]),
                "essential_questions": set(candidate["essential_questions"]),
            }
            continue
        item = merged[key]
        item["points"] = max(item["points"], candidate["points"])
        item["effort"] = max(item["effort"], candidate["effort"])
        for field in ("rule_ids", "issue_keys", "owners", "costs", "essential_questions"):
            item[field].update(candidate[field])
        item["kev"] = item["kev"] or candidate["kev"]
        item["touches_phi"] = item["touches_phi"] or candidate["touches_phi"]

    def priority(item):
        return Fraction(item["points"]) / item["effort"]

    ordered = sorted(merged.values(), key=lambda item: (
        -priority(item), -item["kev"], -bool(item["essential_questions"]),
        -item["touches_phi"], tuple(sorted(item["rule_ids"])),
        item["entity_id"], tuple(sorted(item["issue_keys"])),
    ))
    output = []
    for rank, item in enumerate(ordered, 1):
        output.append({
            "rank": rank, "entity_id": item["entity_id"],
            "rule_ids": sorted(item["rule_ids"]), "issue_keys": sorted(item["issue_keys"]),
            "recommendations": sorted(set(item["recommendations"])),
            "owners": sorted(item["owners"]), "costs": sorted(item["costs"]),
            "points": float(item["points"]), "effort": item["effort"],
            "priority": float(priority(item)), "priority_exact": str(priority(item)),
            "group": action_group(item["rule_ids"], item["effort"], item["costs"]),
            "tie_breakers": {
                "confirmed_kev": item["kev"],
                "essential_questions": sorted(item["essential_questions"]),
                "confirmed_patient_information_scope": item["touches_phi"],
            },
        })
    return output


def build_fix_first(result: ScoredAssessment) -> dict:
    entities = {entity.entity_id: entity for entity in result.evaluation.scoring_inventory.entities}
    technical = {
        (item.finding.entity_id, item.finding.finding_id): item.finding.risk_points
        for item in result.grouped_scoring.technical_findings
    }
    candidates = []
    verification = []
    for group in result.groups:
        confirmed = [item for item in group.occurrences if item.finding.observation.status == "confirmed"]
        unresolved = [item for item in group.occurrences if item.finding.observation.status == "needs_review"]
        if unresolved:
            verification.append({
                "entity_id": group.scoring_entity_id, "issue_key": group.issue_key,
                "rule_ids": sorted({item.finding.rule.rule_id for item in unresolved}),
                "recommendations": sorted({item.finding.rule.fix for item in unresolved}),
                "notice": "Verify this evidence before treating it as a confirmed gap.",
            })
        if not confirmed:
            continue
        points = (
            technical[(group.scoring_entity_id, group.issue_key)]
            if group.scoring_category == "technical" else Fraction(SEVERITY_POINTS[group.severity])
        )
        essential = set()
        kev = False
        phi = False
        for item in confirmed:
            details = dict(item.finding.observation.evidence)
            essential.update(key for key in ESSENTIAL_QUESTIONS if details.get(key) == "No")
            # Existing reviewed question relationships for inventory-based MFA gaps.
            if item.finding.rule.rule_id in {"R12", "R13"} and details.get("mfa_enabled") == "N":
                essential.add({"R12": "Q01", "R13": "Q07"}[item.finding.rule.rule_id])
            kev |= (item.finding.rule.rule_id == "R01"
                    and details.get("kev_status") == "listed"
                    and details.get("applicability") == "match")
            entity = entities.get(item.scoring_entity_id)
            asset = entities.get("device:" + details.get("asset_id", ""))
            phi |= any(value is not None and value.touches_phi == "Y" for value in (entity, asset))
        candidates.append({
            "entity_id": group.scoring_entity_id, "issue_keys": [group.issue_key],
            "rule_ids": sorted({item.finding.rule.rule_id for item in confirmed}),
            "recommendations": sorted({item.finding.rule.fix for item in confirmed}),
            "owners": sorted({item.finding.rule.owner for item in confirmed}),
            "costs": sorted({item.finding.rule.cost for item in confirmed}),
            "points": points, "effort": max(item.finding.rule.effort for item in confirmed),
            "kev": kev, "essential_questions": sorted(essential), "touches_phi": phi,
        })
    return {
        "notice": PLAN_NOTICE, "groups": list(ACTION_GROUPS),
        "actions": rank_actions(candidates),
        "verification_items": sorted(verification, key=lambda item: (item["rule_ids"], item["entity_id"], item["issue_key"])),
    }
