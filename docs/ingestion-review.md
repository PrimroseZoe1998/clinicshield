# Ingestion Acceptance Review

Reviewed October 21, 2026 against the Week 2 ingestion requirements.
This is an implementation review, not Gate 1 approval.

## Implemented

- Typed asset, software, and service schemas.
- In-memory CSV, JSON, and Excel inventory readers.
- Required fields, allowed answers, dates, and port validation.
- Duplicate asset ID rejection and software-to-asset link validation.
- Unmatched services retained and flagged for review.
- Explicit scan-host mapping to existing device asset IDs.
- Nmap XML parsing with authorization confirmation and no scan execution.
- Unknown scan exposure preserved.
- All 25 checklist answers and both Q24 follow-ups validated.
- Conflicting Q24 answers rejected.
- Privacy header checks before aliases, including hidden workbook sheets.
- Explicit header aliases with collision rejection.
- Upload, row, column, cell, and workbook archive limits.
- Safe validation messages without uploaded row values.
- Latest full local suite: 502 tests passed; GitHub checks passed.
- Medical-device presence defaults to Unknown. Q23 is marked
  inapplicable only for an explicit No; Safeguards scoring excludes Q23 from both earned and applicable weight.

## Remaining requirements and review items

- Fuzzy header matching is not implemented. Explicit aliases are used
  to avoid silently selecting the wrong field.
- Hostname remains unsupported because its meaning is ambiguous.
- IP address remains prohibited by the current address blocklist;
  the canonical host field is supported.
- Benjamin accepted explicit aliases without fuzzy matching and
  defusedxml for Nmap parsing at Gate 1 on October 16, 2026.
- 44 runtime privacy cases pass, including 36 complete-assessment
  cases covering all three sample clinics as CSV, JSON, and Excel,
  with and without authorized Nmap input.
  Full-assessment tests guard builtins.open, io.open, os.open,
  os.write, and common tempfile creation functions. They also
  check Python logs and captured terminal output.
  These checks provide bounded evidence for current ingestion;
  future UI, hosting, and operating-system behavior remain unverified.
- Added SECURITY.md and an initial threat model in
  docs/threat-model.md. Deployment checks remain pending.
- Verify upload behavior and friendly errors in the future Streamlit UI.
- Enforced a 20 MiB combined upload limit before assessment parsing,
  retaining per-file limits. Boundary and input-type tests pass.
- Added JSON rejection tests for trailing content, trailing commas,
  comments, unescaped newlines, and excessive nesting.
  Further malformed-file coverage remains under review.
- Added rejection tests for truncated Excel workbooks and ZIP files
  without Excel components.

## Acceptance status

The current Week 2 ingestion implementation meets issue #4's
acceptance criteria within the tested scope.

All three sample clinics load successfully. Tests cover invalid
inputs, safe errors, and runtime privacy across complete assessments.
The latest full suite has 502 passing tests, with GitHub checks green.

Privacy verification provides bounded evidence for the current
ingestion paths, not a guarantee covering every operating-system
mechanism or future deployment.

Header checks do not establish that uploaded values contain
no personal information.

## Deferred verification

- Future Streamlit upload behavior and friendly error presentation.
- Hosted-session isolation, caches, logs, and temporary-file handling.
- Deployment configuration and operating-system data handling.
- Additional regression cases as new input paths are introduced.

Gate 1 decisions are recorded in docs/gate-1-review.md.
Preserve the privacy and no-persistence guardrails.