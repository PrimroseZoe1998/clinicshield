"""Run in the built Linux image with --network none; no files are written."""
import csv
import io
import json
import os
from pathlib import Path

import app
from clinicshield.checklist_input import read_checklist
from clinicshield.report_exports import render_checklist_json, render_findings_csv
from clinicshield.report_pdf import render_assessment_pdf


def check_runtime_content(root=Path(".")):
    for excluded in (".git", ".env", ".venv", "tests", "docs", "data/cache", "samples/reports"):
        if (root / excluded).exists():
            raise RuntimeError(f"Unexpected local/development content in runtime image: {excluded}")


def main():
    if os.getuid() != 10001:
        raise RuntimeError("Container must run as the application user.")
    check_runtime_content()
    expected = {"lakeview_dental": 65, "southside_counseling": 82, "westside_health": 80}
    for clinic, score in expected.items():
        report = app.generate_example(clinic, 30, True)
        if report["score"]["final"] != score:
            raise RuntimeError("Sample score mismatch.")
        if not render_assessment_pdf(report).startswith(b"%PDF-"):
            raise RuntimeError("PDF generation failed.")
        rows = list(csv.DictReader(io.StringIO(render_findings_csv(report))))
        if len(rows) != len(report["findings"]):
            raise RuntimeError("CSV export lost findings.")
        saved = render_checklist_json(report)
        restored = read_checklist(saved.encode())
        if restored.answers != json.loads(saved)["answers"]:
            raise RuntimeError("Saved checklist did not round-trip.")
        print(f"{clinic}: {score}; PDF, CSV and checklist JSON passed.")


if __name__ == "__main__":
    main()
