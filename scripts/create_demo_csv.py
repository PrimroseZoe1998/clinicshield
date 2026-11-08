"""Generate only the three fictional scenario CSV deliverables, offline."""
import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import app
from clinicshield.report_exports import render_findings_csv


def main():
    target = ROOT / "samples" / "reports"
    target.mkdir(parents=True, exist_ok=True)
    for clinic, expected in (("lakeview_dental",65),("southside_counseling",82),("westside_health",80)):
        report = app.generate_example(clinic,30,True)
        if report["score"]["final"] != expected:
            raise RuntimeError("Unexpected fictional fixture score.")
        data = render_findings_csv(report)
        if len(list(csv.DictReader(io.StringIO(data)))) != len(report["findings"]):
            raise RuntimeError("CSV lost findings.")
        (target / f"{clinic}-findings.csv").write_text(data, encoding="utf-8", newline="")
        print(f"{clinic}: {expected}; {len(report['findings'])} finding groups")


if __name__ == "__main__":
    main()
