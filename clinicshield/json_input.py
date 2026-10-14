import json
import math

from pydantic import ValidationError

from clinicshield.headers import map_headers
from clinicshield.ingest import MODELS
from clinicshield.input_limits import (
    MAX_CELL_CHARACTERS,
    MAX_INVENTORY_ROWS,
    InputError,
    validate_upload,
)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError("JSON keys must be unique.")
        result[key] = value
    return result


def reject_constant(value):
    raise InputError("JSON must not contain NaN or Infinity.")


def read_inventory_json(data: bytes, kind: str) -> list:
    """Validate a JSON array of inventory objects in memory."""
    if kind not in MODELS:
        raise InputError("Choose assets, software, or services.")

    validate_upload(data)

    try:
        text = data.decode("utf-8-sig")
        rows = json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except InputError:
        raise
    except (UnicodeDecodeError, ValueError, RecursionError):
        raise InputError("Provide valid UTF-8 inventory JSON.") from None

    if not isinstance(rows, list):
        raise InputError("Inventory JSON must contain an array of objects.")

    if not rows:
        raise InputError("The inventory needs at least one entry.")

    if len(rows) > MAX_INVENTORY_ROWS:
        raise InputError("The inventory contains too many entries.")

    model = MODELS[kind]
    allowed = set(model.model_fields)
    required = {
        name
        for name, field in model.model_fields.items()
        if field.is_required()
    }

    prepared = []

    # Check every object's field names before validating inventory values.
    for row in rows:
        if not isinstance(row, dict):
            raise InputError("Every inventory entry must be an object.")

        original_headers = list(row)
        headers = map_headers(original_headers, kind)

        if set(headers) - allowed:
            raise InputError("The inventory contains unsupported fields.")

        missing = sorted(required - set(headers))
        if missing:
            raise InputError(
                "Missing required fields: " + ", ".join(missing) + "."
            )

        prepared.append(
            dict(zip(headers, row.values()))
        )

    records = []

    for entry_number, row in enumerate(prepared, start=1):
        for value in row.values():
            if isinstance(value, (dict, list)):
                raise InputError(
                    "Inventory field values must not be objects or arrays."
                )

            if isinstance(value, str) and len(value) > MAX_CELL_CHARACTERS:
                raise InputError("An inventory value exceeds the length limit.")

            if isinstance(value, float) and not math.isfinite(value):
                raise InputError("Inventory numbers must be finite.")

        try:
            records.append(model.model_validate(row))
        except ValidationError:
            raise InputError(
                f"Inventory entry {entry_number} contains invalid fields. "
                "Check the template and data dictionary."
            ) from None

    if kind == "assets":
        ids = [record.asset_id for record in records]
        if len(ids) != len(set(ids)):
            raise InputError("Asset IDs must be unique.")

    return records