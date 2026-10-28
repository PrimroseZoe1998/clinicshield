from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from clinicshield.eol_cache import EolSnapshot
from clinicshield.eol_download import EOL_BASE_URL
from clinicshield.lifecycle_adapter import lifecycle_evidence_from_cache
from clinicshield.lifecycle_mapping import OsReleaseMapping
from clinicshield.rule_engine import evaluate_asset_lifecycle_rule
from clinicshield.rule_loader import load_rule
from clinicshield.schemas import Asset


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 27, 12, tzinfo=timezone.utc)


@pytest.fixture
def asset():
    return Asset(
        asset_id="TEST-WS01",
        asset_name="Test workstation",
        asset_type="workstation",
        os_name="Example OS",
        os_version="1.0 Enterprise",
        touches_phi="Y",
        internet_facing="N",
        encrypted="Y",
    )


def make_mapping(**changes):
    data = {
        "os_name": "Example OS",
        "os_version": "1.0 Enterprise",
        "product": "example-os",
        "release_name": "1",
        "mapping_basis": "Fictional explicit mapping for tests.",
    }
    data.update(changes)
    return OsReleaseMapping(**data)


def make_snapshot(*, generated_at=NOW, **release_changes):
    release = {
        "name": "1",
        "isEol": True,
        "eolFrom": "2026-10-01",
        "isMaintained": False,
    }
    release.update(release_changes)
    return EolSnapshot(
        source_url=f"{EOL_BASE_URL}example-os/",
        retrieved_at=NOW,
        product="example-os",
        response={
            "schema_version": "1.2.1",
            "generated_at": generated_at,
            "last_modified": generated_at,
            "result": {
                "name": "example-os",
                "label": "Example OS",
                "releases": [release],
            },
        },
    )


def adapt(asset, snapshot, **options):
    return lifecycle_evidence_from_cache(
        asset, make_mapping(), snapshot, now=NOW, **options
    )


def test_preserves_mapping_source_and_coverage_evidence(asset):
    snapshot = make_snapshot()

    evidence = adapt(
        asset,
        snapshot,
        extended_support="confirmed_absent",
        coverage_basis="Fictional device coverage confirmation.",
    )

    assert evidence is not None
    assert evidence.os_version == asset.os_version
    assert evidence.support_status == "unsupported"
    assert evidence.extended_support == "confirmed_absent"
    assert str(evidence.source_url) == snapshot.source_url
    assert evidence.retrieved_at == snapshot.retrieved_at
    assert evidence.source_generated_at == snapshot.response.generated_at
    assert "Fictional explicit mapping" in evidence.support_basis
    assert "Fictional device coverage confirmation" in evidence.support_basis


@pytest.mark.parametrize("missing", ["mapping", "snapshot"])
def test_missing_input_returns_no_evidence(asset, missing):
    assert lifecycle_evidence_from_cache(
        asset,
        None if missing == "mapping" else make_mapping(),
        None if missing == "snapshot" else make_snapshot(),
        now=NOW,
    ) is None


@pytest.mark.parametrize(
    "changes",
    [
        {"os_name": "Other OS"},
        {"os_version": "1.0"},
        {"product": "other-os"},
        {"release_name": "missing-release"},
    ],
)
def test_requires_exact_explicit_mapping(asset, changes):
    assert lifecycle_evidence_from_cache(
        asset,
        make_mapping(**changes),
        make_snapshot(),
        now=NOW,
    ) is None


@pytest.mark.parametrize(
    "release_changes,expected",
    [
        (
            {"isEol": False, "isMaintained": True, "eolFrom": "2027-01-01"},
            "supported",
        ),
        (
            {"isEol": False, "isMaintained": True, "eolFrom": None},
            "supported",
        ),
        (
            {"isEol": False, "isMaintained": True, "eolFrom": "2026-10-27"},
            "unknown",
        ),
        (
            {"isEol": True, "eolFrom": "2027-01-01"},
            "unknown",
        ),
        (
            {"isEol": None, "eolFrom": None},
            "unknown",
        ),
        (
            {"isEol": False, "isMaintained": None},
            "unknown",
        ),
        (
            {"isEol": True, "eolFrom": None},
            "unsupported",
        ),
    ],
)
def test_support_status_boundaries(asset, release_changes, expected):
    evidence = adapt(asset, make_snapshot(**release_changes))

    assert evidence is not None
    assert evidence.support_status == expected


@pytest.mark.parametrize(
    "coverage,expected",
    [
        ("confirmed_absent", "confirmed"),
        ("unknown", "needs_review"),
        ("active", "needs_review"),
    ],
)
def test_adapter_connects_to_r03(asset, coverage, expected):
    rule = load_rule(ROOT / "rules" / "R03.yaml")
    evidence = adapt(
        asset, make_snapshot(), extended_support=coverage
    )

    finding = evaluate_asset_lifecycle_rule(
        rule,
        asset,
        evidence,
        now=NOW,
        max_age=timedelta(days=8),
    )

    assert finding is not None
    assert finding.observation.status == expected


def test_fresh_retrieval_does_not_hide_stale_source(asset):
    rule = load_rule(ROOT / "rules" / "R03.yaml")
    evidence = adapt(
        asset,
        make_snapshot(generated_at=NOW - timedelta(days=9)),
        extended_support="confirmed_absent",
    )

    finding = evaluate_asset_lifecycle_rule(
        rule,
        asset,
        evidence,
        now=NOW,
        max_age=timedelta(days=8),
    )

    assert finding is not None
    assert finding.observation.status == "needs_review"


def test_rejects_naive_clock(asset):
    with pytest.raises(ValueError, match="timezone"):
        lifecycle_evidence_from_cache(
            asset,
            make_mapping(),
            make_snapshot(),
            now=NOW.replace(tzinfo=None),
        )


@pytest.mark.parametrize("basis", ["", "   ", None])
def test_requires_coverage_basis(asset, basis):
    with pytest.raises(ValueError, match="evidence basis"):
        adapt(asset, make_snapshot(), coverage_basis=basis)