from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from clinicshield.epss_cache import EpssSnapshot
from clinicshield.epss_download import EPSS_URL


@pytest.fixture
def snapshot_data():
    return {
        "retrieved_at": datetime(2026, 10, 26, 14, tzinfo=timezone.utc),
        "model_version": "v2026.06.15",
        "score_date": "2026-10-26",
        "records": [
            {
                "cve": "CVE-2026-12345",
                "epss": "0.123456789",
                "percentile": "0.987654321",
                "score_date": "2026-10-26",
            }
        ],
    }


def test_preserves_metadata_and_scores(snapshot_data):
    snapshot = EpssSnapshot(**snapshot_data)

    assert snapshot.source == "FIRST EPSS"
    assert snapshot.source_url == EPSS_URL
    assert snapshot.model_version == "v2026.06.15"
    assert snapshot.score_date == date(2026, 10, 26)
    assert snapshot.retrieved_at == snapshot_data["retrieved_at"]
    assert snapshot.records[0].epss == Decimal("0.123456789")


def test_json_round_trip_preserves_snapshot(snapshot_data):
    snapshot = EpssSnapshot(**snapshot_data)

    restored = EpssSnapshot.model_validate_json(
        snapshot.model_dump_json()
    )

    assert restored == snapshot


@pytest.mark.parametrize(
    "changes",
    [
        {"source": "Other source"},
        {"source_url": "https://example.org/feed.csv.gz"},
        {"schema_version": 2},
        {"unexpected": "value"},
        {"model_version": ""},
        {"model_version": "   "},
        {"records": []},
    ],
)
def test_rejects_invalid_snapshot_fields(snapshot_data, changes):
    snapshot_data.update(changes)

    with pytest.raises(ValidationError):
        EpssSnapshot(**snapshot_data)


def test_rejects_retrieval_time_without_timezone(snapshot_data):
    snapshot_data["retrieved_at"] = datetime(2026, 10, 26, 14)

    with pytest.raises(ValidationError, match="timezone"):
        EpssSnapshot(**snapshot_data)


def test_rejects_mismatched_record_date(snapshot_data):
    snapshot_data["records"][0]["score_date"] = "2026-10-25"

    with pytest.raises(ValidationError, match="score dates must match"):
        EpssSnapshot(**snapshot_data)


def test_rejects_duplicate_cves(snapshot_data):
    record = snapshot_data["records"][0]
    snapshot_data["records"].append(dict(record))

    with pytest.raises(ValidationError, match="Duplicate"):
        EpssSnapshot(**snapshot_data)


def test_accepts_distinct_cves(snapshot_data):
    record = dict(snapshot_data["records"][0])
    record["cve"] = "CVE-2026-67890"
    snapshot_data["records"].append(record)

    assert len(EpssSnapshot(**snapshot_data).records) == 2


def test_validates_nested_scores(snapshot_data):
    snapshot_data["records"][0]["epss"] = "1.1"

    with pytest.raises(ValidationError):
        EpssSnapshot(**snapshot_data)


@pytest.mark.parametrize(
    "field",
    ["retrieved_at", "model_version", "score_date", "records"],
)
def test_requires_snapshot_fields(snapshot_data, field):
    del snapshot_data[field]

    with pytest.raises(ValidationError):
        EpssSnapshot(**snapshot_data)


def test_snapshot_is_frozen(snapshot_data):
    snapshot = EpssSnapshot(**snapshot_data)

    with pytest.raises(ValidationError):
        snapshot.model_version = "changed"