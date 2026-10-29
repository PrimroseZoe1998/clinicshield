from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from clinicshield import rule_loader
from clinicshield.rule_loader import load_rule


RULE_PATH = Path(__file__).resolve().parents[1] / "rules" / "R05.yaml"


@pytest.fixture
def rule_text():
    return RULE_PATH.read_text(encoding="utf-8")


def test_loads_repository_r05():
    rule = load_rule(RULE_PATH)

    assert rule.rule_id == "R05"
    assert rule.handler == "portable_encryption"
    assert rule.kind == "technical"
    assert rule.severity == "High"
    assert rule.unknown_severity == "Info"
    assert rule.review_status == "draft"
    assert "encrypted" in rule.evidence_fields


def test_loads_valid_rule_from_file(tmp_path, rule_text):
    path = tmp_path / "rule.yaml"
    path.write_text(rule_text, encoding="utf-8")

    assert load_rule(path).rule_id == "R05"


@pytest.mark.parametrize(
    "payload",
    ["", "null", "[]", "- item\n", "plain text"],
)
def test_rejects_nonmapping_document(tmp_path, payload):
    path = tmp_path / "rule.yaml"
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(ValueError, match="one mapping"):
        load_rule(path)


def test_rejects_duplicate_top_level_key(tmp_path, rule_text):
    path = tmp_path / "rule.yaml"
    path.write_text(
        rule_text + "\nrule_id: R06\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate YAML key"):
        load_rule(path)


def test_rejects_duplicate_nested_key(tmp_path, rule_text):
    data = yaml.safe_load(rule_text)
    text = yaml.safe_dump(data, sort_keys=False)
    text = text.replace(
        "review_status: reviewed",
        "review_status: reviewed\n  review_status: pending",
        1,
    )
    path = tmp_path / "rule.yaml"
    path.write_text(text, encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate YAML key"):
        load_rule(path)


def test_rejects_aliases(tmp_path):
    path = tmp_path / "rule.yaml"
    path.write_text("first: &value text\nsecond: *value\n")

    with pytest.raises(ValueError, match="aliases"):
        load_rule(path)


def test_rejects_nontext_keys(tmp_path):
    path = tmp_path / "rule.yaml"
    path.write_text("1: value\n")

    with pytest.raises(ValueError, match="keys must be text"):
        load_rule(path)


def test_rejects_unsafe_yaml_tag(tmp_path):
    path = tmp_path / "rule.yaml"
    path.write_text(
        '!!python/object/apply:builtins.str ["example"]\n'
    )

    with pytest.raises(ValueError, match="Invalid rule YAML"):
        load_rule(path)


def test_rejects_multiple_documents(tmp_path, rule_text):
    path = tmp_path / "rule.yaml"
    path.write_text(rule_text + "\n---\nrule_id: R06\n")

    with pytest.raises(ValueError, match="Invalid rule YAML"):
        load_rule(path)


def test_rejects_malformed_yaml(tmp_path):
    path = tmp_path / "rule.yaml"
    path.write_text("rule_id: [unfinished\n")

    with pytest.raises(ValueError, match="Invalid rule YAML"):
        load_rule(path)


def test_validates_rule_fields(tmp_path, rule_text):
    data = yaml.safe_load(rule_text)
    data["severity"] = "Urgent"
    path = tmp_path / "rule.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(ValidationError):
        load_rule(path)


def test_rejects_invalid_utf8(tmp_path):
    path = tmp_path / "rule.yaml"
    path.write_bytes(b"\xff")

    with pytest.raises(UnicodeDecodeError):
        load_rule(path)


def test_accepts_exact_size_limit(
    tmp_path, monkeypatch, rule_text
):
    payload = rule_text.encode("utf-8")
    monkeypatch.setattr(rule_loader, "MAX_RULE_BYTES", len(payload))
    path = tmp_path / "rule.yaml"
    path.write_bytes(payload)

    assert load_rule(path).rule_id == "R05"


def test_rejects_oversized_file(tmp_path, monkeypatch):
    monkeypatch.setattr(rule_loader, "MAX_RULE_BYTES", 10)
    path = tmp_path / "rule.yaml"
    path.write_bytes(b"x" * 11)

    with pytest.raises(ValueError, match="size limit"):
        load_rule(path)


def test_missing_file_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_rule(tmp_path / "missing.yaml")