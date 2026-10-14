from ipaddress import ip_address

from clinicshield.input_limits import InputError
from clinicshield.schemas import Asset, Service


def map_scan_assets(
    services: list[Service],
    assets: list[Asset],
    host_to_asset: dict[str, str],
) -> list[Service]:
    """Apply explicit host mappings without changing exposure or inputs."""
    if not isinstance(host_to_asset, dict):
        raise InputError("Provide host-to-asset mappings as a dictionary.")

    asset_ids = {asset.asset_id for asset in assets}
    scan_hosts = {service.host for service in services}
    mappings = {}

    for host, asset_id in host_to_asset.items():
        if not isinstance(host, str) or not isinstance(asset_id, str):
            raise InputError("Mapping hosts and asset IDs must be text.")

        try:
            normalized_host = str(ip_address(host.strip()))
        except ValueError:
            raise InputError(
                "A mapping contains an invalid host IP address."
            ) from None

        if normalized_host in mappings:
            raise InputError(
                "Each normalized host address may be mapped only once."
            )

        if normalized_host not in scan_hosts:
            raise InputError(
                "A mapping references a host absent from the scan services."
            )

        asset_id = asset_id.strip()
        if asset_id == "CLOUD" or asset_id not in asset_ids:
            raise InputError(
                "A mapping must reference an existing device asset ID."
            )

        mappings[normalized_host] = asset_id

    return [
        service.model_copy(
            update={
                "asset_id": mappings.get(service.host, service.asset_id)
            }
        )
        for service in services
    ]