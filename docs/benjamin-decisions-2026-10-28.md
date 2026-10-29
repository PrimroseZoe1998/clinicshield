# Benjamin review decisions

Historical record. For the October 29 sample-scoring decision and current scope,
see `benjamin-decisions-2026-10-29.md` and `scoring-calibration.md`.

Received October 28, 2026 by email.

## Confirmed decisions

- Proceed with proposed assignments R01, R02, R04, R06,
  R13, R15, R21, and R23.
- Require clear triggers and supporting evidence for each rule.
- Retain Critical for confirmed applicable KEV vulnerabilities.
- Use High for confirmed unsupported operating systems.
- Escalate unsupported OS findings only when additional documented
  exposure or exploitation conditions justify Critical.
- Treat unknown evidence as informational review items,
  not confirmed risk.

## Evidence and scoring requirements

- Require explicit evidence before confirming vulnerabilities,
  missing MFA, unsupported software, or network isolation.
- Missing information must trigger review rather than assumptions.
- Preserve distinct findings and evidence sources.
- Prevent overlapping remediation issues from inflating Exposure
  or Safeguards scores.
- Clearly distinguish technical vulnerabilities from administrative
  safeguards.

## Freshness and coverage

- Adopt eight days provisionally for public intelligence feeds.
- Track administrator observations separately.
- Display observation/data age, source coverage, and refresh failures.
- Proceed with limited-CVE NVD caching.
- State coverage limitations without claiming comprehensive detection.

## Framework references

Validate rule-specific NIST, CIS, and other relevant mappings before
presenting them as verified references. Approval of rule assignments
does not approve every framework mapping or implementation detail.

## Implementation priorities

1. Complete assessment integration.
2. Implement evidence deduplication and prevent score inflation.
3. Calibrate scores against documented assessment scenarios.
4. Clearly report unresolved findings.
5. Keep recommendations understandable and actionable for smaller
   healthcare organizations without dedicated cybersecurity teams.

## Requested follow-up deliverable

Provide an updated assessment example showing:
- Findings and severity.
- Supporting evidence and unresolved information.
- Recommendations.
- Overall scoring and its explanation.

## Current checkpoint

- 2,092 tests passing; latest GitHub checks green.
- All 24 draft rule handlers registered.
- EPSS lookup implementation saved; its tests are next.
- Full assessment integration and score calibration remain incomplete.