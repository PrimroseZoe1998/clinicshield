from dataclasses import dataclass

from clinicshield.input_limits import InputError


UNKNOWN_MARKERS = {"", "unknown", "n/a", "na", "not known", "unspecified"}


def normalize_name(value: str) -> str:
    if not isinstance(value, str):
        raise InputError("Vendor and product names must be text.")

    return " ".join(value.split()).casefold()


def normalize_version(value: str) -> str | None:
    if not isinstance(value, str):
        raise InputError("Software versions must be text.")

    cleaned = value.strip()

    if cleaned.casefold() in UNKNOWN_MARKERS:
        return None

    return cleaned


@dataclass(frozen=True)
class NormalizedSoftware:
    vendor: str
    product: str
    version: str | None


def normalize_software(
    vendor: str,
    product: str,
    version: str,
) -> NormalizedSoftware:
    normalized_vendor = normalize_name(vendor)
    normalized_product = normalize_name(product)

    if (
        normalized_vendor in UNKNOWN_MARKERS
        or normalized_product in UNKNOWN_MARKERS
    ):
        raise InputError("Provide a known vendor and product name.")

    return NormalizedSoftware(
        vendor=normalized_vendor,
        product=normalized_product,
        version=normalize_version(version),
    )