import csv
from pathlib import Path

import pytest

from clinicshield.privacy import REJECTION_MESSAGE, validate_headers


@pytest.mark.parametrize(
    "header",
    [
        "patient_name",
        "PATIENT",
        " Date Of Birth ",
        "medical-record",
        "insurance_id",
        "notes_patient_details",
        "email_address",
    ],
)
def test_rejects_patient_information_headers(header):
    with pytest.raises(ValueError) as error:
        validate_headers(["asset_id", header])

    assert str(error.value) == REJECTION_MESSAGE


@pytest.mark.parametrize("name", ["assets", "software", "services"])
def test_inventory_template_headers_are_allowed(name):
    project = Path(__file__).resolve().parents[1]
    path = project / "templates" / f"{name}.csv"

    with path.open(encoding="utf-8-sig", newline="") as source:
        headers = next(csv.reader(source))

    validate_headers(headers)