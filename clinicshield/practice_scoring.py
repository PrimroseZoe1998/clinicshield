"""Draft additive practice views; never feed these values back to global scoring."""
import json
from fractions import Fraction

from clinicshield.score_explanation import exact
from clinicshield.scoring import SafeguardsScore, combine_scores, score_exposure

PRACTICES = ((1, 'Email protection', ('Q01', 'Q02'), ('R12',)), (2, 'Endpoint protection', ('Q03', 'Q04', 'Q05'), ('R05', 'R15')), (3, 'Access management', ('Q06', 'Q07', 'Q08', 'Q09'), ('R10', 'R13', 'R14')), (4, 'Data protection', ('Q10', 'Q11', 'Q12', 'Q13'), ('R16', 'R17')), (5, 'Asset management', ('Q14',), ('R24',)), (6, 'Network management', ('Q15', 'Q16', 'Q17'), ('R06', 'R07', 'R09', 'R18', 'R19')), (7, 'Vulnerability management', ('Q18', 'Q19'), ('R01', 'R02', 'R03', 'R04', 'R08')), (8, 'Incident response', ('Q20', 'Q21', 'Q22'), ('R20', 'R21')), (9, 'Network-connected medical devices', ('Q23',), ('R11',)), (10, 'Security oversight and governance', ('Q24', 'Q25'), ('R22', 'R23')))

NOTICE = (
    "These practice views are a draft. They use project groups, not an official "
    "Health Industry Cybersecurity Practices (HICP) crosswalk. Safeguards uses your "
    "answers. Exposure shows known deductions only. No confirmed technical findings "
    "means unassessed, not 100. Both parts are needed for a combined score. "
    "All scores are provisional: checks are still open. Practice scores do not add "
    "or average into the overall score."
)


def build_practice_scores(result):
    questions = {q["question_id"]: q for q in result.explanation["safeguards"]["questions"]}
    rule_area = {rule: identifier for identifier, _, _, rules in PRACTICES for rule in rules}
    group_areas = {}
    for group in result.groups:
        areas = {rule_area[item.finding.rule.rule_id] for item in group.occurrences}
        if len(areas) != 1:
            raise ValueError("Grouped risk requires one primary practice assignment.")
        group_areas[(group.scoring_entity_id, group.issue_key)] = areas.pop()
    entities = [entity.entity_id for entity in result.evaluation.scoring_inventory.entities]
    rows = []
    for identifier, name, question_ids, rules in PRACTICES:
        selected = [dict(questions[q]) for q in question_ids]
        available = sum(q["available"] for q in selected)
        earned = sum(q["earned"] for q in selected)
        s = SafeguardsScore(earned, available, (), ()) if available else None
        groups = [g for g in result.groups
                  if group_areas[(g.scoring_entity_id, g.issue_key)] == identifier]
        technical = [item.finding for item in result.grouped_scoring.technical_findings
                     if group_areas[(item.finding.entity_id, item.finding.finding_id)] == identifier]
        review = [g for g in groups if any(o.finding.observation.status == "needs_review"
                                           for o in g.occurrences)]
        critical = tuple(sorted(json.dumps([g.scoring_entity_id, g.issue_key], separators=(",", ":"))
                                for g in groups if g.has_confirmed_gap and g.severity == "Critical"))
        exposure = score_exposure(entities, technical) if technical else None
        combined = combine_scores(s, exposure, open_critical_findings=critical) if s is not None and exposure is not None else None
        totals = {key: Fraction(0) for key in entities}
        for finding in technical:
            totals[finding.entity_id] += finding.risk_points
        status = "not_applicable" if not available and not groups else "draft_provisional"
        rows.append({"practice_id": identifier, "name": name, "status": status,
                     "question_ids": list(question_ids), "primary_rule_ids": list(rules),
                     "safeguards": {"score": exact(s.score) if s else None,
                                    "earned_weight": earned, "applicable_weight": available,
                                    "unknown_questions": [q["question_id"] for q in selected if q["applicable"] and q["answer"] == "Unknown"],
                                    "questions": selected},
                     "exposure": {"status": "known_deductions_only" if exposure else "unassessed",
                                  "score": exact(exposure.score) if exposure else None,
                                  "entity_count": len(entities), "entity_cap": 25,
                                  "size_factor": exact(Fraction(20, len(entities)) if len(entities) > 20 else 1),
                                  "technical_groups": [{"entity_id": f.entity_id, "issue_key": f.finding_id,
                                                        "risk_points": exact(f.risk_points)} for f in technical],
                                  "entities": [{"entity_id": key, "before_cap": exact(totals[key]), "after_cap": exact(value)}
                                               for key, value in exposure.capped_entity_points] if exposure else [],
                                  "adjusted_points": exact(exposure.adjusted_points) if exposure else None},
                     "combined": {"score": combined.final_score if combined else None,
                                  "raw": exact(combined.raw_score) if combined else None,
                                  "rounded": combined.rounded_score if combined else None,
                                  "band": combined.band if combined else None,
                                  "critical_ceiling": 69 if critical else None,
                                  "critical_findings": list(critical)},
                     "review_group_count": len(review),
                     "coverage_issues": [{"topic": issue.topic, "source_entry_id": issue.source_entry_id,
                                          "message": issue.message} for issue in result.evaluation.coverage_issues],
                     "limitations": ["Global coverage warnings remain relevant; no practice-wide completeness is established.",
                                     "Scores use primary project assignments and independently capped practice views.",
                                     "A missing component is not replaced or reweighted."]})
    return {"schema_version": 1, "mapping_version": "draft-v1", "review_status": "draft",
            "notice": NOTICE, "practices": rows}


def practice_lines(data):
    lines = [data["notice"]]
    for row in data["practices"]:
        s, e, c = row["safeguards"], row["exposure"], row["combined"]
        label = f"{row['practice_id']}. {row['name']} [{row['status'].replace('_', ' ')}]"
        safeguards = f"{s['score']['value']:.2f}/100 ({s['earned_weight']}/{s['applicable_weight']} weight)" if s["score"] else "not applicable (no applicable questions)"
        exposure = f"{e['score']['value']:.2f}/100; known deductions only" if e["score"] else "unassessed"
        combined = f"{c['score']}/100; {c['band']}" if c["score"] is not None else "unavailable; both components required"
        lines.extend([label, "Safeguards: " + safeguards, "Exposure: " + exposure, "Combined: " + combined,
                      f"Inventory denominator: {e['entity_count']} entities; size factor {e['size_factor']['numerator']}/{e['size_factor']['denominator']}; cap {e['entity_cap']} points per entity.",
                      f"Review groups: {row['review_group_count']}; assessment coverage warnings: {len(row['coverage_issues'])}."])
        if s["unknown_questions"]:
            lines.append("Unknown answers earning zero: " + ", ".join(s["unknown_questions"]))
        if c["critical_ceiling"] is not None:
            lines.append("Practice Critical ceiling: 69; responsible groups: " + ", ".join(c["critical_findings"]))
        lines.extend(row["limitations"])
    return lines
