import csv
import io

from pydantic import ValidationError

from clinicshield.headers import map_headers
from clinicshield.input_limits import (
    MAX_CELL_CHARACTERS,
    MAX_COLUMNS,
    MAX_INVENTORY_ROWS,
    InputError,
    validate_upload,
)
from clinicshield.schemas import Asset, Service, Software


MODELS = {
    "assets": Asset,
    "software": Software,
    "services": Service,
}


def read_csv(data: bytes, kind: str) -> list:
    """Validate CSV bytes in memory without saving or logging them."""
    if kind not in MODELS:
        raise InputError("Choose assets, software, or services.")

    validate_upload(data)

    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise InputError("Save the CSV using UTF-8 encoding.") from None

    model = MODELS[kind]
    reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)

    try:
        original_headers = reader.fieldnames
        if not original_headers:
            raise InputError("The CSV needs a header row.")

        if len(original_headers) > MAX_COLUMNS:
            raise InputError("The CSV contains too many columns.")

        if any(
            len(header) > MAX_CELL_CHARACTERS
            for header in original_headers
        ):
            raise InputError("A CSV column name exceeds the length limit.")

        headers = map_headers(original_headers, kind)

        allowed = set(model.model_fields)
        required = {
            name
            for name, field in model.model_fields.items()
            if field.is_required()
        }

        if set(headers) - allowed:
            raise InputError("The CSV contains unsupported columns.")

        missing = sorted(required - set(headers))
        if missing:
            raise InputError(
                "Missing required columns: " + ", ".join(missing) + "."
            )

        reader.fieldnames = headers
        records = []

        for row_number, row in enumerate(reader, start=2):
            if row_number - 1 > MAX_INVENTORY_ROWS:
                raise InputError("The CSV contains too many data rows.")

            if None in row or any(value is None for value in row.values()):
                raise InputError(
                    f"CSV record {row_number} has the wrong number of values."
                )

            if any(
                len(value) > MAX_CELL_CHARACTERS
                for value in row.values()
            ):
                raise InputError("A CSV value exceeds the length limit.")

            if all(not value.strip() for value in row.values()):
                continue

            try:
                records.append(model.model_validate(row))
            except ValidationError:
                raise InputError(
                    f"CSV record {row_number} contains invalid fields. "
                    "Check the template and data dictionary."
                ) from None

        if not records:
            raise InputError("The CSV needs at least one data row.")

        if kind == "assets":
            ids = [record.asset_id for record in records]
            if len(ids) != len(set(ids)):
                raise InputError("Asset IDs must be unique.")

        return records

    except csv.Error:
        raise InputError(
            "The CSV formatting is invalid. Check commas and quotation marks."
        ) from None