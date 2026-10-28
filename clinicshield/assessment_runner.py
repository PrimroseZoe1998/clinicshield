from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from clinicshield import rule_engine as engine
from clinicshield.assessment_evidence import (
    AssessmentEvidence,
    AssessmentFreshnessPolicy,
)
from clinicshield.assessment_evidence_links import validate_evidence_links
from clinicshield.assessment_input import AssessmentInput
from clinicshield.feed_freshness import check_feed_freshness
from clinicshield.inventory import ScoringInventory, build_scoring_inventory
from clinicshield.rule_catalog import load_rule_catalog
from clinicshield.vulnerability_enrichment import (
    EnrichedVulnerabilityFinding,
    enrich_vulnerability_finding,
)


@dataclass(frozen=True)
class AssessmentFinding:
    finding: engine.RuleFinding
    scoring_entity_id: str
    source_entry_id: str
    enrichment: EnrichedVulnerabilityFinding | None = None


@dataclass(frozen=True)
class CoverageIssue:
    source_entry_id: str
    topic: str
    message: str


@dataclass(frozen=True)
class AssessmentEvaluation:
    findings: tuple[AssessmentFinding, ...]
    scoring_inventory: ScoringInventory
    coverage_issues: tuple[CoverageIssue, ...]
    freshness_policy: AssessmentFreshnessPolicy
    evaluated_at: datetime
    rules_loaded: int


def evaluate_assessment(
    assessment: AssessmentInput,
    evidence: AssessmentEvidence,
    policy: AssessmentFreshnessPolicy,
    *,
    rules_directory: Path,
    now: datetime,
) -> AssessmentEvaluation:
    """Evaluate rules offline without saving or logging inventory data."""
    feed_age = policy.public_feed_max_age
    observation_age = policy.administrator_observation_max_age
    check_feed_freshness(None, now=now, max_age=feed_age)

    scoring = build_scoring_inventory(assessment.inventory)
    validate_evidence_links(assessment, evidence)
    rules = load_rule_catalog(rules_directory)
    inventory = assessment.inventory
    checklist = assessment.checklist
    assets = {asset.asset_id: asset for asset in inventory.assets}
    findings = []
    coverage = []

    def collect(finding, scoring_entity_id, source_entry_id):
        if finding is None:
            return

        enrichment = None
        if finding.rule.rule_id in {"R01", "R02"}:
            enrichment = enrich_vulnerability_finding(
                finding,
                evidence.epss_snapshot,
                now=now,
                max_age=feed_age,
                max_score_age_days=feed_age.days,
            )

        findings.append(AssessmentFinding(
            finding=finding,
            scoring_entity_id=scoring_entity_id,
            source_entry_id=source_entry_id,
            enrichment=enrichment,
        ))

    if not inventory.services:
        coverage.append(CoverageIssue(
            "assessment",
            "services",
            "No service inventory is available; network services are unassessed.",
        ))

    for name, snapshot in (
        ("KEV", evidence.kev_snapshot),
        ("EPSS", evidence.epss_snapshot),
    ):
        if snapshot is None:
            coverage.append(CoverageIssue(
                "assessment",
                name,
                f"{name} cache is unavailable; missing coverage is not safety.",
            ))

    for index, _ in enumerate(inventory.software, start=1):
        entry_id = f"software:{index}"
        if not evidence.vulnerabilities.get(entry_id):
            coverage.append(CoverageIssue(
                entry_id,
                "vulnerability_applicability",
                "No applicability records supplied; CVE coverage is unassessed.",
            ))

    for index, service in enumerate(inventory.services, start=1):
        if service.asset_id not in assets:
            coverage.append(CoverageIssue(
                f"service:{index}",
                "asset_association",
                "Service has no matching asset; asset-dependent checks are unassessed.",
            ))

    for rule in rules:
        key = (rule.rule_id, rule.handler, rule.kind)

        if key in engine.CHECKLIST_HANDLERS:
            collect(
                engine.evaluate_checklist_rule(rule, checklist),
                "assessment",
                "checklist",
            )

        elif key in engine.ASSET_HANDLERS:
            for asset in inventory.assets:
                collect(
                    engine.evaluate_asset_rule(rule, asset),
                    f"device:{asset.asset_id}",
                    f"asset:{asset.asset_id}",
                )

        elif key in engine.LIFECYCLE_HANDLERS:
            for asset in inventory.assets:
                collect(
                    engine.evaluate_asset_lifecycle_rule(
                        rule, asset,
                        evidence.os_support.get(asset.asset_id),
                        now=now, max_age=feed_age,
                    ),
                    f"device:{asset.asset_id}",
                    f"asset:{asset.asset_id}",
                )

        elif key in engine.CREDENTIAL_HANDLERS:
            for asset in inventory.assets:
                collect(
                    engine.evaluate_asset_credential_rule(
                        rule, asset,
                        evidence.default_passwords.get(asset.asset_id),
                        now=now, max_age=observation_age,
                    ),
                    f"device:{asset.asset_id}",
                    f"asset:{asset.asset_id}",
                )

        elif key in engine.SEGMENTATION_HANDLERS:
            for asset in inventory.assets:
                collect(
                    engine.evaluate_asset_segmentation_rule(
                        rule, asset,
                        evidence.medical_separation.get(asset.asset_id),
                        now=now, max_age=observation_age,
                    ),
                    f"device:{asset.asset_id}",
                    f"asset:{asset.asset_id}",
                )

        elif (
            key in engine.SERVICE_HANDLERS
            or key in engine.SERVICE_CHECKLIST_HANDLERS
            or key in engine.ASSET_SERVICE_LIFECYCLE_HANDLERS
        ):
            for index, service in enumerate(inventory.services):
                if key in engine.SERVICE_HANDLERS:
                    finding = engine.evaluate_service_rule(rule, service)
                elif key in engine.SERVICE_CHECKLIST_HANDLERS:
                    finding = engine.evaluate_service_checklist_rule(
                        rule, service, checklist
                    )
                else:
                    asset = assets.get(service.asset_id)
                    if asset is None:
                        continue
                    finding = engine.evaluate_asset_service_lifecycle_rule(
                        rule, asset, service,
                        evidence.os_support.get(asset.asset_id),
                        now=now, max_age=feed_age,
                    )

                collect(
                    finding,
                    scoring.service_entity_ids[index],
                    f"service:{index + 1}",
                )

        elif (
            key in engine.SOFTWARE_HANDLERS
            or key in engine.APPLICATION_SUPPORT_HANDLERS
            or key in engine.VULNERABILITY_HANDLERS
        ):
            for index, software in enumerate(inventory.software):
                entry_id = f"software:{index + 1}"
                entity_id = scoring.software_entity_ids[index]

                if key in engine.SOFTWARE_HANDLERS:
                    collect(
                        engine.evaluate_software_rule(
                            rule, software, entity_id=entry_id
                        ),
                        entity_id, entry_id,
                    )
                elif key in engine.APPLICATION_SUPPORT_HANDLERS:
                    collect(
                        engine.evaluate_software_support_rule(
                            rule, software,
                            evidence.application_support.get(entry_id),
                            entity_id=entry_id,
                            now=now, max_age=feed_age,
                        ),
                        entity_id, entry_id,
                    )
                else:
                    for record in evidence.vulnerabilities.get(entry_id, ()):
                        collect(
                            engine.evaluate_software_vulnerability_rule(
                                rule, software, record,
                                evidence.kev_snapshot,
                                entity_id=entry_id,
                                now=now, max_age=feed_age,
                            ),
                            entity_id, entry_id,
                        )
        else:
            raise ValueError("Rule has no assessment evaluation route.")

    return AssessmentEvaluation(
        findings=tuple(findings),
        scoring_inventory=scoring,
        coverage_issues=tuple(coverage),
        freshness_policy=policy,
        evaluated_at=now,
        rules_loaded=len(rules),
    )