# Week 3 status

## October 29, 2026 checkpoint

- All 24 draft rules are registered.
- Saved KEV/EPSS and reviewed lifecycle/applicability evidence are connected.
- CSV, JSON and XLSX upload paths are implemented and manually tested with fictional files.
- Latest pushed checkpoint `85d0998` passed GitHub checks, as reported by the user.
- Benjamin accepted retaining the model and revising sample expectations, as reported
  by the user. See `../benjamin-decisions-2026-10-29.md`.
- Refresh reporting now saves optional per-run JSON and renders an Actions summary.
  Local failure-path checks passed; the revised workflow has not run on GitHub yet.
- Local verification: 2,354 tests passed with the known stalled Streamlit AppTest
  file excluded. The CI-equivalent high-severity Bandit check passed; no medium
  or high findings were reported. Native UI automation remains unverified locally.

Remaining:

- 24 of 24 rule-specific framework references remain pending source validation.
- Confirm the revised refresh workflow and artifacts in GitHub Actions.
- Scheduled execution remains unobserved; artifacts provide 30-day per-run history,
  not an indefinite aggregated failure ledger.
- Actual clinic controls, application support and administrator observations still
  need source evidence; upload success does not verify them.
- Full source coverage/NVD range ingestion and completed rule review are not claimed.

The older checkpoint below is retained as history.

## Verified on October 26, 2026

- 975 automated tests passing.
- GitHub tests and security checks passing.
- Conservative vendor/product normalization and exact-version matching.
- Unsupported version rules require review.
- Feed freshness checks and explicit cache error reporting.
- Validated downloads and atomic cache storage for:
  - CISA KEV
  - FIRST EPSS
  - endoflife.date API v1, verified with Python
- Combined refresh command with independent feed failure handling.
- Weekly GitHub Actions workflow configured.
- Manual workflow run succeeded:
  https://github.com/PrimroseZoe1998/clinicshield/actions/runs/40398969980
- Downloaded artifact contains kev.json, epss.json,
  eol-python.json, and refresh.log.

## Current limits

- Scheduled execution has not yet been observed.
- Lifecycle refresh currently selects Python only.
- Workflow artifacts are not yet connected to assessment ingestion.
- Exact-version matching does not interpret version ranges.
- Feed retrieval age does not establish source completeness.
- Refresh failures are reported in run logs; a persistent failure
  history is not yet implemented.

## Remaining work

- Define NVD CVE scope and caching strategy.
- Connect cached intelligence to assessments and findings.
- Report unmatched versions and stale or missing coverage.
- Expand lifecycle product coverage using explicit mappings.
- Implement and test the 24 YAML starter rules.
- Add evidence, severity, fix, owner, effort, cost, and reviewed
  framework references to each rule.
- Combine duplicate evidence without losing distinct risks.
