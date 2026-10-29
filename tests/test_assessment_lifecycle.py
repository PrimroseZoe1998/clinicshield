import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from clinicshield.assessment_evidence import AssessmentEvidence
from clinicshield.assessment_lifecycle import read_lifecycle_mappings, load_assessment_lifecycle
from clinicshield.eol_cache import EolSnapshot
from clinicshield.eol_cache_io import write_eol_cache
from clinicshield.eol_download import EOL_BASE_URL
from clinicshield.input_limits import InputError
from clinicshield.schemas import Asset

NOW = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)


def record(**changes):
    result = {"asset_id": "A1", "review_status": "reviewed", "mapping": {
        "os_name": "Example OS", "os_version": "1.0", "product": "example-os",
        "release_name": "1", "mapping_basis": "Fictional test mapping only.",
    }}
    result.update(changes)
    return result


def load(tmp_path, records=None, evidence=None):
    asset = Asset(asset_id="A1", asset_name="Test", asset_type="workstation",
                  os_name="Example OS", os_version="1.0", touches_phi="Y",
                  internet_facing="N", encrypted="Y")
    assessment = SimpleNamespace(inventory=SimpleNamespace(assets=[asset]))
    mappings = read_lifecycle_mappings(json.dumps(records or [record()]).encode())
    return load_assessment_lifecycle(
        assessment, evidence or AssessmentEvidence(), mappings, tmp_path,
        now=NOW, max_age=timedelta(days=8),
    )


def write_snapshot(tmp_path, generated=NOW, release="1"):
    snapshot = EolSnapshot(
        source_url=f"{EOL_BASE_URL}example-os/", retrieved_at=NOW, product="example-os",
        response={"schema_version": "1.2.1", "generated_at": generated,
                  "last_modified": generated, "result": {
                      "name": "example-os", "label": "Example OS", "releases": [
                          {"name": release, "isEol": True, "eolFrom": "2026-10-01",
                           "isMaintained": False}]}},
    )
    write_eol_cache(tmp_path / "eol-example-os.json", snapshot)


def test_attaches_matching_release_without_inventing_extended_support(tmp_path):
    write_snapshot(tmp_path)
    evidence, messages = load(tmp_path)
    assert evidence.os_support["A1"].support_status == "unsupported"
    assert evidence.os_support["A1"].extended_support == "unknown"
    assert "Fictional test mapping" in evidence.os_support["A1"].support_basis
    assert any("source fresh" in message for message in messages)


@pytest.mark.parametrize("condition", ["missing", "invalid", "release", "os"])
def test_missing_or_unmatched_evidence_stays_unassessed(tmp_path, condition):
    records = [record()]
    if condition == "invalid":
        (tmp_path / "eol-example-os.json").write_text("invalid")
    elif condition in {"release", "os"}:
        write_snapshot(tmp_path, release="other" if condition == "release" else "1")
        if condition == "os":
            records[0]["mapping"]["os_version"] = "2.0"
    evidence, messages = load(tmp_path, records)
    assert not evidence.os_support
    assert any("unassessed" in message for message in messages)


def test_stale_source_remains_visible(tmp_path):
    write_snapshot(tmp_path, generated=NOW - timedelta(days=9))
    evidence, messages = load(tmp_path)
    assert evidence.os_support["A1"].source_generated_at == NOW - timedelta(days=9)
    assert any("source stale" in message for message in messages)


@pytest.mark.parametrize("records", [
    [record(review_status="draft")], [record(), record()],
    [record(mapping={**record()["mapping"], "product": "../outside"})],
])
def test_rejects_unreviewed_duplicate_or_unsafe_mapping(records):
    with pytest.raises(InputError):
        read_lifecycle_mappings(json.dumps(records).encode())


def test_rejects_orphan_asset(tmp_path):
    with pytest.raises(InputError, match="unknown asset"):
        load(tmp_path, [record(asset_id="ORPHAN")])


def test_does_not_overwrite_existing_evidence(tmp_path):
    write_snapshot(tmp_path)
    evidence, _ = load(tmp_path)
    with pytest.raises(InputError, match="conflicts"):
        load(tmp_path, evidence=evidence)


def test_rejects_oversized_mapping():
    with pytest.raises(InputError, match="size limit"):
        read_lifecycle_mappings(b" " * (64 * 1024 + 1))
