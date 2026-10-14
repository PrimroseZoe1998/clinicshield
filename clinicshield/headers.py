from clinicshield.input_limits import (
    MAX_CELL_CHARACTERS,
    MAX_COLUMNS,
    InputError,
)
from clinicshield.privacy import validate_headers


ALIASES = {
    "assets": {
        "device": "asset_name",
        "computer_name": "asset_name",
    },
    "software": {
        "software_vendor": "vendor",
        "software_name": "product",
        "software_version": "version",
        "device_id": "asset_id",
    },
    "services": {
        "device_id": "asset_id",
        "port_number": "port",
        "transport": "protocol",
        "service_name": "service",
    },
}


def normalize_header(header: str) -> str:
    return "_".join(
        header.strip().casefold().replace("-", " ").split()
    )


def map_headers(headers: list[str], kind: str) -> list[str]:
    """Check privacy before applying explicit, unambiguous aliases."""
    if kind not in ALIASES:
        raise InputError("Choose assets, software, or services.")

    if len(headers) > MAX_COLUMNS:
        raise InputError("The input contains too many columns.")

    if any(not isinstance(header, str) for header in headers):
        raise InputError("Column names must be text.")

    if any(len(header) > MAX_CELL_CHARACTERS for header in headers):
        raise InputError("A column name exceeds the length limit.")

    try:
        validate_headers(headers)
    except ValueError as exc:
        raise InputError(str(exc)) from None

    normalized = [normalize_header(header) for header in headers]

    if any(not header for header in normalized):
        raise InputError("Every column needs a name.")

    mapped = [
        ALIASES[kind].get(header, header)
        for header in normalized
    ]

    if len(mapped) != len(set(mapped)):
        raise InputError(
            "Column names must be unique after header mapping."
        )

    return mapped