from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from clinicshield import rule_engine
from clinicshield.kev_cache import KevSnapshot
from clinicshield.rule_engine import evaluate_software_vulnerability_rule
from clinicshield.rule_loader import load_rule
from clinicshield.schemas import Software
from clinicshield.vulnerability_evidence import VulnerabilityEvidence


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)

REGISTRIES = (
    rule_engine.ASSET_HANDLERS,
    rule_engine.SERVICE_HANDLERS,
    rule_engine.CHECKLIST_HANDLERS,
    rule_engine.SOFTWARE_HANDLERS,
    rule_engine.SERVICE_CHECKLIST_HANDLERS,
    rule_engine.LIFECYCLE_HANDLERS,
    rule_engine.ASSET_SERVICE_LIFECYCLE_HANDLERS,
    rule_engine.CREDENTIAL_HANDLERS,
    rule_engine.SEGMENTATION_HANDLERS,
    rule_engine.APPLICATION_SUPPORT_HANDLERS,
    rule_engine.VULNERABILITY_HANDLERS,
)


def test_catalog_contains_exactly_24_unique_rules():
    paths = sorted((ROOT / "rules").glob("*.yaml"))
    rules = [load_rule(path) for path in paths]
    expected = {f"R{number:02d}" for number in range(1, 25)}

    assert len(rules) == 24
    assert {rule.rule_id for rule in rules} == expected
    assert all(
        path.stem == rule.rule_id
        for path, rule in zip(paths, rules)
    )


@pytest.mark.parametrize("number", range(1, 25))
def test_each_rule_has_exactly_one_registered_handler(number):
    rule = load_rule(ROOT / "rules" / f"R{number:02d}.yaml")
    key = (rule.rule_id, rule.handler, rule.kind)
    handlers = [
        registry[key] for registry in REGISTRIES if key in registry
    ]

    assert len(handlers) == 1
    assert callable(handlers[0])


def test_registrations_cover_each_rule_once():
    counts = Counter(
        key[0]
        for registry in REGISTRIES
        for key in registry
    )

    assert counts == {
        f"R{number:02d}": 1 for number in range(1, 25)
    }


@pytest.fixture
def software():
    return Software(
        asset_id="TEST-WS01",
        vendor="Example Vendor",
        product="Example Product",
        version="1.2.3",
        purpose="ehr",
        deployment="local",
        touches_phi="Y",
        mfa_enabled="Y",
    )


@pytest.fixture
def evidence():
    return VulnerabilityEvidence(
        software_entry_id="software:1",
        record={
            "vulnerability_id": "CVE-2026-12345",
            "source": "Synthetic vulnerability fixture",
            "source_url": "https://example.org/advisory",
            "retrieved_at": NOW,
            "vendor": "Example Vendor",
            "product": "Example Product",
            "version_rule": "exact",
            "affected_versions": ["1.2.3"],
        },
        record_status="active",
        source_generated_at=NOW,
    )


def make_kev(listed=False):
    entries = []
    if listed:
        entries.append({
            "cveID": "CVE-2026-12345",
            "vendorProject": "Example Vendor",
            "product": "Example Product",
            "vulnerabilityName": "Fictional vulnerability",
            "dateAdded": "2026-10-28",
            "shortDescription": "Synthetic test entry.",
            "requiredAction": "Follow fictional vendor guidance.",
            "dueDate": "2026-11-18",
        })
    return KevSnapshot(
        retrieved_at=NOW,
        catalog={
            "catalogVersion": "synthetic-test-catalog",
            "dateReleased": NOW,
            "count": len(entries),
            "vulnerabilities": entries,
        },
    )


def evaluate(rule_id, software, evidence, kev):
    return evaluate_software_vulnerability_rule(
        load_rule(ROOT / "rules" / f"{rule_id}.yaml"),
        software,
        evidence,
        kev,
        entity_id="software:1",
        now=NOW,
        max_age=timedelta(days=8),
    )


def test_r02_engine_confirms_applicable_nonlisted_cve(software, evidence):
    finding = evaluate("R02", software, evidence, make_kev())

    assert finding is not None
    assert finding.observation.rule_id == "R02"
    assert finding.observation.status == "confirmed"
    assert finding.severity == "High"
    assert finding.rule.review_status == "draft"


def test_r02_engine_uses_info_for_unknown_version(software, evidence):
    data = software.model_dump()
    data["version"] = "Unknown"

    finding = evaluate(
        "R02", Software.model_validate(data), evidence, make_kev()
    )

    assert finding is not None
    assert finding.observation.status == "needs_review"
    assert finding.severity == "Info"


@pytest.mark.parametrize(
    "listed,expected_rule",
    [(True, "R01"), (False, "R02")],
)
def test_engine_routes_cve_to_one_rule(
    software, evidence, listed, expected_rule
):
    findings = [
        finding
        for rule_id in ("R01", "R02")
        if (
            finding := evaluate(
                rule_id, software, evidence, make_kev(listed)
            )
        ) is not None
    ]

    assert len(findings) == 1
    assert findings[0].observation.rule_id == expected_rule


def test_missing_kev_uses_only_r01_review_path(software, evidence):
    first = evaluate("R01", software, evidence, None)
    second = evaluate("R02", software, evidence, None)

    assert first is not None
    assert first.observation.status == "needs_review"
    assert first.severity == "Info"
    assert second is None