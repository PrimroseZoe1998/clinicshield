from copy import deepcopy
import pytest
import app
from clinicshield import report_pdf
from clinicshield.report_text import render_assessment_text


@pytest.mark.parametrize("clinic", list(app.CLINICS.values()))
def test_pdf_summary_and_complete_appendix(clinic, monkeypatch):
    report = app.generate_example(clinic, 30, True)
    original = deepcopy(report)
    rendered = []
    paragraph = report_pdf._paragraph
    def capture(pdf, text, **kwargs):
        rendered.append((pdf.page_no(), str(text)))
        return paragraph(pdf, text, **kwargs)
    monkeypatch.setattr(report_pdf, "_paragraph", capture)
    data = report_pdf.render_assessment_pdf(report)
    assert data.startswith(b"%PDF-") and data.rstrip().endswith(b"%%EOF")
    assert report == original
    assert (1, "Owner summary") in rendered
    assert (2, "Detailed appendix") in rendered
    assert any(page == 1 and f"{report['score']['final']}/100" in text for page, text in rendered)
    appendix = [text for page, text in rendered if page >= 2]
    expected = [line for line in render_assessment_text(report).splitlines() if line.strip()]
    assert appendix[2:] == expected
    assert any(page == 1 and "not completed corrective actions" in text for page, text in rendered)


def test_empty_actions_and_long_labels_still_have_one_summary_page(monkeypatch):
    report = app.generate_example("lakeview_dental", 30)
    report["fix_first"]["actions"] = []
    report["example_context"]["clinic"] = "Very long name " * 500
    data = report_pdf.render_assessment_pdf(report)
    assert data.startswith(b"%PDF-")


def test_unicode_and_long_evidence_export_without_mutation():
    report = app.generate_example("lakeview_dental", 30)
    report["findings"][0]["evidence"][0]["details"]["unicode"] = "café 中文 😀 " + "A" * 12000
    data = report_pdf.render_assessment_pdf(report)
    assert data.startswith(b"%PDF-")


def test_pdf_generation_never_writes_assessment_files(monkeypatch):
    from pathlib import Path
    report = app.generate_example("lakeview_dental", 30)
    def forbidden(*args, **kwargs):
        pytest.fail("PDF must not persist assessment data")
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)
    report_pdf.render_assessment_pdf(report)
