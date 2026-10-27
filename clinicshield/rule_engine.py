from dataclasses import dataclass

from clinicshield.rule_handlers import (
    RuleObservation,
    portable_encryption,
)
from clinicshield.rule_handlers import (
    RuleObservation,
    portable_encryption,
    telnet_service,
)
from clinicshield.rule_handlers import (
    RuleObservation,
    individual_accounts,
    portable_encryption,
    telnet_service,
)
from clinicshield.rule_models import RuleDefinition, Severity
from clinicshield.schemas import Asset, Service
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