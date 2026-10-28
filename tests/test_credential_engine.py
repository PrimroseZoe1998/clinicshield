from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from clinicshield import rule_engine
from clinicshield.credential_evidence import DefaultPasswordEvidence
from clinicshield.ingest import read_csv
from clinicshield.rule_engine import evaluate_asset_credential_rule
from clinicshield.rule_handlers import RuleObservation
from clinicshield.rule_loader import load_rule
from clinicshield.rule_models import RuleDefinition
from clinicshield.schemas import Asset


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 27, 12, tzinfo=timezone.utc)


@pytest.fixture
def rule():
    return load_rule(ROOT / "rules" / "R10.yaml")


@pytest.fixture
def asset():
    return Asset(
        asset_id="TEST-RT01",
        asset_name="Test router",
        asset_type="network_device",
        os_name="Example firmware",
        os_version="1.0",
        touches_phi="Unknown",
        internet_facing="N",
        encrypted="Unknown",
    )


def make_evidence(asset, **changes):
    data = {
        "asset_id": asset.asset_id,
        "applicability": "Yes",
        "default_password_changed": "No",
        "evidence_basis": "Fictional administrator confirmation.",
        "evidence_source": "Synthetic test fixture",
        "observed_at": NOW,
    }
    data.update(changes)
    return DefaultPasswordEvidence(**data)


def evaluate(rule, asset, evidence):
    return evaluate_asset_credential_rule(
        rule,
        asset,
        evidence,
        now=NOW,
        max_age=timedelta(days=8),
    )


def change_rule(rule, **changes):
    data = rule.model_dump()
    data.update(changes)
    return RuleDefinition.model_validate(data)


def test_yaml_rule_produces_confirmed_finding(rule, asset):
    finding = evaluate(rule, asset, make_evidence(asset))

    assert finding is not None
    assert finding.observation.rule_id == "R10"
    assert finding.observation.entity_id == asset.asset_id
    assert finding.observation.status == "confirmed"
    assert finding.severity == "High"
    assert finding.rule.review_status == "draft"


def test_missing_evidence_requires_review(rule, asset):
    finding = evaluate(rule, asset, None)

    assert finding is not None
    assert finding.observation.status == "needs_review"
    assert finding.severity == "Info"


@pytest.mark.parametrize(
    "changes",
    [
        {"default_password_changed": "Yes"},
        {"applicability": "No"},
    ],
)
def test_resolved_status_produces_no_finding(rule, asset, changes):
    assert evaluate(
        rule, asset, make_evidence(asset, **changes)
    ) is None


def test_stale_evidence_requires_review(rule, asset):
    finding = evaluate(
        rule,
        asset,
        make_evidence(asset, observed_at=NOW - timedelta(days=9)),
    )

    assert finding is not None
    assert finding.observation.status == "needs_review"


def test_severity_comes_from_definition(rule, asset):
    configured = change_rule(rule, severity="Medium")

    finding = evaluate(configured, asset, make_evidence(asset))

    assert finding is not None
    assert finding.severity == "Medium"


@pytest.mark.parametrize(
    "changes",
    [
        {"rule_id": "R19"},
        {"handler": "unregistered_handler"},
        {"kind": "checklist"},
    ],
)
def test_rejects_unregistered_combinations(rule, asset, changes):
    with pytest.raises(ValueError, match="registration"):
        evaluate(
            change_rule(rule, **changes), asset, make_evidence(asset)
        )


def test_rejects_missing_required_evidence(rule, asset):
    configured = change_rule(
        rule,
        evidence_fields=(*rule.evidence_fields, "missing_field"),
    )

    with pytest.raises(ValueError, match="required evidence"):
        evaluate(configured, asset, make_evidence(asset))


@pytest.mark.parametrize(
    "returned_rule,returned_entity,message",
    [
        ("R19", "TEST-RT01", "different rule ID"),
        ("R10", "OTHER-ASSET", "different asset ID"),
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
        rule_engine.CREDENTIAL_HANDLERS,
        ("R10", "default_admin_password", "technical"),
        incorrect_handler,
    )

    with pytest.raises(ValueError, match=message):
        evaluate(rule, asset, make_evidence(asset))


def test_fictional_lakeview_router_scenario(rule):
    assets = read_csv(
        (ROOT / "samples/lakeview_dental/assets.csv").read_bytes(),
        "assets",
    )
    router = next(asset for asset in assets if asset.asset_id == "LV-RT01")

    # Explicitly transcribe the fictional scenario; do not parse free text.
    evidence = make_evidence(
        router,
        evidence_basis=(
            "Fictional Lakeview scenario states that the default "
            "administrator password is unchanged."
        ),
        evidence_source="samples/lakeview_dental/assets.csv: LV-RT01",
    )

    finding = evaluate(rule, router, evidence)

    assert finding is not None
    assert finding.observation.status == "confirmed"
    assert finding.observation.entity_id == "LV-RT01"
    assert dict(finding.observation.evidence)[
        "default_password_changed"
    ] == "No"