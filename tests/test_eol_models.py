from datetime import date

import pytest
from pydantic import ValidationError

from clinicshield.eol_models import EolResponse


@pytest.fixture
def response_data():
    return {
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
    }


def test_preserves_release_status_and_dates(response_data):
    response = EolResponse(**response_data)
    release = response.result.releases[0]

    assert response.result.name == "python"
    assert release.name == "3.10"
    assert release.isEol is True
    assert release.eolFrom == date(2026, 10, 1)
    assert release.isMaintained is False
    assert response.generated_at.utcoffset().total_seconds() == 0


def test_preserves_unknown_support_status(response_data):
    release = response_data["result"]["releases"][0]
    release.update(isEol=None, eolFrom=None, isMaintained=None)

    result = EolResponse(**response_data).result.releases[0]

    assert result.isEol is None
    assert result.eolFrom is None
    assert result.isMaintained is None


def test_preserves_additional_source_fields(response_data):
    response_data["extraMetadata"] = "source detail"
    response_data["result"]["aliases"] = ["cpython"]
    response_data["result"]["releases"][0]["isLts"] = False

    response = EolResponse(**response_data)

    assert response.model_extra["extraMetadata"] == "source detail"
    assert response.result.model_extra["aliases"] == ["cpython"]
    assert response.result.releases[0].model_extra["isLts"] is False


def test_json_round_trip(response_data):
    response = EolResponse(**response_data)

    restored = EolResponse.model_validate_json(response.model_dump_json())

    assert restored == response


@pytest.mark.parametrize("field", ["isEol", "isMaintained"])
@pytest.mark.parametrize("value", ["true", "false", 0, 1])
def test_rejects_nonboolean_support_flags(response_data, field, value):
    response_data["result"]["releases"][0][field] = value

    with pytest.raises(ValidationError):
        EolResponse(**response_data)


@pytest.mark.parametrize("field", ["name", "isEol", "eolFrom", "isMaintained"])
def test_requires_release_fields(response_data, field):
    del response_data["result"]["releases"][0][field]

    with pytest.raises(ValidationError):
        EolResponse(**response_data)


def test_rejects_invalid_eol_date(response_data):
    response_data["result"]["releases"][0]["eolFrom"] = "2026-02-30"

    with pytest.raises(ValidationError):
        EolResponse(**response_data)


def test_rejects_duplicate_release_names(response_data):
    release = response_data["result"]["releases"][0]
    response_data["result"]["releases"].append(dict(release))

    with pytest.raises(ValidationError, match="Duplicate"):
        EolResponse(**response_data)


def test_accepts_distinct_release_names(response_data):
    release = dict(response_data["result"]["releases"][0])
    release["name"] = "3.11"
    response_data["result"]["releases"].append(release)

    assert len(EolResponse(**response_data).result.releases) == 2


@pytest.mark.parametrize("field", ["generated_at", "last_modified"])
def test_requires_timezone_on_source_timestamps(response_data, field):
    response_data[field] = "2026-10-26T12:00:00"

    with pytest.raises(ValidationError, match="timezone"):
        EolResponse(**response_data)


@pytest.mark.parametrize("version", ["2.0.0", "1", "invalid"])
def test_rejects_unsupported_schema_version(response_data, version):
    response_data["schema_version"] = version

    with pytest.raises(ValidationError):
        EolResponse(**response_data)


@pytest.mark.parametrize(
    "field",
    ["schema_version", "generated_at", "last_modified", "result"],
)
def test_requires_response_fields(response_data, field):
    del response_data[field]

    with pytest.raises(ValidationError):
        EolResponse(**response_data)


def test_response_is_frozen(response_data):
    response = EolResponse(**response_data)

    with pytest.raises(ValidationError):
        response.schema_version = "1.0.0"