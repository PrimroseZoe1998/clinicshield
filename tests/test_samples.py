import csv
import json
from pathlib import Path

import pytest

from clinicshield.privacy import validate_headers

SAMPLES = Path(__file__).resolve().parents[1] / "samples"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        validate_headers(reader.fieldnames)
        rows = list(reader)

    assert all(None not in row for row in rows)
    assert all(value is not None for row in rows for value in row.values())
    return rows


@pytest.mark.parametrize(
    "clinic,asset_count,software_count,service_count",
    [
        ("lakeview_dental", 11, 4, 3),
        ("southside_counseling", 9, 5, 0),
        ("westside_health", 35, 5, 3),
    ],
)
def test_sample_inventory_and_checklist(
    clinic, asset_count, software_count, service_count
):
    folder = SAMPLES / clinic
    assets = read_csv(folder / "assets.csv")
    software = read_csv(folder / "software.csv")

    assert len(assets) == asset_count
    assert len(software) == software_count

    asset_ids = {row["asset_id"] for row in assets}
    assert len(asset_ids) == len(assets)
    assert "" not in asset_ids

    for row in software:
        assert row["asset_id"] in asset_ids | {"", "CLOUD"}

    services_path = folder / "services.csv"
    services = read_csv(services_path) if services_path.exists() else []
    assert len(services) == service_count

    for row in services:
        assert row["asset_id"] in asset_ids
        assert 1 <= int(row["port"]) <= 65535
        assert row["protocol"] in {"tcp", "udp"}
        assert row["exposure"] in {"internal", "internet", "unknown"}

    answers = json.loads(
        (folder / "checklist.json").read_text(encoding="utf-8-sig")
    )
    assert set(answers) == {f"Q{n:02d}" for n in range(1, 26)}
    assert all(value in {"Yes", "No", "Unknown"} for value in answers.values())


@pytest.mark.parametrize(
    "clinic",
    ["lakeview_dental", "southside_counseling", "westside_health"],
)
def test_q24_followups_match_combined_answer(clinic):
    folder = SAMPLES / clinic
    followups = json.loads(
        (folder / "followups.json").read_text(encoding="utf-8-sig")
    )
    answers = json.loads(
        (folder / "checklist.json").read_text(encoding="utf-8-sig")
    )

    assert set(followups) == {"Q24a", "Q24b"}
    assert all(
        value in {"Yes", "No", "Unknown"}
        for value in followups.values()
    )

    values = list(followups.values())
    if all(value == "Yes" for value in values):
        combined = "Yes"
    elif "No" in values:
        combined = "No"
    else:
        combined = "Unknown"

    assert answers["Q24"] == combined