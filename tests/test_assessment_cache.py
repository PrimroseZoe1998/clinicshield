from datetime import datetime, timedelta, timezone

import pytest

from clinicshield.assessment_cache import load_assessment_caches
from clinicshield.assessment_evidence import AssessmentEvidence
from clinicshield.kev_cache import KevSnapshot, write_kev_cache
from clinicshield.epss_cache import EpssSnapshot
from clinicshield.epss_cache_io import write_epss_cache


NOW = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)


def load(directory, evidence=None):
    return load_assessment_caches(
        evidence or AssessmentEvidence(), directory,
        now=NOW, max_age=timedelta(days=8),
    )


def test_missing_caches_preserve_unassessed_applicability(tmp_path):
    evidence, messages = load(tmp_path)
    assert evidence.kev_snapshot is None
    assert evidence.epss_snapshot is None
    assert not evidence.vulnerabilities
    assert sum("unavailable" in message for message in messages) == 2


@pytest.mark.parametrize("retrieved, status", [
    (NOW, "fresh"),
    (NOW - timedelta(days=9), "stale"),
    (NOW + timedelta(days=1), "needs_review"),
])
def test_attaches_valid_snapshot_with_freshness(tmp_path, retrieved, status):
    snapshot = KevSnapshot(
        retrieved_at=retrieved,
        catalog={"catalogVersion": "2026.10.29", "dateReleased": NOW,
                 "count": 0, "vulnerabilities": []},
    )
    write_kev_cache(tmp_path / "kev.json", snapshot)
    original = AssessmentEvidence()
    evidence, messages = load(tmp_path, original)
    assert evidence.kev_snapshot == snapshot
    assert original.kev_snapshot is None
    assert f"KEV cache retrieval status: {status}." in messages
    assert not evidence.vulnerabilities


def test_invalid_kev_does_not_prevent_epss_loading(tmp_path):
    (tmp_path / "kev.json").write_text("invalid")
    snapshot = EpssSnapshot(
        retrieved_at=NOW, model_version="test", score_date=NOW.date(),
        records=[{"cve": "CVE-2026-12345", "epss": "0.1",
                  "percentile": "0.5", "score_date": NOW.date()}],
    )
    write_epss_cache(tmp_path / "epss.json", snapshot)
    evidence, messages = load(tmp_path)
    assert evidence.kev_snapshot is None
    assert evidence.epss_snapshot == snapshot
    assert any("invalid or unreadable" in message for message in messages)


def test_fresh_retrieval_does_not_hide_old_source_date(tmp_path):
    write_kev_cache(tmp_path / "kev.json", KevSnapshot(
        retrieved_at=NOW,
        catalog={"catalogVersion": "2026.10.01",
                 "dateReleased": "2026-10-01T12:00:00Z",
                 "count": 0, "vulnerabilities": []},
    ))
    _, messages = load(tmp_path)
    assert any("source date 2026-10-01 requires freshness review" in m for m in messages)
