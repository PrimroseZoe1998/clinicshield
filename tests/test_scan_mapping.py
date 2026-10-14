from pathlib import Path

import pytest

from clinicshield.assessment_input import read_assessment
from clinicshield.input_limits import InputError
from clinicshield.scan_mapping import map_scan_assets
from clinicshield.schemas import Asset, Service


SAMPLES = Path(__file__).resolve().parents[1] / "samples"


def make_asset(asset_id="TEST-01"):
    return Asset(
        asset_id=asset_id,
        asset_name="Test server",
        asset_type="server",
        os_name="Linux",
        os_version="Unknown",
        touches_phi="Unknown",
        internet_facing="Unknown",
        encrypted="Unknown",
    )


def make_service(host="192.0.2.2", port=8080):
    return Service(
        asset_id=host,
        host=host,
        port=port,
        protocol="tcp",
        service="http",
        exposure="unknown",
    )


def assessment_inputs():
    folder = SAMPLES / "westside_health"
    return {
        "assets_csv": (folder / "assets.csv").read_bytes(),
        "software_csv": (folder / "software.csv").read_bytes(),
        "services_csv": (folder / "services.csv").read_bytes(),
        "checklist_json": (folder / "checklist.json").read_bytes(),
        "followups_json": (folder / "followups.json").read_bytes(),
        "nmap_xml": (SAMPLES / "lab_scan.xml").read_bytes(),
        "scan_authorized": True,
    }


def test_maps_host_without_changing_other_fields():
    original = make_service()
    mapped = map_scan_assets(
        [original], [make_asset()], {"192.0.2.2": "TEST-01"}
    )[0]

    assert mapped.asset_id == "TEST-01"
    assert mapped.host == original.host
    assert mapped.port == original.port
    assert mapped.exposure == "unknown"
    assert mapped.model_dump(exclude={"asset_id"}) == (
        original.model_dump(exclude={"asset_id"})
    )


def test_does_not_mutate_original_services():
    original = make_service()
    mapped = map_scan_assets(
        [original], [make_asset()], {"192.0.2.2": "TEST-01"}
    )
    assert original.asset_id == "192.0.2.2"
    assert mapped[0] is not original


def test_preserves_unmapped_hosts():
    services = [make_service(), make_service("192.0.2.3")]
    mapped = map_scan_assets(
        services, [make_asset()], {"192.0.2.2": "TEST-01"}
    )
    assert [service.asset_id for service in mapped] == [
        "TEST-01", "192.0.2.3"
    ]


def test_maps_all_ports_for_one_host():
    mapped = map_scan_assets(
        [make_service(port=80), make_service(port=8080)],
        [make_asset()],
        {"192.0.2.2": "TEST-01"},
    )
    assert [service.asset_id for service in mapped] == [
        "TEST-01", "TEST-01"
    ]


def test_empty_mapping_preserves_services():
    original = make_service()
    mapped = map_scan_assets([original], [make_asset()], {})
    assert mapped[0].model_dump() == original.model_dump()


def test_normalizes_mapping_whitespace():
    mapped = map_scan_assets(
        [make_service()],
        [make_asset()],
        {" 192.0.2.2 ": " TEST-01 "},
    )
    assert mapped[0].asset_id == "TEST-01"


def test_normalizes_ipv6_mapping():
    mapped = map_scan_assets(
        [make_service("2001:db8::2")],
        [make_asset()],
        {"2001:0db8:0:0:0:0:0:2": "TEST-01"},
    )
    assert mapped[0].asset_id == "TEST-01"


def test_rejects_duplicate_normalized_hosts():
    with pytest.raises(InputError, match="only once"):
        map_scan_assets(
            [make_service("2001:db8::2")],
            [make_asset()],
            {
                "2001:db8::2": "TEST-01",
                "2001:0db8:0:0:0:0:0:2": "TEST-01",
            },
        )


@pytest.mark.parametrize("mapping", [None, [], "text"])
def test_rejects_non_dictionary_mapping(mapping):
    with pytest.raises(InputError, match="dictionary"):
        map_scan_assets([make_service()], [make_asset()], mapping)


@pytest.mark.parametrize(
    "mapping",
    [{123: "TEST-01"}, {"192.0.2.2": 123}],
)
def test_rejects_non_text_mapping_values(mapping):
    with pytest.raises(InputError, match="must be text"):
        map_scan_assets([make_service()], [make_asset()], mapping)


def test_rejects_invalid_host_safely():
    with pytest.raises(InputError) as error:
        map_scan_assets(
            [make_service()],
            [make_asset()],
            {"PRIVATE_SENTINEL": "TEST-01"},
        )
    assert "invalid host IP" in str(error.value)
    assert "PRIVATE_SENTINEL" not in str(error.value)


def test_rejects_host_absent_from_scan():
    with pytest.raises(InputError, match="absent from the scan"):
        map_scan_assets(
            [make_service()],
            [make_asset()],
            {"192.0.2.99": "TEST-01"},
        )


@pytest.mark.parametrize("asset_id", ["PRIVATE_SENTINEL", "CLOUD", ""])
def test_rejects_invalid_device_link_safely(asset_id):
    with pytest.raises(InputError) as error:
        map_scan_assets(
            [make_service()],
            [make_asset()],
            {"192.0.2.2": asset_id},
        )
    assert "existing device asset ID" in str(error.value)
    assert "PRIVATE_SENTINEL" not in str(error.value)


def test_assessment_applies_explicit_lab_mapping():
    values = assessment_inputs()
    values["scan_host_to_asset"] = {"192.0.2.2": "WH-SRV03"}

    result = read_assessment(**values)

    scanned = result.inventory.services[-1]
    assert scanned.asset_id == "WH-SRV03"
    assert scanned.host == "192.0.2.2"
    assert scanned.exposure == "unknown"
    assert result.inventory.unmatched_service_rows == []


def test_assessment_rejects_mapping_without_scan():
    values = assessment_inputs()
    del values["nmap_xml"]
    values["scan_host_to_asset"] = {"192.0.2.2": "WH-SRV03"}

    with pytest.raises(InputError, match="Provide Nmap XML"):
        read_assessment(**values)


def test_mapping_does_not_bypass_scan_authorization():
    values = assessment_inputs()
    values["scan_authorized"] = False
    values["scan_host_to_asset"] = {"192.0.2.2": "WH-SRV03"}

    with pytest.raises(InputError, match="Confirm"):
        read_assessment(**values)