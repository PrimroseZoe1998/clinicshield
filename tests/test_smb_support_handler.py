from datetime import datetime, timedelta, timezone

import pytest

from clinicshield.lifecycle_evidence import LifecycleEvidence
from clinicshield.lifecycle_handlers import smb_os_support
from clinicshield.schemas import Asset, Service


NOW = datetime(2026, 10, 27, 12, tzinfo=timezone.utc)
MAX_AGE = timedelta(days=8)


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


def make_evidence(**changes):
    data = {
        "os_name": "Example OS",
        "os_version": "1.0",
        "support_status": "unsupported",
        "support_basis": "Fictional support evidence for tests.",
        "extended_support": "confirmed_absent",
        "source_url": "https://example.org/support",
        "retrieved_at": NOW,
        "source_generated_at": NOW,
    }
    data.update(changes)
    return LifecycleEvidence(**data)


def evaluate(asset, service, evidence):
    return smb_os_support(
        asset, service, evidence, now=NOW, max_age=MAX_AGE
    )


def test_confirms_smb_on_unsupported_os(asset):
    result = evaluate(asset, make_service(), make_evidence())

    assert result is not None
    assert result.rule_id == "R08"
    assert result.entity_id == asset.asset_id
    assert result.status == "confirmed"
    evidence = dict(result.evidence)
    assert evidence["support_status"] == "unsupported"
    assert evidence["service"] == "smb"
    assert evidence["port"] == "445"
    assert evidence["exposure"] == "internal"
    assert len(result.evidence) == len(evidence)


def test_supported_os_does_not_trigger(asset):
    assert evaluate(
        asset,
        make_service(),
        make_evidence(support_status="supported"),
    ) is None


def test_missing_lifecycle_evidence_requires_review(asset):
    result = evaluate(asset, make_service(), None)

    assert result is not None
    assert result.status == "needs_review"
    assert dict(result.evidence)["support_status"] == "unknown"


@pytest.mark.parametrize(
    "changes",
    [
        {"os_version": "2.0"},
        {"support_status": "unknown"},
        {"extended_support": "active"},
        {"extended_support": "unknown"},
        {"source_generated_at": NOW - timedelta(days=9)},
        {"retrieved_at": None},
    ],
)
def test_unresolved_support_never_confirms_gap(asset, changes):
    result = evaluate(
        asset, make_service(), make_evidence(**changes)
    )

    assert result is not None
    assert result.status == "needs_review"


@pytest.mark.parametrize("service_name", ["other", "http", "rdp", "telnet"])
def test_port_445_alone_does_not_confirm_smb(asset, service_name):
    assert evaluate(
        asset,
        make_service(service=service_name),
        make_evidence(),
    ) is None


def test_udp_does_not_trigger_tcp_rule(asset):
    assert evaluate(
        asset, make_service(protocol="udp"), make_evidence()
    ) is None


def test_identified_smb_on_nonstandard_port_is_assessed(asset):
    result = evaluate(
        asset, make_service(port=1445), make_evidence()
    )

    assert result is not None
    assert dict(result.evidence)["port"] == "1445"


def test_rejects_service_for_different_asset(asset):
    with pytest.raises(ValueError, match="match the supplied asset"):
        evaluate(
            asset,
            make_service(asset_id="OTHER-ASSET"),
            make_evidence(),
        )


@pytest.mark.parametrize("exposure", ["internal", "internet", "unknown"])
def test_preserves_exposure(asset, exposure):
    result = evaluate(
        asset, make_service(exposure=exposure), make_evidence()
    )

    assert result is not None
    assert dict(result.evidence)["exposure"] == exposure


def test_does_not_modify_inputs(asset):
    service = make_service()
    evidence = make_evidence()
    originals = (
        asset.model_dump(),
        service.model_dump(),
        evidence.model_dump(),
    )

    evaluate(asset, service, evidence)

    assert (
        asset.model_dump(),
        service.model_dump(),
        evidence.model_dump(),
    ) == originals