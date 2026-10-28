from clinicshield.assessment_scoring import ScoredAssessment


def build_assessment_report(result: ScoredAssessment) -> dict:
    """Build JSON-compatible report data without writing files."""
    scored_groups = {
        (item.finding.entity_id, item.finding.finding_id): item
        for item in result.grouped_scoring.technical_findings
    }
    enriched = {
        id(linked.finding): linked.enrichment
        for linked in result.evaluation.findings
        if linked.enrichment is not None
    }
    findings = []

    for group in result.groups:
        scored = scored_groups.get((
            group.scoring_entity_id,
            group.issue_key,
        ))
        evidence = []
        recommendations = []
        framework_references = []
        epss_context = []

        for item in group.occurrences:
            finding = item.finding
            rule = finding.rule

            evidence.append({
                "rule_id": rule.rule_id,
                "status": finding.observation.status,
                "source_entity_id": finding.observation.entity_id,
                "details": dict(finding.observation.evidence),
                "grouping_basis": item.grouping_basis,
            })

            if rule.fix not in recommendations:
                recommendations.append(rule.fix)

            for reference in rule.framework_references:
                entry = {
                    "framework": reference.framework,
                    "reference": reference.reference,
                    "source": reference.source,
                    "rationale": reference.rationale,
                    "review_status": reference.review_status,
                }
                if entry not in framework_references:
                    framework_references.append(entry)

            enrichment = enriched.get(id(finding))
            if enrichment is not None:
                lookup = enrichment.epss
                record = lookup.record
                priority = enrichment.epss_for_priority
                epss_context.append({
                    "status": lookup.status,
                    "cve": record.cve if record is not None else None,
                    "current_score": (
                        str(record.epss)
                        if record is not None
                        and lookup.status == "available"
                        else None
                    ),
                    "current_percentile": (
                        str(record.percentile)
                        if record is not None
                        and lookup.status == "available"
                        else None
                    ),
                    "priority_score": (
                        str(priority) if priority is not None else None
                    ),
                    "score_date": (
                        lookup.score_date.isoformat()
                        if lookup.score_date is not None else None
                    ),
                    "retrieved_at": (
                        lookup.retrieved_at.isoformat()
                        if lookup.retrieved_at is not None else None
                    ),
                    "source_url": lookup.source_url,
                    "model_version": lookup.model_version,
                    "review_reasons": list(lookup.reasons),
                })

        findings.append({
            "scoring_entity_id": group.scoring_entity_id,
            "issue_key": group.issue_key,
            "rule_ids": sorted({
                item.finding.rule.rule_id
                for item in group.occurrences
            }),
            "titles": list(dict.fromkeys(
                item.finding.rule.title
                for item in group.occurrences
            )),
            "status": (
                "confirmed_from_supplied_evidence"
                if group.has_confirmed_gap else "needs_review"
            ),
            "severity": group.severity,
            "scoring_category": group.scoring_category,
            "exposure_points": (
                float(scored.finding.risk_points)
                if scored is not None else 0.0
            ),
            "unknown_scoring_conditions": (
                list(scored.unknown_conditions)
                if scored is not None else []
            ),
            "evidence": evidence,
            "recommendations": recommendations,
            "owners": sorted({
                item.finding.rule.owner for item in group.occurrences
            }),
            "effort_values": sorted({
                item.finding.rule.effort for item in group.occurrences
            }),
            "cost_estimates": sorted({
                item.finding.rule.cost for item in group.occurrences
            }),
            "framework_references": framework_references,
            "epss_context": epss_context,
        })

    policy = result.evaluation.freshness_policy

    return {
        "report_schema_version": 1,
        "evaluated_at": result.evaluation.evaluated_at.isoformat(),
        "score": {
            "status": "provisional" if result.is_provisional else "assessed_scope",
            "final": result.combined.final_score,
            "band": result.combined.band,
            "raw": float(result.combined.raw_score),
            "safeguards": float(result.safeguards.score),
            "exposure": float(result.grouped_scoring.exposure.score),
            "critical_ceiling": result.combined.critical_ceiling,
            "critical_findings": list(result.combined.critical_findings),
            "limitations": list(result.score_limitations),
        },
        "freshness_policy": {
            "public_feed_max_age_seconds": policy.public_feed_max_age.total_seconds(),
            "administrator_observation_max_age_seconds": (
                policy.administrator_observation_max_age.total_seconds()
            ),
        },
        "coverage_issues": [
            {
                "source_entry_id": issue.source_entry_id,
                "topic": issue.topic,
                "message": issue.message,
            }
            for issue in result.evaluation.coverage_issues
        ],
        "checklist_conflicts": [
            {
                "rule_id": conflict.rule_id,
                "source_entry_id": conflict.source_entry_id,
                "question_id": conflict.question_id,
            }
            for conflict in result.checklist_conflicts
        ],
        "findings": findings,
    }