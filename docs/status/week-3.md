# Week 3 status

## October 30, 2026 brief-based audit

Done: compared the original Week 3 table with the implementation; added
`../rules.md`; rechecked three fictional scenarios (65/82/80); 162 focused tests
passed using a writable pytest scratch directory. Unknown versions remained
review items; no synthetic scenario invented a CVE match.

CVSS follow-up: source-attributed CVSS 3.1 base-score context is implemented
with explicit unsupported/malformed-data warnings; see ../cvss-context.md.
Other versions and score recalculation remain outside this bounded step.

Cache follow-up: app and workflow now default to data/cache/; the verified
artifact is installed locally. Future artifact synchronization is still manual;
see ../local-feed-cache.md.

Healthcare reference follow-up: all 24 rules now carry partial HICP/HIPAA
relationships; 18 carry partial/conditional HHS CPG relationships. Six HHS
omissions are documented rather than forced. See ../healthcare-rule-review.md.

Manual checks on October 30: screenshots show fresh KEV/EPSS, NVD 1/1 and
CVSS source context. The user confirmed CVSS in the downloaded TXT report and
healthcare references in the R16 preview and download. These are scoped manual
checks, not independent validation of the mappings. The garbled UI separators
were then replaced with ASCII; syntax and 28 focused tests passed.
Latest broad verification: 2,468 tests passed excluding the known stalled local
Streamlit AppTest file; the high-severity Bandit check passed at the CVSS step.

Next: review remaining delivery/scope differences and keep full rule approval
and scheduled execution as unverified. See
`../week-3-acceptance-review.md` for the requirement-by-requirement assessment.

Blocked/limits: scheduled execution unobserved; rule definitions remain draft.
No new CI run or independent stakeholder approval was verified in this audit.

Scope correction: scoring/Fix First belong to Week 4; the Streamlit app and
results sub-scores belong to Week 5. These are not Week 3 blockers. Core engine
checks pass, but full original-brief conformance is not yet claimed.

The October 29 and October 26 checkpoints below are historical records; their
pending scope-confirmation statements are superseded by this brief-based audit.

## October 29, 2026 checkpoint

- All 24 draft rules are registered.
- Saved KEV/EPSS and reviewed lifecycle/applicability evidence are connected.
- CSV, JSON and XLSX upload paths are implemented and manually tested with fictional files.
- Latest pushed checkpoint `71d762b` passed GitHub checks, as reported by the user.
- Benjamin accepted retaining the model and revising sample expectations, as reported
  by the user. See `../benjamin-decisions-2026-10-29.md`.
- Refresh reporting saves optional per-run JSON and renders an Actions summary.
  [Manual refresh run #3](https://github.com/PrimroseZoe1998/clinicshield/actions/runs/40949949834)
  succeeded on `6099acb`. The supplied screenshot shows success for KEV, EPSS,
  Python and Windows lifecycle feeds. The user confirmed all six artifact files:
  `refresh-status.json`, `refresh.log`, `kev.json`, `epss.json`, `eol-python.json`
  and `eol-windows.json`. Artifact contents were confirmed by the user, not
  independently downloaded by the agent.
- Local verification: 2,429 tests passed with the known stalled Streamlit AppTest
  file excluded. The CI-equivalent high-severity Bandit check passed; no medium
  or high findings were reported. Native UI automation remains unverified locally.

- R16 framework labels, limits and URLs were checked in the browser screenshot
  and user-confirmed readable download.

Acceptance status: **pending milestone scope confirmation and final review**. See `../week-3-acceptance-review.md`.

Remaining:

- All 24 rules now have source-checked partial CSF 2.0 mappings; 22 also have
  source-checked partial/conditional CIS v8.1 mappings. See `../rule-framework-review.md`.
  Rule definitions remain draft. Additional HICP/HHS/HIPAA rule crosswalks and
  independent stakeholder review are not implied by this source check.
- Scheduled execution remains unobserved; artifacts provide 30-day per-run history,
  not an indefinite aggregated failure ledger.
- Actual clinic controls, application support and administrator observations still
  need source evidence; upload success does not verify them.
- Full source coverage/NVD range ingestion and completed rule review are not claimed.
- Fix First priority, conservative tie-breakers, four action groups and exact
  repeated-action-set handling are implemented and tested. The user confirmed
  Lakeview priorities 4.5 and 3, single R03/R08 grouping, and the matching download
  with a separate verification section; see `../fix-first-plan.md`.
- Limited-CVE NVD caching and conservative reviewed exact-CPE adaptation are now
  implemented. The initial one-record public download/cache/offline check passed;
  the screenshot and user-confirmed download verify availability/no-mapping behavior.
  The user confirmed successful NVD refresh run `40963762712`, its NVD status row
  and the CVE JSON artifact. The unsupported mapping-upload preview/download
  path was then verified with synthetic inventory: needs_review and unchanged
  displayed scores; the download preserves the explanation and fixture notice.
  See `../nvd-cache-implementation.md`.

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

## Historical limits as of October 26

- Scheduled execution has not yet been observed.
- Lifecycle refresh currently selects Python only.
- Workflow artifacts are not yet connected to assessment ingestion.
- Exact-version matching does not interpret version ranges.
- Feed retrieval age does not establish source completeness.
- Refresh failures are reported in run logs; a persistent failure
  history is not yet implemented.

## Historical remaining work as of October 26

- Define NVD CVE scope and caching strategy.
- Connect cached intelligence to assessments and findings.
- Report unmatched versions and stale or missing coverage.
- Expand lifecycle product coverage using explicit mappings.
- Implement and test the 24 YAML starter rules.
- Add evidence, severity, fix, owner, effort, cost, and reviewed
  framework references to each rule.
- Combine duplicate evidence without losing distinct risks.
