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
- 334 tests pass locally; merged pull request checks passed.

## Remaining requirements and review items

- Fuzzy header matching is not implemented. Explicit aliases are used
  to avoid silently selecting the wrong field.
- Hostname remains unsupported because its meaning is ambiguous.
- IP address remains prohibited by the current address blocklist;
  the canonical host field is supported.
- The Nmap reader uses defusedxml rather than python-libnmap.
  Record this implementation choice at Gate 1.
- Add documented runtime verification that uploaded content is neither
  written to disk nor logged.
- Complete the threat model and SECURITY.md.
- Verify upload behavior and friendly errors in the future Streamlit UI.
- Test additional malformed files and combined assessment size limits.

## Acceptance status

Core ingestion is implemented, but full ingestion acceptance remains
pending. Passing tests do not establish that uploaded values contain
no personal information.

Record decisions on header matching and implementation variations
at Gate 1. Preserve the privacy and no-persistence guardrails.