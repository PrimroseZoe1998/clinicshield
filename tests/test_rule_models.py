import pytest
from pydantic import ValidationError

from clinicshield.rule_models import RuleDefinition


@pytest.fixture
def rule_data():
    return {
        "rule_id": "R05",
        "title": "Portable-device encryption",
        "kind": "technical",
        "handler": "portable_encryption",
        "description": "Identify disabled or unknown encryption.",
        "severity": "High",
        "unknown_severity": "Info",
        "evidence_fields": ["asset_id", "portable", "encrypted"],
        "fix": "Verify encryption and enable it where appropriate.",
        "owner": "IT administrator",
        "effort": 2,
        "cost": "unknown",
        "framework_references": [
            {
                "framework": "Project mapping",
                "reference": "Q05",
                "source": "docs/framework-mappings.md",
                "rationale": "Portable-device encryption mapping.",
                "review_status": "pending",
            }
        ],
        "review_status": "draft",
    }


def test_accepts_draft_rule(rule_data):
    rule = RuleDefinition(**rule_data)

    assert rule.rule_id == "R05"
    assert rule.evidence_fields == (
        "asset_id", "portable", "encrypted"
    )
    assert rule.review_status == "draft"
    assert rule.framework_references[0].review_status == "pending"


def test_json_round_trip(rule_data):
    rule = RuleDefinition(**rule_data)

    assert RuleDefinition.model_validate_json(
        rule.model_dump_json()
    ) == rule


@pytest.mark.parametrize("rule_id", ["R01", "R09", "R10", "R24"])
def test_accepts_rule_id_boundaries(rule_data, rule_id):
    rule_data["rule_id"] = rule_id

    assert RuleDefinition(**rule_data).rule_id == rule_id


@pytest.mark.parametrize("rule_id", ["R00", "R25", "R1", "r05", "R05x"])
def test_rejects_invalid_rule_id(rule_data, rule_id):
    rule_data["rule_id"] = rule_id

    with pytest.raises(ValidationError):
        RuleDefinition(**rule_data)


@pytest.mark.parametrize(
    "handler",
    ["", "PortableEncryption", "../handler", "handler()", "a.b"],
)
def test_rejects_invalid_handler_name(rule_data, handler):
    rule_data["handler"] = handler

    with pytest.raises(ValidationError):
        RuleDefinition(**rule_data)


@pytest.mark.parametrize(
    "field",
    ["title", "description", "fix", "owner"],
)
def test_rejects_blank_required_text(rule_data, field):
    rule_data[field] = "   "

    with pytest.raises(ValidationError):
        RuleDefinition(**rule_data)


@pytest.mark.parametrize(
    "field",
    ["severity", "unknown_severity"],
)
def test_rejects_unknown_severity(rule_data, field):
    rule_data[field] = "Urgent"

    with pytest.raises(ValidationError):
        RuleDefinition(**rule_data)


@pytest.mark.parametrize("effort", [1, 2, 3])
def test_accepts_effort_scale(rule_data, effort):
    rule_data["effort"] = effort

    assert RuleDefinition(**rule_data).effort == effort


@pytest.mark.parametrize("effort", [0, 4, "2"])
def test_rejects_invalid_effort(rule_data, effort):
    rule_data["effort"] = effort

    with pytest.raises(ValidationError):
        RuleDefinition(**rule_data)


@pytest.mark.parametrize(
    "changes",
    [
        {"kind": "other"},
        {"cost": "expensive"},
        {"review_status": "approved"},
        {"schema_version": 2},
        {"unexpected": "value"},
        {"evidence_fields": []},
        {"evidence_fields": ["   "]},
        {"framework_references": []},
    ],
)
def test_rejects_invalid_rule_fields(rule_data, changes):
    rule_data.update(changes)

    with pytest.raises(ValidationError):
        RuleDefinition(**rule_data)


@pytest.mark.parametrize(
    "field",
    ["framework", "reference", "source", "rationale"],
)
def test_rejects_blank_framework_fields(rule_data, field):
    rule_data["framework_references"][0][field] = "   "

    with pytest.raises(ValidationError):
        RuleDefinition(**rule_data)


def test_rejects_invalid_framework_review_status(rule_data):
    rule_data["framework_references"][0]["review_status"] = "approved"

    with pytest.raises(ValidationError):
        RuleDefinition(**rule_data)


@pytest.mark.parametrize(
    "field",
    [
        "rule_id",
        "handler",
        "severity",
        "unknown_severity",
        "evidence_fields",
        "fix",
        "framework_references",
        "review_status",
    ],
)
def test_requires_rule_fields(rule_data, field):
    del rule_data[field]

    with pytest.raises(ValidationError):
        RuleDefinition(**rule_data)


def test_rule_is_frozen(rule_data):
    rule = RuleDefinition(**rule_data)

    with pytest.raises(ValidationError):
        rule.title = "Changed title"