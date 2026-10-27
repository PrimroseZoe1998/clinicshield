from pathlib import Path

import pytest

from clinicshield import rule_engine
from clinicshield.rule_engine import evaluate_asset_rule
from clinicshield.rule_handlers import RuleObservation
from clinicshield.rule_loader import load_rule
from clinicshield.rule_models import RuleDefinition
from clinicshield.schemas import Asset


RULE_PATH = Path(__file__).resolve().parents[1] / "rules" / "R05.yaml"


@pytest.fixture
def rule():
    return load_rule(RULE_PATH)


def make_asset(**changes):
    data = {
        "asset_id": "TEST-LT01",
        "asset_name": "Test laptop",
        "asset_type": "laptop",
        "os_name": "Example OS",
        "os_version": "1.0",
        "touches_phi": "Y",
        "internet_facing": "N",
        "encrypted": "N",
    }
    data.update(changes)
    return Asset(**data)


def change_rule(rule, **changes):
    data = rule.model_dump()
    data.update(changes)
    return RuleDefinition.model_validate(data)


def test_yaml_rule_produces_confirmed_finding(rule):
    finding = evaluate_asset_rule(rule, make_asset())

    assert finding is not None
    assert finding.observation.rule_id == "R05"
    assert finding.observation.entity_id == "TEST-LT01"
    assert finding.observation.status == "confirmed"
    assert finding.severity == "High"
    assert finding.rule == rule
    assert finding.rule.review_status == "draft"
    assert finding.rule.fix
    assert finding.rule.framework_references


def test_unknown_encryption_uses_unknown_severity(rule):
    finding = evaluate_asset_rule(
        rule, make_asset(encrypted="Unknown")
    )

    assert finding is not None
    assert finding.observation.status == "needs_review"
    assert finding.severity == "Info"


@pytest.mark.parametrize("encrypted", ["N", "Unknown"])
def test_severity_comes_from_definition(rule, encrypted):
    configured = change_rule(
        rule,
        severity="Medium",
        unknown_severity="Low",
    )

    finding = evaluate_asset_rule(
        configured, make_asset(encrypted=encrypted)
    )

    assert finding is not None
    assert finding.severity == (
        "Medium" if encrypted == "N" else "Low"
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"encrypted": "Y"},
        {"portable": "N"},
    ],
)
def test_nontrigger_returns_no_finding(rule, changes):
    assert evaluate_asset_rule(rule, make_asset(**changes)) is None


@pytest.mark.parametrize(
    "changes",
    [
        {"rule_id": "R06"},
        {"handler": "unregistered_handler"},
        {"kind": "checklist"},
    ],
)
def test_rejects_unregistered_rule_combinations(rule, changes):
    configured = change_rule(rule, **changes)

    with pytest.raises(ValueError, match="registration"):
        evaluate_asset_rule(configured, make_asset())


def test_rejects_missing_required_evidence(rule):
    configured = change_rule(
        rule,
        evidence_fields=(*rule.evidence_fields, "missing_field"),
    )

    with pytest.raises(ValueError, match="required evidence"):
        evaluate_asset_rule(configured, make_asset())


def test_rejects_handler_returning_different_rule_id(
    rule, monkeypatch
):
    def incorrect_handler(asset):
        return RuleObservation(
            rule_id="R06",
            entity_id=asset.asset_id,
            status="confirmed",
            evidence=(),
        )

    monkeypatch.setitem(
        rule_engine.ASSET_HANDLERS,
        ("R05", "portable_encryption", "technical"),
        incorrect_handler,
    )

    with pytest.raises(ValueError, match="different rule ID"):
        evaluate_asset_rule(rule, make_asset())


def test_evaluation_preserves_inputs(rule):
    asset = make_asset(encrypted="Unknown")
    original_rule = rule.model_dump()
    original_asset = asset.model_dump()

    evaluate_asset_rule(rule, asset)

    assert rule.model_dump() == original_rule
    assert asset.model_dump() == original_asset