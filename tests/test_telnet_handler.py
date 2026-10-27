import pytest

from clinicshield.rule_handlers import telnet_service
from clinicshield.schemas import Service


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


def test_identified_telnet_produces_confirmed_observation():
    result = telnet_service(make_service())

    assert result is not None
    assert result.rule_id == "R09"
    assert result.entity_id == "TEST-PR01"
    assert result.status == "confirmed"
    assert dict(result.evidence) == {
        "asset_id": "TEST-PR01",
        "host": "192.0.2.10",
        "port": "23",
        "protocol": "tcp",
        "service": "telnet",
        "exposure": "internal",
    }


@pytest.mark.parametrize("port", [23, 2323, 8023])
def test_identified_telnet_triggers_on_any_tcp_port(port):
    assert telnet_service(make_service(port=port)) is not None


@pytest.mark.parametrize("exposure", ["internal", "internet", "unknown"])
def test_preserves_reported_exposure(exposure):
    result = telnet_service(make_service(exposure=exposure))

    assert result is not None
    assert dict(result.evidence)["exposure"] == exposure


@pytest.mark.parametrize("service_name", ["other", "ssh", "http", "rdp"])
def test_port_23_alone_does_not_confirm_telnet(service_name):
    service = make_service(service=service_name, port=23)

    assert telnet_service(service) is None


def test_udp_telnet_label_does_not_trigger_tcp_rule():
    assert telnet_service(make_service(protocol="udp")) is None


def test_blank_host_does_not_discard_identified_telnet():
    result = telnet_service(make_service(host=""))

    assert result is not None
    assert result.entity_id == "TEST-PR01"
    assert dict(result.evidence)["host"] == ""


def test_detection_does_not_modify_service():
    service = make_service(exposure="unknown")
    original = service.model_dump()

    telnet_service(service)

    assert service.model_dump() == original