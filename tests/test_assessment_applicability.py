import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from clinicshield.assessment_applicability import load_reviewed_applicability
from clinicshield.assessment_evidence import AssessmentEvidence
from clinicshield.input_limits import InputError
from clinicshield.matching import MatchStatus
from clinicshield.vulnerability_matching import evaluate_applicability

NOW = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)


def record():
    return {"review_status": "reviewed", "review_basis": "Fictional advisory comparison.",
            "evidence": {"software_entry_id": "software:1", "record_status": "active",
                         "source_generated_at": NOW.isoformat(), "record": {
                             "vulnerability_id": "CVE-2026-12345", "source": "Test advisory",
                             "source_url": "https://example.org/advisory",
                             "retrieved_at": NOW.isoformat(), "vendor": "Example Vendor",
                             "product": "Example App", "version_rule": "exact",
                             "affected_versions": ["1.0"], "version_evidence": "Test version list."}}}


def load(records, original=None):
    assessment = SimpleNamespace(inventory=SimpleNamespace(assets=[], software=[object()]))
    return load_reviewed_applicability(
        assessment, original or AssessmentEvidence(), json.dumps(records).encode(),
    )


@pytest.mark.parametrize("version,expected", [
    ("1.0", MatchStatus.MATCH), ("2.0", MatchStatus.NO_MATCH),
    ("Unknown", MatchStatus.NEEDS_REVIEW),
])
def test_reviewed_input_still_requires_matching_version(version, expected):
    evidence = load([record()]).vulnerabilities["software:1"][0]
    software = SimpleNamespace(vendor="Example Vendor", product="Example App", version=version)
    result = evaluate_applicability(
        software, evidence, entity_id="software:1", now=NOW, max_age=timedelta(days=8),
    )
    assert result.status is expected
    assert "Fictional advisory comparison" in evidence.record.version_evidence


def test_stale_source_requires_review_even_when_reviewed():
    item = record()
    item["evidence"]["source_generated_at"] = (NOW - timedelta(days=9)).isoformat()
    evidence = load([item]).vulnerabilities["software:1"][0]
    software = SimpleNamespace(vendor="Example Vendor", product="Example App", version="1.0")
    assert evaluate_applicability(
        software, evidence, entity_id="software:1", now=NOW, max_age=timedelta(days=8),
    ).status is MatchStatus.NEEDS_REVIEW


@pytest.mark.parametrize("case", ["draft", "blank", "orphan", "duplicate", "conflict"])
def test_rejects_invalid_or_conflicting_uploads(case):
    item = record()
    original = None
    if case == "draft":
        item["review_status"] = "draft"
    elif case == "blank":
        item["review_basis"] = " "
    elif case == "orphan":
        item["evidence"]["software_entry_id"] = "software:2"
    elif case == "conflict":
        original = load([record()])
    with pytest.raises(InputError):
        load([item, item] if case == "duplicate" else [item], original)
