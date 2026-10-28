from datetime import datetime, timedelta, timezone

import pytest

from clinicshield.assessment_evidence import (
    AssessmentEvidence,
    AssessmentFreshnessPolicy,
)
from clinicshield.credential_evidence import DefaultPasswordEvidence
from clinicshield.vulnerability_evidence import VulnerabilityEvidence


NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)


def make_password_evidence():
    return DefaultPasswordEvidence(
        asset_id="TEST-RT01",
        applicability="Yes",
        default_password_changed="No",
        evidence_basis="Fictional administrator confirmation.",
        evidence_source="Synthetic test fixture",
        observed_at=NOW,
    )


def make_vulnerability_evidence():
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


def test_public_feed_default_is_eight_days():
    policy = AssessmentFreshnessPolicy(
        administrator_observation_max_age=timedelta(days=30)
    )

    assert policy.public_feed_max_age == timedelta(days=8)
    assert policy.administrator_observation_max_age == timedelta(days=30)


def test_freshness_limits_are_independent():
    policy = AssessmentFreshnessPolicy(
        administrator_observation_max_age=timedelta(days=14),
        public_feed_max_age=timedelta(days=3),
    )

    assert policy.public_feed_max_age == timedelta(days=3)
    assert policy.administrator_observation_max_age == timedelta(days=14)


def test_administrator_age_has_no_implicit_default():
    with pytest.raises(TypeError):
        AssessmentFreshnessPolicy()


@pytest.mark.parametrize(
    "field",
    ["administrator_observation_max_age", "public_feed_max_age"],
)
@pytest.mark.parametrize(
    "value",
    [timedelta(0), timedelta(seconds=-1), 8, "8 days", None],
)
def test_rejects_invalid_freshness_limits(field, value):
    values = {
        "administrator_observation_max_age": timedelta(days=30),
        "public_feed_max_age": timedelta(days=8),
    }
    values[field] = value

    with pytest.raises(ValueError, match="positive durations"):
        AssessmentFreshnessPolicy(**values)


def test_empty_bundle_preserves_missing_coverage():
    evidence = AssessmentEvidence()

    assert not evidence.os_support
    assert not evidence.application_support
    assert not evidence.default_passwords
    assert not evidence.medical_separation
    assert not evidence.vulnerabilities
    assert evidence.kev_snapshot is None
    assert evidence.epss_snapshot is None


@pytest.mark.parametrize(
    "field",
    [
        "os_support",
        "application_support",
        "default_passwords",
        "medical_separation",
        "vulnerabilities",
    ],
)
def test_bundle_mappings_cannot_be_modified(field):
    evidence = AssessmentEvidence()

    with pytest.raises(TypeError):
        getattr(evidence, field)["new-key"] = None


def test_copies_caller_mapping():
    observation = make_password_evidence()
    original = {"TEST-RT01": observation}
    bundle = AssessmentEvidence(default_passwords=original)

    original.clear()

    assert bundle.default_passwords["TEST-RT01"] is observation


def test_vulnerability_sequences_are_copied_to_tuples():
    record = make_vulnerability_evidence()
    original_records = [record]
    original_mapping = {"software:1": original_records}

    bundle = AssessmentEvidence(vulnerabilities=original_mapping)
    original_records.clear()
    original_mapping.clear()

    assert bundle.vulnerabilities["software:1"] == (record,)
    assert isinstance(bundle.vulnerabilities["software:1"], tuple)


def test_separate_bundles_do_not_share_mappings():
    first = AssessmentEvidence(
        default_passwords={"TEST-RT01": make_password_evidence()}
    )
    second = AssessmentEvidence()

    assert len(first.default_passwords) == 1
    assert not second.default_passwords


def test_policy_is_frozen():
    policy = AssessmentFreshnessPolicy(
        administrator_observation_max_age=timedelta(days=30)
    )

    with pytest.raises(AttributeError):
        policy.public_feed_max_age = timedelta(days=1)


def test_bundle_is_frozen():
    evidence = AssessmentEvidence()

    with pytest.raises(AttributeError):
        evidence.kev_snapshot = None