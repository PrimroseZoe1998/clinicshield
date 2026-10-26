from pathlib import Path

import yaml
from yaml.events import AliasEvent

from clinicshield.rule_models import RuleDefinition


MAX_RULE_BYTES = 64 * 1024


class RuleYamlLoader(yaml.SafeLoader):
    """Safe YAML loading with duplicate keys and aliases rejected."""

    def compose_node(self, parent, index):
        if self.check_event(AliasEvent):
            raise ValueError("YAML aliases are not supported in rules.")
        return super().compose_node(parent, index)

    def construct_mapping(self, node, deep=False):
        if not isinstance(node, yaml.MappingNode):
            raise ValueError("Expected a YAML mapping.")

        result = {}

        for key_node, value_node in node.value:
            if key_node.tag != "tag:yaml.org,2002:str":
                raise ValueError("Rule YAML keys must be text.")

            key = self.construct_object(key_node, deep=deep)

            if key in result:
                raise ValueError(f"Duplicate YAML key: {key}")

            result[key] = self.construct_object(value_node, deep=deep)

        return result


def load_rule(path: Path) -> RuleDefinition:
    """Read one bounded YAML file and validate its rule definition."""
    with path.open("rb") as handle:
        payload = handle.read(MAX_RULE_BYTES + 1)

    if len(payload) > MAX_RULE_BYTES:
        raise ValueError("Rule file exceeds the size limit.")

    loader = RuleYamlLoader(payload.decode("utf-8"))

    try:
        data = loader.get_single_data()
    except yaml.YAMLError as error:
        raise ValueError("Invalid rule YAML.") from error
    finally:
        loader.dispose()

    if not isinstance(data, dict):
        raise ValueError("Rule YAML must contain one mapping.")

    return RuleDefinition.model_validate(data)