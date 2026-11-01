"""JSON-compatible arithmetic trail for an already computed assessment."""
from fractions import Fraction
from clinicshield.scoring import ESSENTIAL_QUESTIONS, SEVERITY_POINTS


def exact(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator,
            "value": float(value)}


def build_score_explanation(checklist, safeguards, grouped, combined, entities, groups):
    questions = []
    for question, answer in sorted(checklist.answers.items()):
        applicable = question not in safeguards.excluded_questions
        weight = 3 if question in ESSENTIAL_QUESTIONS else 1
        questions.append({"question_id": question, "answer": answer,
                          "applicable": applicable, "weight": weight,
                          "earned": weight if applicable and answer == "Yes" else 0,
                          "available": weight if applicable else 0})
    entity_map = {entity.entity_id: entity for entity in entities}
    group_map = {(group.scoring_entity_id, group.issue_key): group for group in groups}
    technical = []
    totals = {entity.entity_id: Fraction(0) for entity in entities}
    for item in grouped.technical_findings:
        finding = item.finding
        group = group_map[(finding.entity_id, finding.finding_id)]
        entity = entity_map[finding.entity_id]
        phi = Fraction(3, 2) if entity.touches_phi in ("Y", "Unknown") else Fraction(1)
        internet = Fraction(3, 2) if entity.internet_facing == "Y" else Fraction(1)
        medical = Fraction(5, 4) if entity.medical_device is True else Fraction(1)
        technical.append({"entity_id": finding.entity_id, "issue_key": finding.finding_id,
                          "rule_ids": sorted({o.finding.rule.rule_id for o in group.occurrences}),
                          "severity": group.severity, "base_points": SEVERITY_POINTS[group.severity],
                          "multipliers": {"patient_information": exact(phi),
                                          "internet": exact(internet), "medical_device": exact(medical)},
                          "risk_points": exact(finding.risk_points),
                          "unknown_conditions": list(item.unknown_conditions)})
        totals[finding.entity_id] += finding.risk_points
    exposure = grouped.exposure
    capped_total = sum((v for _, v in exposure.capped_entity_points), Fraction(0))
    factor = Fraction(20, exposure.entity_count) if exposure.entity_count > 20 else Fraction(1)
    return {"schema_version": 1,
            "notice": "Arithmetic explains the assessed scope, not complete coverage or safety. "
                      "Unknown answers earn zero safeguards weight; review-only technical evidence "
                      "adds no confirmed Exposure deduction. Administrative findings add no extra "
                      "Exposure deduction. Grouped risks are counted once. Q24 follow-ups are scored "
                      "once through Q24, not as separate questions.",
            "safeguards": {"questions": questions, "earned_weight": safeguards.earned_weight,
                           "applicable_weight": safeguards.applicable_weight,
                           "excluded_questions": list(safeguards.excluded_questions),
                           "unknown_questions": list(safeguards.unknown_questions),
                           "score": exact(safeguards.score)},
            "exposure": {"technical_groups": technical, "entity_count": exposure.entity_count,
                         "entity_cap": 25,
                         "entities": [{"entity_id": key, "before_cap": exact(totals[key]),
                                       "after_cap": exact(value)}
                                      for key, value in exposure.capped_entity_points],
                         "capped_total": exact(capped_total), "size_factor": exact(factor),
                         "adjusted_points": exact(exposure.adjusted_points),
                         "score": exact(exposure.score)},
            "combined": {"safeguards_weight": exact(Fraction(3, 5)),
                         "exposure_weight": exact(Fraction(2, 5)),
                         "raw": exact(combined.raw_score), "rounded": combined.rounded_score,
                         "rounding": "Nearest whole number; exact .5 ties round upward.",
                         "critical_ceiling": combined.critical_ceiling,
                         "critical_findings": list(combined.critical_findings),
                         "final": combined.final_score, "band": combined.band}}


def display_number(number):
    return f"{number['value']:.4f} (exact {number['numerator']}/{number['denominator']})"


def explanation_lines(explanation):
    s, e, c = (explanation[key] for key in ("safeguards", "exposure", "combined"))
    lines = [explanation["notice"],
             f"Safeguards: 100 x {s['earned_weight']} / {s['applicable_weight']} = {display_number(s['score'])}"]
    for q in s["questions"]:
        suffix = "excluded from denominator" if not q["applicable"] else f"earned {q['earned']} of {q['available']}"
        lines.append(f"{q['question_id']}: {q['answer']}; weight {q['weight']}; {suffix}.")
    lines.append(f"Exposure: {e['entity_count']} scoring entities; cap {e['entity_cap']} points per entity.")
    for g in e["technical_groups"]:
        m = g["multipliers"]
        lines.append(f"{g['entity_id']} / {', '.join(g['rule_ids'])}: {g['base_points']} severity points "
                     f"x {m['patient_information']['value']:g} patient-information "
                     f"x {m['internet']['value']:g} internet x {m['medical_device']['value']:g} medical-device "
                     f"= {display_number(g['risk_points'])}; issue {g['issue_key']}.")
        if g["unknown_conditions"]:
            lines.append("Unresolved scoring conditions: " + ", ".join(g["unknown_conditions"]))
    for entity in e["entities"]:
        lines.append(f"{entity['entity_id']}: {display_number(entity['before_cap'])} before cap; "
                     f"{display_number(entity['after_cap'])} after cap.")
    lines.extend([f"Capped total {display_number(e['capped_total'])} x size factor "
                  f"{display_number(e['size_factor'])} = adjusted deduction {display_number(e['adjusted_points'])}.",
                  f"Exposure = max(0, 100 - adjusted deduction) = {display_number(e['score'])}.",
                  f"Combined: 0.6 x Safeguards + 0.4 x Exposure = {display_number(c['raw'])}.",
                  f"Rounded score: {c['rounded']}. {c['rounding']}"])
    if c["critical_ceiling"] is not None:
        lines.append(f"Confirmed Critical ceiling: {c['critical_ceiling']}; responsible finding IDs: "
                     + ", ".join(c["critical_findings"]))
    else:
        lines.append("No confirmed Critical ceiling applied; unresolved evidence still requires review.")
    lines.append(f"Final score: {c['final']}/100; {c['band']}.")
    return lines
