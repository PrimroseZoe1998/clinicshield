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
            assert "source checked October 29, 2026" in ref.rationale
            assert ref.source.startswith((
                "https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf",
                "https://www.cisecurity.org/controls/CIS-controls-navigator",
            ))


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
