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