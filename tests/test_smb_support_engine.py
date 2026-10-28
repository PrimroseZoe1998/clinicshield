from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from clinicshield import rule_engine
from clinicshield.ingest import read_csv
from clinicshield.lifecycle_evidence import LifecycleEvidence
from clinicshield.rule_engine import evaluate_asset_service_lifecycle_rule
from clinicshield.rule_handlers import RuleObservation
from clinicshield.rule_loader import load_rule
from clinicshield.rule_models import RuleDefinition
from clinicshield.schemas import Asset, Service


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 27, 12, tzinfo=timezone.utc)


@pytest.fixture
def rule():
    return load_rule(ROOT / "rules" / "R08.yaml")


@pytest.fixture
def asset():
    return Asset(
        asset_id="TEST-SRV01",
        asset_name="Test server",
        asset_type="server",
        os_name="Example OS",
        os_version="1.0",
        touches_phi="Y",
        internet_facing="N",
        encrypted="Y",
    )


def make_service(**changes):
    data = {
        "asset_id": "TEST-SRV01",
        "host": "192.0.2.10",
        "port": 445,
        "protocol": "tcp",
        "service": "smb",
        "exposure": "internal",
    }
    data.update(changes)
    return Service(**data)


def make_evidence(asset, **changes):
    data = {
        "os_name": asset.os_name,
        "os_version": asset.os_version,
        "support_status": "unsupported",
        "support_basis": "Fictional lifecycle fixture, not live vendor evidence.",
        "extended_support": "confirmed_absent",
        "source_url": "https://example.org/support-fixture",
        "retrieved_at": NOW,
        "source_generated_at": NOW,
    }
    data.update(changes)
    return LifecycleEvidence(**data)


def evaluate(rule, asset, service, evidence):
    return evaluate_asset_service_lifecycle_rule(
        rule,
        asset,
        service,
        evidence,
        now=NOW,
        max_age=timedelta(days=8),
    )


def change_rule(rule, **changes):
    data = rule.model_dump()
    data.update(changes)
    return RuleDefinition.model_validate(data)


def test_yaml_rule_produces_confirmed_finding(rule, asset):
    finding = evaluate(
        rule, asset, make_service(), make_evidence(asset)
    )

    assert finding is not None
    assert finding.observation.rule_id == "R08"
    assert finding.observation.entity_id == asset.asset_id
    assert finding.observation.status == "confirmed"
    assert finding.severity == "High"
    assert finding.rule.review_status == "draft"


def test_missing_evidence_requires_review(rule, asset):
    finding = evaluate(rule, asset, make_service(), None)

    assert finding is not None
    assert finding.observation.status == "needs_review"
    assert finding.severity == "Info"


def test_supported_os_produces_no_finding(rule, asset):
    assert evaluate(
        rule,
        asset,
        make_service(),
        make_evidence(asset, support_status="supported"),
    ) is None


def test_non_smb_service_produces_no_finding(rule, asset):
    assert evaluate(
        rule,
        asset,
        make_service(service="other"),
        make_evidence(asset),
    ) is None


def test_severity_comes_from_definition(rule, asset):
    configured = change_rule(rule, severity="Medium")

    finding = evaluate(
        configured, asset, make_service(), make_evidence(asset)
    )

    assert finding is not None
    assert finding.severity == "Medium"


@pytest.mark.parametrize(
    "changes",
    [
        {"rule_id": "R03"},
        {"handler": "unregistered_handler"},
        {"kind": "checklist"},
    ],
)
def test_rejects_unregistered_combinations(rule, asset, changes):
    with pytest.raises(ValueError, match="registration"):
        evaluate(
            change_rule(rule, **changes),
            asset,
            make_service(),
            make_evidence(asset),
        )


def test_rejects_missing_required_evidence(rule, asset):
    configured = change_rule(
        rule,
        evidence_fields=(*rule.evidence_fields, "missing_field"),
    )

    with pytest.raises(ValueError, match="required evidence"):
        evaluate(
            configured, asset, make_service(), make_evidence(asset)
        )


@pytest.mark.parametrize(
    "returned_rule,returned_entity,message",
    [
        ("R03", "TEST-SRV01", "different rule ID"),
        ("R08", "OTHER-ASSET", "different asset ID"),
    ],
)
def test_rejects_wrong_handler_identity(
    rule, asset, monkeypatch, returned_rule, returned_entity, message
):
    def incorrect_handler(asset, service, evidence, *, now, max_age):
        return RuleObservation(
            rule_id=returned_rule,
            entity_id=returned_entity,
            status="confirmed",
            evidence=(),
        )

    monkeypatch.setitem(
        rule_engine.ASSET_SERVICE_LIFECYCLE_HANDLERS,
        ("R08", "smb_os_support", "technical"),
        incorrect_handler,
    )

    with pytest.raises(ValueError, match=message):
        evaluate(rule, asset, make_service(), make_evidence(asset))


@pytest.mark.parametrize(
    "clinic,expected_assets",
    [
        ("lakeview_dental", {"LV-SRV01"}),
        ("westside_health", set()),
    ],
)
def test_sample_service_matching_with_fictional_support_fixture(
    rule, clinic, expected_assets
):
    folder = ROOT / "samples" / clinic
    assets = {
        item.asset_id: item
        for item in read_csv(
            (folder / "assets.csv").read_bytes(), "assets"
        )
    }
    services = read_csv(
        (folder / "services.csv").read_bytes(), "services"
    )
    findings = []

    for service in services:
        asset = assets[service.asset_id]
        finding = evaluate(
            rule, asset, service, make_evidence(asset)
        )
        if finding is not None:
            findings.append(finding)

    assert len(findings) == len(expected_assets)
    assert {
        finding.observation.entity_id for finding in findings
    } == expected_assets