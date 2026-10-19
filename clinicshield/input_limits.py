MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_ASSESSMENT_BYTES = 20 * 1024 * 1024
MAX_JSON_BYTES = 64 * 1024
MAX_INVENTORY_ROWS = 10_000
MAX_COLUMNS = 50
MAX_CELL_CHARACTERS = 10_000

MAX_WORKBOOK_UNCOMPRESSED_BYTES = 50 * 1024 * 1024
MAX_WORKBOOK_MEMBERS = 1_000
MAX_WORKBOOK_SHEETS = 20


class InputError(ValueError):
    """An input error safe to display without exposing uploaded values."""


def validate_upload(
    data: bytes,
    *,
    max_bytes: int = MAX_UPLOAD_BYTES,
) -> None:
    if not isinstance(data, bytes):
        raise InputError("Provide uploaded file data as bytes.")

    if len(data) > max_bytes:
        raise InputError(
            "The uploaded file exceeds the supported size limit."
        )

def validate_assessment_uploads(*uploads: bytes | None) -> None:
    total = 0

    for data in uploads:
        if data is None:
            continue

        if not isinstance(data, bytes):
            raise InputError("Provide uploaded file data as bytes.")

        total += len(data)

        if total > MAX_ASSESSMENT_BYTES:
            raise InputError(
                "The combined assessment uploads exceed "
                "the supported size limit."
            )