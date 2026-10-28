from pathlib import Path

from clinicshield import rule_engine
from clinicshield.input_limits import InputError
from clinicshield.rule_loader import load_rule
from clinicshield.rule_models import RuleDefinition


REGISTRIES = (
    rule_engine.ASSET_HANDLERS,
    rule_engine.SERVICE_HANDLERS,
    rule_engine.CHECKLIST_HANDLERS,
    rule_engine.SOFTWARE_HANDLERS,
    rule_engine.SERVICE_CHECKLIST_HANDLERS,
    rule_engine.LIFECYCLE_HANDLERS,
    rule_engine.ASSET_SERVICE_LIFECYCLE_HANDLERS,
    rule_engine.CREDENTIAL_HANDLERS,
    rule_engine.SEGMENTATION_HANDLERS,
    rule_engine.APPLICATION_SUPPORT_HANDLERS,
    rule_engine.VULNERABILITY_HANDLERS,
)


def load_rule_catalog(directory: Path) -> tuple[RuleDefinition, ...]:
    """Require one valid, registered definition for each of 24 rules."""
    paths = sorted([
        *directory.glob("*.yaml"),
        *directory.glob("*.yml"),
    ])

    if len(paths) != 24:
        raise InputError("The rule catalog must contain exactly 24 files.")

    rules = tuple(load_rule(path) for path in paths)
    expected = {f"R{number:02d}" for number in range(1, 25)}

    if {rule.rule_id for rule in rules} != expected:
        raise InputError("The catalog must contain R01 through R24 once.")

    for path, rule in zip(paths, rules):
        if path.stem != rule.rule_id:
            raise InputError("Rule filenames must match their rule IDs.")

        key = (rule.rule_id, rule.handler, rule.kind)
        matches = [
            registry[key]
            for registry in REGISTRIES
            if key in registry
        ]

        if len(matches) != 1 or not callable(matches[0]):
            raise InputError("Each rule requires exactly one registered handler.")

    return tuple(sorted(rules, key=lambda rule: rule.rule_id))