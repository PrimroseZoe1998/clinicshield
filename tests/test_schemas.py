from datetime import date

import pytest
from pydantic import ValidationError

from clinicshield.schemas import Asset, Service, Software


def asset_data(**changes):
    data = {
        "asset_id": "TEST-01",
        "asset_name": "Test laptop",
        "asset_type": "laptop",
        "os_name": "Windows",
        "os_version": "11",
        "touches_phi": "Y",
        "internet_facing": "N",
        "encrypted": "Y",
    }
    return {**data, **changes}


def software_data(**changes):
    data = {
        "asset_id": "CLOUD",
        "vendor": "Example vendor",
        "product": "Example email",
        "version": "Unknown",
        "purpose": "email",
        "deployment": "cloud",
        "touches_phi": "Y",
        "mfa_enabled": "Y",
    }
    return {**data, **changes}


def service_data(**changes):
    data = {
        "asset_id": "TEST-01",
        "port": "8080",
        "protocol": "tcp",
        "service": "http",
        "exposure": "internal",
    }
    return {**data, **changes}


@pytest.mark.parametrize(
    "asset_type,expected",
    [
        ("laptop", "Y"),
        ("tablet", "Y"),
        ("phone", "Y"),
        ("server", "N"),
    ],
)
def test_asset_infers_portability(asset_type, expected):
    asset = Asset.model_validate(asset_data(asset_type=asset_type))
    assert asset.portable == expected


def test_asset_preserves_explicit_portability():
    asset = Asset.model_validate(asset_data(portable="N"))
    assert asset.portable == "N"


def test_asset_normalizes_blank_optional_fields():
    asset = Asset.model_validate(
        asset_data(
            portable=" ",
            auto_update=" ",
            network_segment=" ",
            last_patched="",
        )
    )
    assert asset.portable == "Y"
    assert asset.auto_update == "Unknown"
    assert asset.network_segment == "unknown"
    assert asset.last_patched is None


def test_asset_parses_patch_date():
    asset = Asset.model_validate(asset_data(last_patched="2026-10-13"))
    assert asset.last_patched == date(2026, 10, 13)


@pytest.mark.parametrize(
    "value",
    ["2026-02-30", "10/13/2026", "20261013", 1791849600],
)
def test_asset_rejects_invalid_patch_dates(value):
    with pytest.raises(ValidationError):
        Asset.model_validate(asset_data(last_patched=value))


@pytest.mark.parametrize(
    "changes",
    [
        {"asset_id": " "},
        {"os_version": ""},
        {"touches_phi": "Yes"},
        {"encrypted": "NA"},
        {"unexpected_column": "value"},
    ],
)
def test_asset_rejects_invalid_fields(changes):
    with pytest.raises(ValidationError):
        Asset.model_validate(asset_data(**changes))


def test_software_normalizes_blank_answers():
    software = Software.model_validate(
        software_data(auto_update=" ", baa_signed="")
    )
    assert software.auto_update == "Unknown"
    assert software.baa_signed == "Unknown"


def test_software_rejects_cloud_marker_for_local_software():
    with pytest.raises(ValidationError):
        Software.model_validate(software_data(deployment="local"))


@pytest.mark.parametrize(
    "changes",
    [
        {"vendor": ""},
        {"purpose": "invalid"},
        {"mfa_enabled": "Yes"},
        {"unexpected_column": "value"},
    ],
)
def test_software_rejects_invalid_fields(changes):
    with pytest.raises(ValidationError):
        Software.model_validate(software_data(**changes))


@pytest.mark.parametrize("value,expected", [("1", 1), ("65535", 65535), (8080, 8080)])
def test_service_accepts_valid_ports(value, expected):
    service = Service.model_validate(service_data(port=value))
    assert service.port == expected


@pytest.mark.parametrize(
    "value",
    [0, 65536, -1, True, 80.5, "80.5", "", "abc"],
)
def test_service_rejects_invalid_ports(value):
    with pytest.raises(ValidationError):
        Service.model_validate(service_data(port=value))


def test_service_normalizes_blank_version():
    service = Service.model_validate(service_data(version=" "))
    assert service.version == "Unknown"


@pytest.mark.parametrize(
    "changes",
    [
        {"asset_id": ""},
        {"protocol": "icmp"},
        {"exposure": "public"},
        {"unexpected_column": "value"},
    ],
)
def test_service_rejects_invalid_fields(changes):
    with pytest.raises(ValidationError):
        Service.model_validate(service_data(**changes))