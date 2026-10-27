from pathlib import Path

import pytest

from clinicshield import rule_engine
from clinicshield.ingest import read_csv
from clinicshield.rule_engine import evaluate_service_rule
from clinicshield.rule_handlers import RuleObservation
from clinicshield.rule_loader import load_rule
from clinicshield.rule_models import RuleDefinition
from clinicshield.schemas import Service


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def rule():
    return load_rule(ROOT / "rules" / "R09.yaml")


def make_service(**changes):
    data = {
        "asset_id": "TEST-PR01",
        "host": "192.0.2.10",
        "port": 23,
        "protocol": "tcp",
        "service": "telnet",
        "exposure": "internal",
    }
    data.update(changes)
    return Service(**data)


def change_rule(rule, **changes):
    data = rule.model_dump()
    data.update(changes)
    return RuleDefinition.model_validate(data)


def test_yaml_rule_produces_telnet_finding(rule):
    finding = evaluate_service_rule(rule, make_service())

    assert finding is not None
    assert finding.observation.rule_id == "R09"
    assert finding.observation.status == "confirmed"
    assert finding.severity == "High"
    assert finding.rule == rule
    assert finding.rule.review_status == "draft"


def test_severity_comes_from_yaml_definition(rule):
    configured = change_rule(rule, severity="Medium")

    finding = evaluate_service_rule(configured, make_service())

    assert finding is not None
    assert finding.severity == "Medium"


@pytest.mark.parametrize(
    "changes",
    [
        {"service": "ssh"},
        {"service": "other"},
        {"protocol": "udp"},
    ],
)
def test_nontrigger_returns_no_finding(rule, changes):
    assert evaluate_service_rule(
        rule, make_service(**changes)
    ) is None


@pytest.mark.parametrize(
    "changes",
    [
        {"rule_id": "R08"},
        {"handler": "unregistered_handler"},
        {"kind": "checklist"},
    ],
)
def test_rejects_unregistered_combinations(rule, changes):
    configured = change_rule(rule, **changes)

    with pytest.raises(ValueError, match="registration"):
        evaluate_service_rule(configured, make_service())


def test_rejects_missing_required_evidence(rule):
    configured = change_rule(
        rule,
        evidence_fields=(*rule.evidence_fields, "missing_field"),
    )

    with pytest.raises(ValueError, match="required evidence"):
        evaluate_service_rule(configured, make_service())


def test_rejects_wrong_handler_rule_id(rule, monkeypatch):
    def incorrect_handler(service):
        return RuleObservation(
            rule_id="R08",
            entity_id=service.asset_id,
            status="confirmed",
            evidence=(),
        )

    monkeypatch.setitem(
        rule_engine.SERVICE_HANDLERS,
        ("R09", "telnet_service", "technical"),
        incorrect_handler,
    )

    with pytest.raises(ValueError, match="different rule ID"):
        evaluate_service_rule(rule, make_service())


@pytest.mark.parametrize(
    "clinic,expected",
    [
        ("lakeview_dental", set()),
        ("westside_health", {"WH-PR01"}),
    ],
)
def test_matches_sample_telnet_expectations(rule, clinic, expected):
    services = read_csv(
        (ROOT / "samples" / clinic / "services.csv").read_bytes(),
        "services",
    )
    actual = set()

    for service in services:
        finding = evaluate_service_rule(rule, service)
        if finding is not None:
            actual.add(finding.observation.entity_id)
            assert finding.observation.status == "confirmed"
            assert finding.severity == "High"

    assert actual == expected


def test_preserves_unknown_exposure(rule):
    finding = evaluate_service_rule(
        rule, make_service(exposure="unknown")
    )

    assert finding is not None
    assert dict(finding.observation.evidence)["exposure"] == "unknown"