from dataclasses import dataclass

from clinicshield.rule_handlers import (
    RuleObservation,
    backup_safeguards,
    documented_risk_analysis,
    guest_wifi_separation,
    incident_readiness,
    individual_accounts,
    portable_encryption,
    router_security,
    telnet_service,
    staff_security_training,
    antivirus_protection,
    reporting_preparation,
    unknown_software_version,
    cloud_baa_status,
    email_mfa,
    clinical_system_mfa,
    remote_admin_exposure,
    remote_access_safeguards,
)

from datetime import datetime, timedelta

from clinicshield.lifecycle_evidence import LifecycleEvidence
from clinicshield.lifecycle_handlers import operating_system_support
from clinicshield.rule_models import RuleDefinition, Severity
from clinicshield.schemas import Asset, Service, Software
from clinicshield.checklist_input import Checklist

ASSET_HANDLERS = {
    ("R05", "portable_encryption", "technical"): portable_encryption,
}


@dataclass(frozen=True)
class RuleFinding:
    rule: RuleDefinition
    observation: RuleObservation

    @property
    def severity(self) -> Severity:
        if self.observation.status == "needs_review":
            return self.rule.unknown_severity
        return self.rule.severity


def evaluate_asset_rule(
    rule: RuleDefinition,
    asset: Asset,
) -> RuleFinding | None:
    """Evaluate an explicitly registered rule against one asset."""
    key = (rule.rule_id, rule.handler, rule.kind)
    handler = ASSET_HANDLERS.get(key)

    if handler is None:
        raise ValueError("Unsupported asset rule registration.")

    observation = handler(asset)

    if observation is None:
        return None

    if observation.rule_id != rule.rule_id:
        raise ValueError("Handler returned a different rule ID.")

    evidence_keys = {key for key, _ in observation.evidence}
    if not set(rule.evidence_fields).issubset(evidence_keys):
        raise ValueError("Handler did not provide required evidence.")

    return RuleFinding(rule=rule, observation=observation)

SERVICE_HANDLERS = {
    ("R06", "remote_admin_exposure", "technical"): remote_admin_exposure,
    ("R09", "telnet_service", "technical"): telnet_service,
}


def evaluate_service_rule(
    rule: RuleDefinition,
    service: Service,
) -> RuleFinding | None:
    """Evaluate an explicitly registered rule against one service."""
    key = (rule.rule_id, rule.handler, rule.kind)
    handler = SERVICE_HANDLERS.get(key)

    if handler is None:
        raise ValueError("Unsupported service rule registration.")

    observation = handler(service)

    if observation is None:
        return None

    if observation.rule_id != rule.rule_id:
        raise ValueError("Handler returned a different rule ID.")

    evidence_keys = {key for key, _ in observation.evidence}
    if not set(rule.evidence_fields).issubset(evidence_keys):
        raise ValueError("Handler did not provide required evidence.")

    return RuleFinding(rule=rule, observation=observation)

CHECKLIST_HANDLERS = {
    ("R14", "individual_accounts", "checklist"): individual_accounts,
    ("R18", "guest_wifi_separation", "checklist"): guest_wifi_separation,
    ("R19", "router_security", "checklist"): router_security,
    ("R22", "documented_risk_analysis", "checklist"): documented_risk_analysis,
    ("R20", "incident_readiness", "checklist"): incident_readiness,
    ("R16", "backup_safeguards", "checklist"): backup_safeguards,
    ("R23", "staff_security_training", "checklist"): staff_security_training,
    ("R15", "antivirus_protection", "checklist"): antivirus_protection,
    ("R21", "reporting_preparation", "checklist"): reporting_preparation,
}


def evaluate_checklist_rule(
    rule: RuleDefinition,
    checklist: Checklist,
) -> RuleFinding | None:
    """Evaluate an explicitly registered checklist rule."""
    key = (rule.rule_id, rule.handler, rule.kind)
    handler = CHECKLIST_HANDLERS.get(key)

    if handler is None:
        raise ValueError("Unsupported checklist rule registration.")

    observation = handler(checklist)

    if observation is None:
        return None

    if observation.rule_id != rule.rule_id:
        raise ValueError("Handler returned a different rule ID.")

    evidence_keys = {key for key, _ in observation.evidence}
    if not set(rule.evidence_fields).issubset(evidence_keys):
        raise ValueError("Handler did not provide required evidence.")

    return RuleFinding(rule=rule, observation=observation)

SOFTWARE_HANDLERS = {
    ("R12", "email_mfa", "technical"): email_mfa,
    ("R13", "clinical_system_mfa", "technical"): clinical_system_mfa,
    ("R17", "cloud_baa_status", "technical"): cloud_baa_status,
    ("R24", "unknown_software_version", "technical"): unknown_software_version,
}


def evaluate_software_rule(
    rule: RuleDefinition,
    software: Software,
    *,
    entity_id: str,
) -> RuleFinding | None:
    """Evaluate a registered rule against one identified software entry."""
    key = (rule.rule_id, rule.handler, rule.kind)
    handler = SOFTWARE_HANDLERS.get(key)

    if handler is None:
        raise ValueError("Unsupported software rule registration.")

    observation = handler(software, entity_id=entity_id)

    if observation is None:
        return None

    if observation.rule_id != rule.rule_id:
        raise ValueError("Handler returned a different rule ID.")

    if observation.entity_id != entity_id:
        raise ValueError("Handler returned a different software entry ID.")

    evidence_keys = {key for key, _ in observation.evidence}
    if not set(rule.evidence_fields).issubset(evidence_keys):
        raise ValueError("Handler did not provide required evidence.")

    return RuleFinding(rule=rule, observation=observation)

SERVICE_CHECKLIST_HANDLERS = {
    ("R07", "remote_access_safeguards", "technical"): remote_access_safeguards,
}


def evaluate_service_checklist_rule(
    rule: RuleDefinition,
    service: Service,
    checklist: Checklist,
) -> RuleFinding | None:
    """Evaluate a registered rule using service and checklist evidence."""
    key = (rule.rule_id, rule.handler, rule.kind)
    handler = SERVICE_CHECKLIST_HANDLERS.get(key)

    if handler is None:
        raise ValueError("Unsupported service/checklist rule registration.")

    observation = handler(service, checklist)

    if observation is None:
        return None

    if observation.rule_id != rule.rule_id:
        raise ValueError("Handler returned a different rule ID.")

    if observation.entity_id != service.asset_id:
        raise ValueError("Handler returned a different service asset ID.")

    evidence_keys = {key for key, _ in observation.evidence}
    if not set(rule.evidence_fields).issubset(evidence_keys):
        raise ValueError("Handler did not provide required evidence.")

    return RuleFinding(rule=rule, observation=observation)

LIFECYCLE_HANDLERS = {
    ("R03", "operating_system_support", "technical"): operating_system_support,
}


def evaluate_asset_lifecycle_rule(
    rule: RuleDefinition,
    asset: Asset,
    evidence: LifecycleEvidence | None,
    *,
    now: datetime,
    max_age: timedelta,
) -> RuleFinding | None:
    """Evaluate an asset using explicitly supplied lifecycle evidence."""
    key = (rule.rule_id, rule.handler, rule.kind)
    handler = LIFECYCLE_HANDLERS.get(key)

    if handler is None:
        raise ValueError("Unsupported lifecycle rule registration.")

    observation = handler(
        asset,
        evidence,
        now=now,
        max_age=max_age,
    )

    if observation is None:
        return None

    if observation.rule_id != rule.rule_id:
        raise ValueError("Handler returned a different rule ID.")

    if observation.entity_id != asset.asset_id:
        raise ValueError("Handler returned a different asset ID.")

    evidence_keys = {key for key, _ in observation.evidence}
    if not set(rule.evidence_fields).issubset(evidence_keys):
        raise ValueError("Handler did not provide required evidence.")

    return RuleFinding(rule=rule, observation=observation)