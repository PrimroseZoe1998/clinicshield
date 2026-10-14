from dataclasses import dataclass

from clinicshield.checklist_input import Checklist, read_checklist
from clinicshield.ingest import InputError, read_csv
from clinicshield.inventory import Inventory, validate_inventory
from clinicshield.nmap_input import read_nmap
from clinicshield.workbook import read_workbook


@dataclass
class AssessmentInput:
    inventory: Inventory
    checklist: Checklist


def read_assessment(
    *,
    checklist_json: bytes,
    followups_json: bytes,
    workbook_xlsx: bytes | None = None,
    assets_csv: bytes | None = None,
    software_csv: bytes | None = None,
    services_csv: bytes | None = None,
    nmap_xml: bytes | None = None,
    scan_authorized: bool = False,
) -> AssessmentInput:
    """Validate assessment inputs in memory without saving or logging them."""
    if workbook_xlsx is not None:
        if any(
            data is not None
            for data in (assets_csv, software_csv, services_csv)
        ):
            raise InputError(
                "Choose either an Excel workbook or CSV inventories."
            )

        sheets = read_workbook(workbook_xlsx)
        assets = sheets["assets"]
        software = sheets["software"]
        services = sheets["services"]

    else:
        if assets_csv is None or software_csv is None:
            raise InputError(
                "Provide both assets and software CSV files, "
                "or an Excel workbook."
            )

        assets = read_csv(assets_csv, "assets")
        software = read_csv(software_csv, "software")
        services = (
            read_csv(services_csv, "services")
            if services_csv is not None
            else []
        )

    if nmap_xml is not None:
        services.extend(
            read_nmap(nmap_xml, authorized=scan_authorized)
        )

    inventory = validate_inventory(assets, software, services)
    checklist = read_checklist(checklist_json, followups_json)

    return AssessmentInput(
        inventory=inventory,
        checklist=checklist,
    )