from pathlib import Path

import pytest

from clinicshield.ingest import read_csv
from clinicshield.rule_engine import evaluate_asset_rule
from clinicshield.rule_loader import load_rule
from clinicshield.schemas import Asset


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "clinic,expected",
    [
        (
            "lakeview_dental",
            {"LV-LT01": ("confirmed", "High")},
        ),
        (
            "southside_counseling",
            {
                "SC-LT03": ("needs_review", "Info"),
                "SC-LT05": ("needs_review", "Info"),
            },
        ),
        (
            "westside_health",
            {"WH-LT01": ("needs_review", "Info")},
        ),
    ],
)
def test_r05_matches_documented_sample_expectations(clinic, expected):
    rule = load_rule(ROOT / "rules" / "R05.yaml")
    assets = read_csv(
        (ROOT / "samples" / clinic / "assets.csv").read_bytes(),
        "assets",
    )
    actual = {}

    for asset in assets:
        finding = evaluate_asset_rule(rule, asset)
        if finding is not None:
            actual[asset.asset_id] = (
                finding.observation.status,
                finding.severity,
            )

    assert actual == expected


@pytest.mark.parametrize(
    "clinic",
    [
        "lakeview_dental",
        "southside_counseling",
        "westside_health",
    ],
)
def test_verified_encryption_removes_r05_findings(clinic):
    rule = load_rule(ROOT / "rules" / "R05.yaml")
    assets = read_csv(
        (ROOT / "samples" / clinic / "assets.csv").read_bytes(),
        "assets",
    )

    for asset in assets:
        data = asset.model_dump()
        data["encrypted"] = "Y"
        corrected = Asset.model_validate(data)

        assert evaluate_asset_rule(rule, corrected) is None