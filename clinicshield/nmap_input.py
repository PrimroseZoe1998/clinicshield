from ipaddress import ip_address
from xml.etree.ElementTree import ParseError

from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException
from pydantic import ValidationError

from clinicshield.ingest import InputError
from clinicshield.schemas import Service


SERVICE_NAMES = {
    "rdp": "rdp",
    "ms-wbt-server": "rdp",
    "smb": "smb",
    "microsoft-ds": "smb",
    "netbios-ssn": "smb",
    "ssh": "ssh",
    "http": "http",
    "https": "https",
    "ssl/http": "https",
    "ftp": "ftp",
    "telnet": "telnet",
    "vnc": "vnc",
    "dicom": "dicom",
}


def read_nmap(data: bytes, *, authorized: bool = False) -> list[Service]:
    """Parse existing scan results; never start a network scan."""
    if authorized is not True:
        raise InputError(
            "Confirm the scan was run on a network your organization "
            "owns or has written permission to scan."
        )

    if not isinstance(data, bytes):
        raise InputError("Provide Nmap XML data as bytes.")

    try:
        root = ElementTree.fromstring(
            data,
            forbid_dtd=False,
            forbid_entities=True,
            forbid_external=True,
        )
    except (ParseError, DefusedXmlException, ValueError):
        raise InputError("Provide valid, safe Nmap XML.") from None

    if root.tag != "nmaprun" or root.get("scanner") != "nmap":
        raise InputError("Provide an Nmap XML scan result.")

    records = []

    for host in root.findall("host"):
        status = host.find("status")
        if status is None or status.get("state") != "up":
            continue

        address = next(
            (
                element.get("addr", "")
                for element in host.findall("address")
                if element.get("addrtype") in {"ipv4", "ipv6"}
            ),
            None,
        )

        if address is None:
            raise InputError("An active scan host is missing its IP address.")

        try:
            address = str(ip_address(address))
        except ValueError:
            raise InputError(
                "An active scan host has an invalid IP address."
            ) from None

        for port in host.findall("./ports/port"):
            state = port.find("state")
            if state is None or state.get("state") != "open":
                continue

            details = port.find("service")
            name = details.get("name", "") if details is not None else ""
            service_name = SERVICE_NAMES.get(name.casefold(), "other")

            if (
                service_name == "http"
                and details is not None
                and details.get("tunnel") == "ssl"
            ):
                service_name = "https"

            product = (
                details.get("product", "")
                if details is not None
                else ""
            )
            version = (
                details.get("version", "") or "Unknown"
                if details is not None
                else "Unknown"
            )

            try:
                record = Service(
                    asset_id=address,
                    host=address,
                    port=port.get("portid", ""),
                    protocol=port.get("protocol", ""),
                    service=service_name,
                    product=product,
                    version=version,
                    exposure="unknown",
                )
            except ValidationError:
                raise InputError(
                    "An open service has invalid port or protocol fields."
                ) from None

            records.append(record)

    return records