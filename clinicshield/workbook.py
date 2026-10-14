import csv
import io
from datetime import date, datetime
from zipfile import BadZipFile

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from clinicshield.ingest import InputError, read_csv
from clinicshield.privacy import validate_headers


def cell_text(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        if value.time().isoformat() != "00:00:00":
            raise InputError("Date cells must not contain a time.")
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def read_workbook(data: bytes) -> dict:
    """Read inventory sheets in memory without saving uploaded content."""
    if not isinstance(data, bytes):
        raise InputError("Provide workbook data as bytes.")

    try:
        workbook = load_workbook(
            io.BytesIO(data),
            read_only=True,
            data_only=False,
            keep_links=False,
        )
    except (BadZipFile, InvalidFileException, OSError, ValueError, KeyError):
        raise InputError("Provide a valid Excel .xlsx workbook.") from None

    try:
        # Inspect every sheet before processing inventory rows.
        for sheet in workbook.worksheets:
            first_row = next(sheet.iter_rows(), ())
            headers = [cell_text(cell.value) for cell in first_row]

            try:
                validate_headers(headers)
            except ValueError as exc:
                raise InputError(str(exc)) from None

            if any(cell.data_type == "f" for cell in first_row):
                raise InputError("Column names must not contain formulas.")

        if not {"assets", "software"}.issubset(workbook.sheetnames):
            raise InputError(
                "The workbook needs assets and software sheets."
            )

        result = {"assets": [], "software": [], "services": []}

        for kind in result:
            if kind not in workbook.sheetnames:
                continue

            sheet = workbook[kind]
            stream = io.StringIO(newline="")
            writer = csv.writer(stream)
            has_data = False

            for row_number, row in enumerate(sheet.iter_rows(), start=1):
                if any(cell.data_type == "f" for cell in row):
                    raise InputError(
                        "Inventory cells must contain values, not formulas."
                    )

                if any(cell.data_type == "e" for cell in row):
                    raise InputError(
                        "Inventory cells must not contain Excel errors."
                    )

                values = [cell_text(cell.value) for cell in row]

                if row_number == 1:
                    # Excel may retain formatting beyond the last header.
                    while values and not values[-1].strip():
                        values.pop()
                    width = len(values)
                    writer.writerow(values)
                    continue

                if any(value.strip() for value in values[width:]):
                    raise InputError(
                        "Inventory data extends beyond the named columns."
                    )

                values = values[:width]
                values.extend([""] * (width - len(values)))

                if any(value.strip() for value in values):
                    has_data = True

                writer.writerow(values)

            # A services sheet may be omitted or have headers only.
            if kind == "services" and not has_data:
                continue

            result[kind] = read_csv(
                stream.getvalue().encode("utf-8"), kind
            )

        return result

    finally:
        workbook.close()