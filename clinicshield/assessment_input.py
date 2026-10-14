from dataclasses import dataclass

from clinicshield.checklist_input import Checklist, read_checklist
from clinicshield.ingest import read_csv
from clinicshield.input_limits import InputError
from clinicshield.inventory import Inventory, validate_inventory
from clinicshield.json_input import read_inventory_json
from clinicshield.nmap_input import read_nmap
from clinicshield.scan_mapping import map_scan_assets
from clinicshield.workbook import read_workbook


@dataclass
class AssessmentInput:
    inventory: Inventory
    checklist: Checklist


def read_inventory_file(
    kind: str,
    csv_data: bytes | None,
    json_data: bytes | None,
    *,
    required: bool,
) -> list:
    if csv_data is not None and json_data is not None:
        raise InputError(
            "Provide each inventory once, as either CSV or JSON."
        )

    if csv_data is not None:
        return read_csv(csv_data, kind)

    if json_data is not None:
        return read_inventory_json(json_data, kind)

    if required:
        raise InputError(
            "Provide both assets and software inventories "
            "as CSV or JSON, or an Excel workbook."
        )

    return []


def read_assessment(
    *,
    checklist_json: bytes,
    followups_json: bytes,
    workbook_xlsx: bytes | None = None,
    assets_csv: bytes | None = None,
    software_csv: bytes | None = None,
    services_csv: bytes | None = None,
    assets_json: bytes | None = None,
    software_json: bytes | None = None,
    services_json: bytes | None = None,
    nmap_xml: bytes | None = None,
    scan_authorized: bool = False,
    scan_host_to_asset: dict[str, str] | None = None,
) -> AssessmentInput:
    """Validate assessment inputs in memory without saving or logging them."""
    if scan_host_to_asset is not None and nmap_xml is None:
        raise InputError("Provide Nmap XML when supplying scan host mappings.")

    if workbook_xlsx is not None:
        if any(
            data is not None
            for data in (
                assets_csv,
                software_csv,
                services_csv,
                assets_json,
                software_json,
                services_json,
            )
        ):
            raise InputError(
                "Choose either an Excel workbook or separate "
                "CSV/JSON inventories."
            )

        sheets = read_workbook(workbook_xlsx)
        assets = sheets["assets"]
        software = sheets["software"]
        services = sheets["services"]

    else:
        assets = read_inventory_file(
            "assets", assets_csv, assets_json, required=True
        )
        software = read_inventory_file(
            "software", software_csv, software_json, required=True
        )
        services = read_inventory_file(
            "services", services_csv, services_json, required=False
        )

    if nmap_xml is not None:
        scanned_services = read_nmap(
            nmap_xml, authorized=scan_authorized
        )

        if scan_host_to_asset is not None:
            scanned_services = map_scan_assets(
                scanned_services,
                assets,
                scan_host_to_asset,
            )

        services.extend(scanned_services)

    inventory = validate_inventory(assets, software, services)
    checklist = read_checklist(checklist_json, followups_json)

    return AssessmentInput(
        inventory=inventory,
        checklist=checklist,
    )