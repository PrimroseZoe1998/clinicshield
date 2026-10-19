# Ingestion Acceptance Review

Reviewed October 15, 2026 against the project brief.
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
- 342 tests pass locally; merged pull request checks passed.

## Remaining requirements and review items

- Fuzzy header matching is not implemented. Explicit aliases are used
  to avoid silently selecting the wrong field.
- Hostname remains unsupported because its meaning is ambiguous.
- IP address remains prohibited by the current address blocklist;
  the canonical host field is supported.
- Benjamin accepted explicit aliases without fuzzy matching and
  defusedxml for Nmap parsing at Gate 1 on October 16, 2026.
- Runtime tests cover valid and invalid CSV, JSON, Excel, and Nmap
  inputs: no builtins.open or io.open calls, Python log records,
  or captured terminal output occurred during parsing.
  Broader filesystem access and future UI behavior remain unverified.
- Added SECURITY.md and an initial threat model in
  docs/threat-model.md. Deployment checks remain pending.
- Verify upload behavior and friendly errors in the future Streamlit UI.
- Test additional malformed files and combined assessment size limits.

## Acceptance status

Core ingestion is implemented, but full ingestion acceptance remains
pending. Passing tests do not establish that uploaded values contain
no personal information.

Gate 1 decisions are recorded in docs/gate-1-review.md.
Preserve the privacy and no-persistence guardrails.