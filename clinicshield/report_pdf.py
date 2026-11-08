from clinicshield.reader_guidance import SCORE_GUIDE, SCOPE_NOTICE, PRIORITY_GUIDE
"""Create owner-summary and full-detail PDF reports entirely in memory."""
from pathlib import Path
import re

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from clinicshield.report_text import render_assessment_text

FONT_DIR = Path(__file__).resolve().parent / "fonts"


class AssessmentPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Vera", "B", 9)
            self.set_text_color(35, 65, 80)
            self.cell(0, 7, "ClinicShield | Detailed assessment", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(2)

    def footer(self):
        self.set_y(-14)
        self.set_font("Vera", "", 7)
        self.set_text_color(85, 95, 105)
        self.cell(0, 4, f"ClinicShield | Lead developer: Primrose Mangwendeza | Page {self.page_no()} of {{nb}}",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 4, "Prototype assessment - not proof of compliance or security effectiveness", align="C")


def _text(pdf, value):
    text = str(value).replace("\r", " ").replace("\t", "    ")
    text = text.translate(str.maketrans({"—": "-", "–": "-", "‑": "-"}))
    # Preserve unsupported characters explicitly rather than silently dropping them.
    cmap = pdf.current_font.cmap
    return "".join(c if c == "\n" or ord(c) in cmap else f"[U+{ord(c):04X}]" for c in text)


def _paragraph(pdf, text, *, bold=False, size=9, height=4.5):
    pdf.set_font("Vera", "B" if bold else "", size)
    pdf.set_text_color(25, 38, 48)
    pdf.multi_cell(0, height, _text(pdf, text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def _short(value, limit):
    value = " ".join(str(value).split())
    return value if len(value) <= limit else value[:limit - 3] + "..."


def render_assessment_pdf(report: dict) -> bytes:
    """One bounded owner-summary page followed by the complete readable report.

    Long summary labels are shortened; full evidence/actions remain in the appendix.
    Unsupported font glyphs are represented as explicit Unicode code points.
    """
    pdf = AssessmentPDF(format="A4")
    pdf.set_margins(17, 15, 17)
    pdf.set_auto_page_break(True, margin=20)
    pdf.add_font("Vera", fname=FONT_DIR / "Vera.ttf")
    pdf.add_font("Vera", "B", fname=FONT_DIR / "VeraBd.ttf")
    pdf.alias_nb_pages()
    pdf.set_title("ClinicShield assessment")
    pdf.set_author("ClinicShield")
    pdf.add_page()
    _paragraph(pdf, "ClinicShield", bold=True, size=24, height=12)
    _paragraph(pdf, "Owner summary", bold=True, size=14, height=9)
    _paragraph(pdf, f"Assessment time: {report['evaluated_at']}", size=8)
    example = report.get("example_context")
    if example:
        _paragraph(pdf, "Fictional example: " + _short(example['clinic'], 65), bold=True)
        _paragraph(pdf, "Evidence mode: " + _short(example['evidence_mode'], 100))
        _paragraph(pdf, "Demo only. These changes are made-up assumptions. They are not completed corrective actions or verified improvement.")
    else:
        _paragraph(pdf, "Supplied assessment: inventory and answers have not been independently verified.")
    pdf.ln(4)
    score = report["score"]
    _paragraph(pdf, f"{score['final']}/100 | {_short(score['band'], 45)}", bold=True, size=20, height=11)
    _paragraph(pdf, f"Safeguards {score['safeguards']:.1f}/100 | Exposure {score['exposure']:.1f}/100")
    _paragraph(pdf, "Weighting: 60% Safeguards + 40% Exposure. Status: " + score['status'].replace('_', ' '))
    _paragraph(pdf, SCORE_GUIDE, size=8)
    if score.get('critical_ceiling') is not None:
        _paragraph(pdf, f"Confirmed Critical finding: overall score capped at {score['critical_ceiling']}.", bold=True)
    pdf.ln(4)
    _paragraph(pdf, "Read the score with its limits", bold=True, size=11, height=7)
    _paragraph(pdf, f"{len(report['coverage_issues'])} coverage issues | {sum(f['status'] != 'confirmed_from_supplied_evidence' for f in report['findings'])} finding groups need review.")
    _paragraph(pdf, SCOPE_NOTICE)
    for item in score['limitations'][:3]:
        _paragraph(pdf, "- " + _short(item, 150))
    pdf.ln(4)
    _paragraph(pdf, "Fix First: highest-ranked actions", bold=True, size=11, height=7)
    _paragraph(pdf, PRIORITY_GUIDE)
    actions = report.get('fix_first', {}).get('actions', [])
    for action in actions[:3]:
        _paragraph(pdf, f"#{action['rank']} | " + _short(', '.join(action['rule_ids']) + ' | ' + action['entity_id'], 85), bold=True)
        _paragraph(pdf, _short('; '.join(action['recommendations']), 150))
        _paragraph(pdf, "Owner: " + _short(', '.join(action['owners']), 65) + f" | Effort: {action['effort']}/3 | Cost: " + _short(', '.join(action['costs']), 35), size=8)
        pdf.ln(1)
    if not actions:
        _paragraph(pdf, "No confirmed actions within the supplied scope. Review missing evidence before concluding that no work is needed.")
    pdf.ln(3)
    _paragraph(pdf, "Next: agree owners, confirm evidence and request provider estimates. The appendix contains all actions, evidence, score arithmetic and coverage warnings. Summary labels may be shortened.", size=8)
    if pdf.page_no() != 1:
        raise ValueError("Owner summary exceeded one page.")
    pdf.add_page()
    _paragraph(pdf, "Detailed appendix", bold=True, size=17, height=10)
    _paragraph(pdf, "Full report including findings requiring verification. Unsupported glyphs are shown as [U+code].", size=8)
    pdf.ln(3)
    headings = {"Why this score", "Practice-area results (draft)", "What this score covers",
                "Evidence age policy", "Coverage requiring attention", "Answers that need reconciliation",
                "Fix First plan", "Verify before planning remediation", "Findings from supplied evidence",
                "Items requiring verification", "How to read this report", "Word guide"}
    for line in render_assessment_text(report).splitlines():
        if not line.strip():
            pdf.ln(2)
            continue
        heading = line in headings or bool(re.match(r"^\d+\. ", line))
        if heading:
            if pdf.will_page_break(30 if line in headings else 22):
                pdf.add_page()
            pdf.ln(2)
        _paragraph(pdf, line, bold=heading, size=10 if heading else 8.5,
                   height=5.2 if heading else 4.2)
    return bytes(pdf.output())
