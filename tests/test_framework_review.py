from pathlib import Path

import pytest

from app import generate_example
from clinicshield.report_text import render_assessment_text
from clinicshield.rule_catalog import load_rule_catalog


ROOT = Path(__file__).resolve().parents[1]


def test_reference_review_does_not_upgrade_draft_rules_or_claim_complete_coverage():
    rules = load_rule_catalog(ROOT / "rules")
    for rule in rules:
        assert rule.review_status == "draft"
        assert any(ref.framework == "NIST CSF 2.0" for ref in rule.framework_references)
        for ref in rule.framework_references:
            assert ref.review_status == "reviewed"
            assert "partial" in ref.reference.lower()
            sources = {
                "NIST CSF 2.0": ("October 29", "https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf"),
                "CIS Controls v8.1": ("October 29", "https://www.cisecurity.org/controls/CIS-controls-navigator"),
                "HICP 2023": ("October 30", "https://hhscyber.hhs.gov/Documents/HICP/tech-vol"),
                "HHS Healthcare CPG": ("October 30", "https://hhscyber.hhs.gov/cybersecurity-performance-goals.html"),
                "HIPAA Security Rule": ("October 30", "https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164."),
            }
            date, prefix = sources[ref.framework]
            assert f"source checked {date}, 2026" in ref.rationale
            assert ref.source.startswith(prefix)


@pytest.mark.parametrize("clinic,score", [
    ("lakeview_dental", 65), ("southside_counseling", 82), ("westside_health", 80),
])
def test_reference_changes_preserve_scenario_scores_and_provisional_status(clinic, score):
    report = generate_example(clinic, 30, True)
    assert report["score"]["final"] == score
    assert report["score"]["status"] == "provisional"
    assert "Some applied rule definitions remain drafts." in report["score"]["limitations"]
    text = render_assessment_text(report)
    assert "Source-checked project mapping:" in text
    assert "Mapping scope: Partial project mapping" in text


def test_conditional_and_agreement_mapping_limits_survive_download():
    text = render_assessment_text(generate_example("southside_counseling", 30, True))
    assert "externally exposed applications where supported" in text
    assert "do not establish BAA applicability" in text


def test_healthcare_mapping_omissions_do_not_invent_cpg_coverage():
    rules = {rule.rule_id: rule for rule in load_rule_catalog(ROOT / "rules")}
    # Stored-data encryption and lifecycle support are not automatically the
    # in-motion encryption / Internet-accessible known-vulnerability goals.
    for identifier in ("R03", "R04", "R05", "R06", "R08", "R22"):
        assert not any(ref.framework == "HHS Healthcare CPG"
                       for ref in rules[identifier].framework_references)
    for rule in rules.values():
        assert {"HICP 2023", "HIPAA Security Rule"} <= {
            ref.framework for ref in rule.framework_references}


def test_conditional_mfa_and_legal_limits_survive_download():
    text = render_assessment_text(generate_example("lakeview_dental", 30, True))
    assert "HIPAA Security Rule" in text
    assert "HICP 2023" in text
    assert "HHS Healthcare CPG" in text
    assert "Internet-accessible accounts where safe and technically capable" in text
    assert "Encryption/decryption is Addressable" in text
    assert "not a compliance finding" in text
    assert "daily frequency and a six-month" in text.lower()


def test_reporting_mapping_does_not_determine_notification_duties():
    rule = next(r for r in load_rule_catalog(ROOT / "rules") if r.rule_id == "R21")
    reference = next(r for r in rule.framework_references if r.framework == "HIPAA Security Rule")
    assert "164.308(a)(6)(ii)" in reference.reference
    assert "Q22 requires separate breach/notification evaluation" in reference.rationale
    assert "No breach, legal notification duty, recipient or deadline" in reference.rationale
