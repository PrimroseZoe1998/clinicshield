# ClinicShield Week 3 — review requested October 28, 2026

Historical record. For the October 29 sample-scoring decision and current scope,
see `benjamin-decisions-2026-10-29.md` and `scoring-calibration.md`.

## Verified progress

- 1,623 local tests passing; GitHub checks green.
- KEV, EPSS, and Python lifecycle downloads/cache round trips verified.
- Weekly refresh workflow manually verified, including artifacts.
- 18 draft rules connected to typed evaluation functions.
- NVD scope and caching strategy documented; downloader not implemented.

## Decisions requested

### 1. Reconstructed rule assignments

Please review these proposed assignments:
- R01: Confirmed applicable CVE listed in KEV.
- R02: Other confirmed applicable CVE; EPSS informs priority.
- R04: Unsupported application release.
- R06: Internet-exposed remote administration.
- R13: Clinical-system MFA gap.
- R15: Antivirus protection gap.
- R21: Security reporting or notification preparation gap.
- R23: Staff security training gap.

Sources and existing rule meanings: docs/rule-catalog.md.

### 2. Severity and scoring

- All implemented rule severities and effort estimates remain drafts.
- Unknown evidence generally produces an Info review finding.
- R03 currently assigns High to confirmed unsupported OS findings.
  Sample score expectations mention Critical findings; please confirm
  which rules and circumstances should be Critical.
- Review technical versus checklist classification for inventory-based
  MFA and agreement findings, including potential scoring overlap.
- Final sample score calibration remains incomplete.

### 3. Evidence and overlap

- R10 default-password evidence may overlap R19 router safeguards.
- R06 exposure, R07 remote-access safeguards, and R09 Telnet describe
  distinct risks; shared remediation must not erase their evidence.
- R12/Q01 and R13/Q07 evidence grouping remains unfinished.
- R20 uses Q20 and Q24a; R22 independently uses Q24b.

### 4. Lifecycle coverage

- Exact product/release mappings are required.
- Stale, missing, mismatched, or unresolved extended-support evidence
  requires review.
- R03 is tested with fictional evidence; real-cache integration is pending.
- Lifecycle refresh currently selects Python only.
- Confirm initial OS/application coverage and eight-day freshness policy.

### 5. NVD scope

Please review docs/nvd-caching.md:
- Reviewed allowlist, initially capped at 50 CVEs.
- Weekly public-data refresh; offline assessment use.
- No claim of comprehensive vulnerability coverage.

## Remaining implementation

- Six rules: R01, R02, R04, R08, R10, R11.
- Real lifecycle-cache adapters and vulnerability applicability.
- Evidence grouping, assessment orchestration, and scoring integration.
- Rule-specific framework review and final sample calibration.

A reviewed rule definition is separate from verification of a clinic's
actual controls. Draft mappings do not establish compliance.