from pathlib import Path

import pytest

from clinicshield.ingest import read_csv
from clinicshield.rule_engine import evaluate_service_rule
from clinicshield.rule_handlers import remote_admin_exposure
from clinicshield.rule_loader import load_rule
from clinicshield.schemas import Service


ROOT = Path(__file__).resolve().parents[1]


def make_service(**changes):
    data = {
        "asset_id": "TEST-SRV01",
        "host": "192.0.2.10",
        "port": 3389,
        "protocol": "tcp",
        "service": "rdp",
        "exposure": "internet",
    }
    data.update(changes)
    return Service(**data)


@pytest.mark.parametrize("service_name", ["rdp", "vnc", "ssh", "telnet"])
@pytest.mark.parametrize(
    "exposure,expected",
    [
        ("internet", "confirmed"),
        ("unknown", "needs_review"),
        ("internal", None),
    ],
)
def test_remote_service_exposure_combinations(
    service_name, exposure, expected
):
    result = remote_admin_exposure(
        make_service(service=service_name, exposure=exposure)
    )

    if expected is None:
        assert result is None
    else:
        assert result is not None
        assert result.rule_id == "R06"
        assert result.entity_id == "TEST-SRV01"
        assert result.status == expected
        assert dict(result.evidence)["service"] == service_name
        assert dict(result.evidence)["exposure"] == exposure


@pytest.mark.parametrize("port", [23, 22, 3389, 5900])
def test_port_alone_does_not_confirm_remote_service(port):
    assert remote_admin_exposure(
        make_service(service="other", port=port)
    ) is None


@pytest.mark.parametrize("service_name", ["http", "https", "smb", "dicom"])
def test_other_services_are_outside_scope(service_name):
    assert remote_admin_exposure(
        make_service(service=service_name)
    ) is None


@pytest.mark.parametrize("service_name", ["rdp", "vnc", "ssh", "telnet"])
def test_udp_does_not_trigger_tcp_rule(service_name):
    assert remote_admin_exposure(
        make_service(service=service_name, protocol="udp")
    ) is None


def test_identified_service_on_nonstandard_port_is_assessed():
    result = remote_admin_exposure(make_service(port=13389))

    assert result is not None
    assert dict(result.evidence)["port"] == "13389"


def test_preserves_evidence_without_inventing_authentication_status():
    result = remote_admin_exposure(make_service(exposure="unknown"))

    assert result is not None
    assert result.status == "needs_review"
    assert dict(result.evidence) == {
        "asset_id": "TEST-SRV01",
        "host": "192.0.2.10",
        "port": "3389",
        "protocol": "tcp",
        "service": "rdp",
        "exposure": "unknown",
    }


@pytest.mark.parametrize(
    "exposure,status,severity",
    [
        ("internet", "confirmed", "High"),
        ("unknown", "needs_review", "Info"),
    ],
)
def test_yaml_rule_runs_through_engine(exposure, status, severity):
    rule = load_rule(ROOT / "rules" / "R06.yaml")

    finding = evaluate_service_rule(
        rule, make_service(exposure=exposure)
    )

    assert finding is not None
    assert finding.observation.status == status
    assert finding.severity == severity
    assert finding.rule.review_status == "draft"


def test_internal_exposure_produces_no_engine_finding():
    rule = load_rule(ROOT / "rules" / "R06.yaml")

    assert evaluate_service_rule(
        rule, make_service(exposure="internal")
    ) is None


def test_does_not_modify_service():
    service = make_service()
    original = service.model_dump()

    remote_admin_exposure(service)

    assert service.model_dump() == original


@pytest.mark.parametrize("clinic", ["lakeview_dental", "westside_health"])
def test_sample_internal_services_do_not_trigger(clinic):
    rule = load_rule(ROOT / "rules" / "R06.yaml")
    services = read_csv(
        (ROOT / "samples" / clinic / "services.csv").read_bytes(),
        "services",
    )

    assert all(
        evaluate_service_rule(rule, service) is None
        for service in services
    )