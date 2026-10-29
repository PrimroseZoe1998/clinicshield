# ClinicShield

Cyber Safety Checkup for Small Health Providers

ClinicShield is a free, open-source prototype that helps small
healthcare providers review their cybersecurity practices.

It uses device/software inventories and a security checklist to produce an
explained provisional Cyber Safety Score and evidence-based findings.
A ranked Fix First plan groups confirmed actions and separates verification items.
See [ranking scope and limits](docs/fix-first-plan.md).

## Project status

The prototype includes 24 draft rules, fictional example assessments,
CSV/JSON/XLSX uploads, grouped scoring and readable report downloads.
Saved public feeds and reviewed lifecycle/CVE applicability evidence can be
loaded offline. Missing coverage and unresolved information remain visible.

The latest pushed checkpoint is `8771794`, with green GitHub checks reported
by the developer. Current local verification passed 2,429 tests excluding a known
Streamlit AppTest socket-pair stall. Manual checks cover the documented paths.

Week 3 remains incomplete: Fix First is implemented and manually checked with fictional data,
and limited-CVE NVD caching is implemented with availability browser checks complete;
the revised refresh workflow still needs verification. See the [acceptance audit](docs/week-3-acceptance-review.md)
and [Week 3 status](docs/status/week-3.md).

## Run locally

Use Python 3.13 and install the pinned dependencies in a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Start with **Fictional example**, or choose **Upload inventory** for separate
CSV/JSON inventories or an Excel workbook. Checklist/follow-up JSON answers
are required for uploads. See the [upload guide](docs/inventory-upload-assessments.md)
for formats, limits and checks. Example data in `samples/` is fictional;
uploaded inputs have not been independently verified by ClinicShield.

## Evidence and refreshes

Refresh public data separately from assessment generation. The weekly/manual
GitHub Actions workflow produces a ZIP with snapshots, a log and per-feed status.
Extract it into a local folder to load in the app. Assessment generation does not
download workflow artifacts or infer CVE applicability from KEV/EPSS alone.

The bounded NVD refresh uses a reviewed repository allowlist and preserves full
source records. Assessments require reviewed software mappings and support only
a narrow exact-configuration subset; complex logic remains for review. See the
[NVD implementation guide](docs/nvd-cache-implementation.md).

See [evidence inputs](docs/reviewed-assessment-evidence.md),
[mapping scope](docs/rule-framework-review.md) and
[refresh reporting](docs/refresh-failure-reporting.md).

## Safety requirements

- Do not upload patient information.
- Uploaded data will be processed in memory without being saved.
- The application will never initiate network scans.
- Results will not certify HIPAA compliance or replace a formal
  security risk analysis.
- The tool does not provide legal advice.

## Credits

Developed for Chicago Education Advocacy Cooperative (ChiEAC).

Lead developer: Primrose Mangwendeza.
