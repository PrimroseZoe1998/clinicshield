from dataclasses import dataclass

from clinicshield.ingest import InputError
from clinicshield.schemas import Asset, Service, Software


@dataclass
class Inventory:
    assets: list[Asset]
    software: list[Software]
    services: list[Service]
    unmatched_service_rows: list[int]


def validate_inventory(
    assets: list[Asset],
    software: list[Software],
    services: list[Service] | None = None,
) -> Inventory:
    """Validate links without displaying uploaded identifiers or values."""
    assets = list(assets)
    software = list(software)
    services = list(services) if services is not None else []

    if not assets:
        raise InputError("Provide at least one asset.")

    asset_ids = {asset.asset_id for asset in assets}

    if len(asset_ids) != len(assets):
        raise InputError("Asset IDs must be unique.")

    if "CLOUD" in asset_ids:
        raise InputError(
            "CLOUD is reserved for cloud software. "
            "Use a different device asset ID."
        )

    for row_number, application in enumerate(software, start=1):
        asset_id = application.asset_id

        if asset_id in {"", "CLOUD"}:
            if application.deployment != "cloud":
                raise InputError(
                    f"Software entry {row_number} needs an existing "
                    "device asset ID for local deployment."
                )
            continue

        if asset_id not in asset_ids:
            raise InputError(
                f"Software entry {row_number} references an unknown asset. "
                "Use an existing asset ID, or CLOUD or blank "
                "for a cloud service."
            )

    # Unmatched services remain available for review.
    # Do not invent device settings for them.
    unmatched_service_rows = [
        row_number
        for row_number, service in enumerate(services, start=1)
        if service.asset_id not in asset_ids
    ]

    return Inventory(
        assets=assets,
        software=software,
        services=services,
        unmatched_service_rows=unmatched_service_rows,
    )

@dataclass(frozen=True)
class ScoringEntity:
    entity_id: str
    kind: str
    touches_phi: str
    internet_facing: str
    medical_device: bool | None


@dataclass(frozen=True)
class ScoringInventory:
    entities: tuple[ScoringEntity, ...]
    software_entity_ids: tuple[str, ...]
    service_entity_ids: tuple[str, ...]

def device_scoring_entities(
    inventory: Inventory,
) -> tuple[ScoringEntity, ...]:
    return tuple(
        ScoringEntity(
            entity_id=f"device:{asset.asset_id}",
            kind="device",
            touches_phi=asset.touches_phi,
            internet_facing=asset.internet_facing,
            medical_device=asset.asset_type == "medical_device",
        )
        for asset in inventory.assets
    )

def cloud_scoring_entities(
    inventory: Inventory,
) -> tuple[tuple[ScoringEntity, ...], tuple[str, ...]]:
    groups = {}
    software_ids = []

    for application in inventory.software:
        if application.deployment != "cloud":
            software_ids.append(f"device:{application.asset_id}")
            continue

        key = (
            application.vendor.strip().casefold(),
            application.product.strip().casefold(),
            application.purpose,
        )

        if key not in groups:
            groups[key] = {
                "entity_id": f"cloud:{len(groups) + 1}",
                "phi_values": set(),
            }

        group = groups[key]
        group["phi_values"].add(application.touches_phi)
        software_ids.append(group["entity_id"])

    entities = []

    for group in groups.values():
        values = group["phi_values"]
        if "Y" in values:
            phi = "Y"
        elif "Unknown" in values:
            phi = "Unknown"
        else:
            phi = "N"

        entities.append(
            ScoringEntity(
                entity_id=group["entity_id"],
                kind="cloud",
                touches_phi=phi,
                internet_facing="Unknown",
                medical_device=False,
            )
        )

    return tuple(entities), tuple(software_ids)

def unmatched_scoring_entities(
    inventory: Inventory,
) -> tuple[tuple[ScoringEntity, ...], tuple[str, ...]]:
    from ipaddress import ip_address

    device_ids = {asset.asset_id for asset in inventory.assets}
    groups = {}
    service_ids = []

    for service in inventory.services:
        if service.asset_id in device_ids:
            service_ids.append(f"device:{service.asset_id}")
            continue

        if service.host.strip():
            host = service.host.strip()
            try:
                host = str(ip_address(host))
            except ValueError:
                host = host.casefold()
            key = ("host", host)
        else:
            key = ("asset_id", service.asset_id)

        if key not in groups:
            groups[key] = {
                "entity_id": f"unmatched:{len(groups) + 1}",
                "exposures": set(),
            }

        group = groups[key]
        group["exposures"].add(service.exposure)
        service_ids.append(group["entity_id"])

    entities = []

    for group in groups.values():
        exposures = group["exposures"]
        if "internet" in exposures:
            exposure = "Y"
        elif exposures == {"internal"}:
            exposure = "N"
        else:
            exposure = "Unknown"

        entities.append(
            ScoringEntity(
                entity_id=group["entity_id"],
                kind="unmatched",
                touches_phi="Unknown",
                internet_facing=exposure,
                medical_device=None,
            )
        )

    return tuple(entities), tuple(service_ids)

def build_scoring_inventory(inventory: Inventory) -> ScoringInventory:
    validated = validate_inventory(
        inventory.assets,
        inventory.software,
        inventory.services,
    )

    devices = device_scoring_entities(validated)
    clouds, software_ids = cloud_scoring_entities(validated)
    unmatched, service_ids = unmatched_scoring_entities(validated)

    return ScoringInventory(
        entities=devices + clouds + unmatched,
        software_entity_ids=software_ids,
        service_entity_ids=service_ids,
    )