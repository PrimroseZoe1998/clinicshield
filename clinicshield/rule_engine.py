from dataclasses import dataclass

from clinicshield.rule_handlers import (
    RuleObservation,
    portable_encryption,
)
from clinicshield.rule_models import RuleDefinition, Severity
from clinicshield.schemas import Asset


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