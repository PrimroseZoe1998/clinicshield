from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from clinicshield import rule_engine
from clinicshield.lifecycle_evidence import LifecycleEvidence
from clinicshield.rule_engine import evaluate_asset_lifecycle_rule
from clinicshield.rule_handlers import RuleObservation
from clinicshield.rule_loader import load_rule
from clinicshield.rule_models import RuleDefinition
from clinicshield.schemas import Asset


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 27, 12, tzinfo=timezone.utc)
MAX_AGE = timedelta(days=8)


@pytest.fixture
def rule():
    return load_rule(ROOT / "rules" / "R03.yaml")


@pytest.fixture
def asset():
    return Asset(
        asset_id="TEST-WS01",
        asset_name="Test workstation",
        asset_type="workstation",
        os_name="Example OS",
        os_version="1.0",
        touches_phi="Y",
        internet_facing="N",
        encrypted="Y",
    )


def make_evidence(**changes):
    data = {
        "os_name": "Example OS",
        "os_version": "1.0",
        "support_status": "unsupported",
        "support_basis": "Support ended; no extended coverage.",
        "extended_support": "confirmed_absent",
        "source_url": "https://example.org/support",
        "retrieved_at": NOW,
        "source_generated_at": NOW,
    }
    data.update(changes)
    return LifecycleEvidence(**data)


def evaluate(rule, asset, evidence):
    return evaluate_asset_lifecycle_rule(
        rule, asset, evidence, now=NOW, max_age=MAX_AGE
    )


def change_rule(rule, **changes):
    data = rule.model_dump()
    data.update(changes)
    return RuleDefinition.model_validate(data)


def test_yaml_rule_produces_unsupported_finding(rule, asset):
    finding = evaluate(rule, asset, make_evidence())

    assert finding is not None
    assert finding.observation.rule_id == "R03"
    assert finding.observation.entity_id == asset.asset_id
    assert finding.observation.status == "confirmed"
    assert finding.severity == "High"
    assert finding.rule.review_status == "draft"


def test_missing_evidence_uses_unknown_severity(rule, asset):
    finding = evaluate(rule, asset, None)

    assert finding is not None
    assert finding.observation.status == "needs_review"
    assert finding.severity == "Info"


def test_supported_release_produces_no_finding(rule, asset):
    assert evaluate(
        rule, asset, make_evidence(support_status="supported")
    ) is None


@pytest.mark.parametrize(
    "changes",
    [
        {"extended_support": "active"},
        {"extended_support": "unknown"},
        {"os_version": "2.0"},
        {"source_generated_at": NOW - timedelta(days=9)},
    ],
)
def test_unresolved_evidence_requires_review(rule, asset, changes):
    finding = evaluate(rule, asset, make_evidence(**changes))

    assert finding is not None
    assert finding.observation.status == "needs_review"
    assert finding.severity == "Info"


@pytest.mark.parametrize(
    "evidence,expected",
    [(make_evidence(), "Medium"), (None, "Low")],
)
def test_severity_comes_from_definition(rule, asset, evidence, expected):
    configured = change_rule(
        rule, severity="Medium", unknown_severity="Low"
    )

    finding = evaluate(configured, asset, evidence)

    assert finding is not None
    assert finding.severity == expected


@pytest.mark.parametrize(
    "changes",
    [
        {"rule_id": "R04"},
        {"handler": "unregistered_handler"},
        {"kind": "checklist"},
    ],
)
def test_rejects_unregistered_combinations(rule, asset, changes):
    with pytest.raises(ValueError, match="registration"):
        evaluate(change_rule(rule, **changes), asset, make_evidence())


def test_rejects_missing_required_evidence(rule, asset):
    configured = change_rule(
        rule,
        evidence_fields=(*rule.evidence_fields, "missing_field"),
    )

    with pytest.raises(ValueError, match="required evidence"):
        evaluate(configured, asset, make_evidence())


@pytest.mark.parametrize(
    "returned_rule,returned_entity,message",
    [
        ("R04", "TEST-WS01", "different rule ID"),
        ("R03", "OTHER-ASSET", "different asset ID"),
    ],
)
def test_rejects_incorrect_handler_identity(
    rule, asset, monkeypatch, returned_rule, returned_entity, message
):
    def incorrect_handler(asset, evidence, *, now, max_age):
        return RuleObservation(
            rule_id=returned_rule,
            entity_id=returned_entity,
            status="confirmed",
            evidence=(),
        )

    monkeypatch.setitem(
        rule_engine.LIFECYCLE_HANDLERS,
        ("R03", "operating_system_support", "technical"),
        incorrect_handler,
    )

    with pytest.raises(ValueError, match=message):
        evaluate(rule, asset, make_evidence())