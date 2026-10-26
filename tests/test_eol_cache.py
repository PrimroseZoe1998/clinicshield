from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from clinicshield.eol_cache import EolSnapshot
from clinicshield.eol_download import EOL_BASE_URL


@pytest.fixture
def snapshot_data():
    return {
        "source_url": f"{EOL_BASE_URL}python/",
        "retrieved_at": datetime(2026, 10, 26, 14, tzinfo=timezone.utc),
        "product": "python",
        "response": {
            "schema_version": "1.2.1",
            "generated_at": "2026-10-26T00:00:00Z",
            "last_modified": "2026-10-25T12:00:00Z",
            "result": {
                "name": "python",
                "label": "Python",
                "releases": [
                    {
                        "name": "3.10",
                        "isEol": True,
                        "eolFrom": "2026-10-01",
                        "isMaintained": False,
                    }
                ],
            },
        },
    }


def test_preserves_provenance_and_source_timestamps(snapshot_data):
    snapshot = EolSnapshot(**snapshot_data)

    assert snapshot.source == "endoflife.date"
    assert snapshot.product == "python"
    assert snapshot.source_url == f"{EOL_BASE_URL}python/"
    assert snapshot.retrieved_at == snapshot_data["retrieved_at"]
    assert snapshot.retrieved_at != snapshot.response.generated_at
    assert snapshot.response.result.releases[0].isEol is True


def test_json_round_trip_preserves_snapshot(snapshot_data):
    snapshot = EolSnapshot(**snapshot_data)

    restored = EolSnapshot.model_validate_json(snapshot.model_dump_json())

    assert restored == snapshot


def test_preserves_unknown_support_status(snapshot_data):
    release = snapshot_data["response"]["result"]["releases"][0]
    release.update(isEol=None, eolFrom=None, isMaintained=None)

    snapshot = EolSnapshot(**snapshot_data)

    assert snapshot.response.result.releases[0].isEol is None
    assert snapshot.response.result.releases[0].isMaintained is None


@pytest.mark.parametrize(
    "changes",
    [
        {"source": "Other source"},
        {"schema_version": 2},
        {"unexpected": "value"},
        {"product": ""},
        {"product": "Python"},
        {"product": "../python"},
    ],
)
def test_rejects_invalid_metadata(snapshot_data, changes):
    snapshot_data.update(changes)

    with pytest.raises(ValidationError):
        EolSnapshot(**snapshot_data)


def test_requires_retrieval_timezone(snapshot_data):
    snapshot_data["retrieved_at"] = datetime(2026, 10, 26, 14)

    with pytest.raises(ValidationError, match="timezone"):
        EolSnapshot(**snapshot_data)


def test_rejects_mismatched_response_product(snapshot_data):
    snapshot_data["response"]["result"]["name"] = "other-product"

    with pytest.raises(ValidationError, match="match the product"):
        EolSnapshot(**snapshot_data)


@pytest.mark.parametrize(
    "source_url",
    [
        f"{EOL_BASE_URL}other-product/",
        "https://example.org/python/",
        f"{EOL_BASE_URL}python",
    ],
)
def test_rejects_mismatched_source_url(snapshot_data, source_url):
    snapshot_data["source_url"] = source_url

    with pytest.raises(ValidationError, match="Source URL"):
        EolSnapshot(**snapshot_data)


def test_validates_nested_response(snapshot_data):
    snapshot_data["response"]["result"]["releases"][0]["isEol"] = "yes"

    with pytest.raises(ValidationError):
        EolSnapshot(**snapshot_data)


@pytest.mark.parametrize(
    "field",
    ["source_url", "retrieved_at", "product", "response"],
)
def test_requires_snapshot_fields(snapshot_data, field):
    del snapshot_data[field]

    with pytest.raises(ValidationError):
        EolSnapshot(**snapshot_data)


def test_snapshot_is_frozen(snapshot_data):
    snapshot = EolSnapshot(**snapshot_data)

    with pytest.raises(ValidationError):
        snapshot.product = "other-product"