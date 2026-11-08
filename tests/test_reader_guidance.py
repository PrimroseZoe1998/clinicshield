from pathlib import Path
import app
from clinicshield.reader_guidance import glossary_lines
from clinicshield.report_text import render_assessment_text
from scripts.readability_review import review


def test_selected_owner_prose_stays_within_local_screening_target():
    rows=review()
    assert len(rows)==56
    assert all(row["estimated_grade"]<=8 for row in rows)


def test_download_report_defines_terms_before_detailed_findings():
    report=app.generate_example("lakeview_dental",30,True)
    text=render_assessment_text(report)
    assert text.index("Word guide") < text.index("Why this score")
    assert "Known Exploited Vulnerabilities" in text
    assert "Exploit Prediction Scoring System" in text
    assert "Business Associate Agreement" in text
    assert "Provisional means" in text
    assert "does not prove" in text
