import json
from datetime import date

import pytest
from pydantic import ValidationError

from clinicshield.kev_models import KevCatalog


@pytest.fixture
def catalog_data():
    return {
        "catalogVersion": "2026.10.26",
        "dateReleased": "2026-10-26T12:00:00Z",
        "count": 1,
        "vulnerabilities": [
            {
                "cveID": "CVE-2026-12345",
                "vendorProject": "Example Vendor",
                "product": "Product-X",
                "vulnerabilityName": "Example vulnerability",
                "dateAdded": "2026-10-26",
                "shortDescription": "Example description.",
                "requiredAction": "Apply vendor updates.",
                "dueDate": "2026-11-16",
                "knownRansomwareCampaignUse": "Unknown",
                "notes": "https://example.org/advisory",
            }
        ],
    }


def test_parses_catalog_json(catalog_data):
    catalog = KevCatalog.model_validate_json(json.dumps(catalog_data))

    assert catalog.count == 1
    assert catalog.vulnerabilities[0].cveID == "CVE-2026-12345"
    assert catalog.vulnerabilities[0].dateAdded == date(2026, 10, 26)
    assert catalog.dateReleased.utcoffset().total_seconds() == 0


def test_preserves_additional_source_fields(catalog_data):
    catalog_data["newCatalogField"] = "source metadata"
    catalog_data["vulnerabilities"][0]["newEntryField"] = "source detail"

    catalog = KevCatalog.model_validate(catalog_data)

    assert catalog.model_extra["newCatalogField"] == "source metadata"
    entry = catalog.vulnerabilities[0]
    assert entry.model_extra["newEntryField"] == "source detail"
    assert entry.model_extra["knownRansomwareCampaignUse"] == "Unknown"


def test_json_round_trip_preserves_catalog(catalog_data):
    catalog = KevCatalog.model_validate(catalog_data)

    restored = KevCatalog.model_validate_json(catalog.model_dump_json())

    assert restored == catalog


def test_accepts_empty_catalog(catalog_data):
    catalog_data.update(count=0, vulnerabilities=[])

    assert KevCatalog.model_validate(catalog_data).vulnerabilities == ()


@pytest.mark.parametrize("count", [0, 2])
def test_rejects_count_mismatch(catalog_data, count):
    catalog_data["count"] = count

    with pytest.raises(ValidationError, match="count"):
        KevCatalog.model_validate(catalog_data)


def test_rejects_duplicate_cve_ids(catalog_data):
    entry = catalog_data["vulnerabilities"][0]
    catalog_data.update(count=2, vulnerabilities=[entry, dict(entry)])

    with pytest.raises(ValidationError, match="duplicate"):
        KevCatalog.model_validate(catalog_data)


@pytest.mark.parametrize("count", [-1, True, "1", 1.5])
def test_rejects_invalid_count(catalog_data, count):
    catalog_data["count"] = count

    with pytest.raises(ValidationError):
        KevCatalog.model_validate(catalog_data)


@pytest.mark.parametrize(
    "cve_id",
    ["", "CVE-2026-123", "cve-2026-12345", "OTHER-2026-12345"],
)
def test_rejects_invalid_cve_id(catalog_data, cve_id):
    catalog_data["vulnerabilities"][0]["cveID"] = cve_id

    with pytest.raises(ValidationError):
        KevCatalog.model_validate(catalog_data)


@pytest.mark.parametrize("field", ["dateAdded", "dueDate"])
def test_rejects_invalid_entry_dates(catalog_data, field):
    catalog_data["vulnerabilities"][0][field] = "2026-02-30"

    with pytest.raises(ValidationError):
        KevCatalog.model_validate(catalog_data)


def test_rejects_release_time_without_timezone(catalog_data):
    catalog_data["dateReleased"] = "2026-10-26T12:00:00"

    with pytest.raises(ValidationError, match="timezone"):
        KevCatalog.model_validate(catalog_data)


@pytest.mark.parametrize(
    "field",
    [
        "cveID",
        "vendorProject",
        "product",
        "vulnerabilityName",
        "dateAdded",
        "shortDescription",
        "requiredAction",
        "dueDate",
    ],
)
def test_requires_entry_fields(catalog_data, field):
    del catalog_data["vulnerabilities"][0][field]

    with pytest.raises(ValidationError):
        KevCatalog.model_validate(catalog_data)


def test_catalog_is_frozen(catalog_data):
    catalog = KevCatalog.model_validate(catalog_data)

    with pytest.raises(ValidationError):
        catalog.catalogVersion = "changed"