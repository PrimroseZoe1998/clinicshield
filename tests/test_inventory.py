from pathlib import Path

import pytest

from clinicshield.ingest import InputError, read_csv
from clinicshield.inventory import validate_inventory
from clinicshield.schemas import Asset, Service, Software


SAMPLES = Path(__file__).resolve().parents[1] / "samples"


def make_asset(asset_id="TEST-01"):
    return Asset(
        asset_id=asset_id,
        asset_name="Test laptop",
        asset_type="laptop",
        os_name="Windows",
        os_version="11",
        touches_phi="Y",
        internet_facing="N",
        encrypted="Y",
    )


def make_software(asset_id="TEST-01", deployment="local"):
    return Software(
        asset_id=asset_id,
        vendor="Example vendor",
        product="Example application",
        version="Unknown",
        purpose="office",
        deployment=deployment,
        touches_phi="N",
        mfa_enabled="NA",
    )


def make_service(asset_id="TEST-01"):
    return Service(
        asset_id=asset_id,
        port=8080,
        protocol="tcp",
        service="http",
        exposure="unknown",
    )


@pytest.mark.parametrize(
    "clinic",
    ["lakeview_dental", "southside_counseling", "westside_health"],
)
def test_sample_inventory_links(clinic):
    folder = SAMPLES / clinic
    assets = read_csv((folder / "assets.csv").read_bytes(), "assets")
    software = read_csv(
        (folder / "software.csv").read_bytes(), "software"
    )
    service_file = folder / "services.csv"
    services = (
        read_csv(service_file.read_bytes(), "services")
        if service_file.exists()
        else []
    )

    inventory = validate_inventory(assets, software, services)
    assert inventory.unmatched_service_rows == []


def test_accepts_linked_local_software():
    inventory = validate_inventory(
        [make_asset()], [make_software()]
    )
    assert len(inventory.software) == 1


@pytest.mark.parametrize("asset_id", ["", "CLOUD", "TEST-01"])
def test_accepts_cloud_software(asset_id):
    inventory = validate_inventory(
        [make_asset()],
        [make_software(asset_id=asset_id, deployment="cloud")],
    )
    assert len(inventory.software) == 1


def test_rejects_local_software_without_asset_id():
    with pytest.raises(InputError, match="existing device asset ID"):
        validate_inventory(
            [make_asset()], [make_software(asset_id="")]
        )


@pytest.mark.parametrize("deployment", ["local", "cloud"])
def test_rejects_unknown_software_asset_safely(deployment):
    with pytest.raises(InputError) as error:
        validate_inventory(
            [make_asset()],
            [
                make_software(
                    asset_id="PRIVATE_SENTINEL",
                    deployment=deployment,
                )
            ],
        )
    assert "unknown asset" in str(error.value)
    assert "PRIVATE_SENTINEL" not in str(error.value)


def test_rejects_empty_assets():
    with pytest.raises(InputError, match="at least one asset"):
        validate_inventory([], [])


def test_rejects_duplicate_asset_ids():
    with pytest.raises(InputError, match="must be unique"):
        validate_inventory([make_asset(), make_asset()], [])


def test_rejects_reserved_device_id():
    with pytest.raises(InputError, match="reserved for cloud software"):
        validate_inventory([make_asset("CLOUD")], [])


def test_services_are_optional():
    inventory = validate_inventory([make_asset()], [])
    assert inventory.services == []
    assert inventory.unmatched_service_rows == []


def test_preserves_and_flags_unmatched_services():
    services = [
        make_service(),
        make_service("192.0.2.2"),
        make_service("UNKNOWN-DEVICE"),
    ]
    inventory = validate_inventory([make_asset()], [], services)

    assert inventory.unmatched_service_rows == [2, 3]
    assert len(inventory.services) == 3
    assert inventory.services[1].exposure == "unknown"
    assert len(inventory.assets) == 1


def test_copies_input_lists():
    assets = [make_asset()]
    software = [make_software()]
    services = [make_service()]
    inventory = validate_inventory(assets, software, services)

    assets.clear()
    software.clear()
    services.clear()

    assert len(inventory.assets) == 1
    assert len(inventory.software) == 1
    assert len(inventory.services) == 1