# Week 2 Status

Progress as of October 20, 2026.

## Done

- Implemented typed inventory models and checklist validation.
- Added in-memory CSV, JSON, XLSX, and authorized Nmap XML readers.
- Enforced per-file and combined assessment upload limits.
- Validated fields, dates, allowed values, and inventory links.
- Checked prohibited headers, including hidden workbook sheets.
- Implemented approved header aliases with ambiguity rejection.
- Preserved Unknown and NA values during ingestion.
- Added safe validation errors and malformed-input tests.
- Added SECURITY.md and an initial threat model.
- Latest full local suite: 502 tests passed.

## Privacy verification

44 runtime privacy cases pass, including 36 complete-assessment
cases covering all three sample clinics as CSV, JSON, and Excel,
both with and without authorized Nmap input.

Complete-assessment tests cover successful ingestion and invalid
checklist rejection after inventory and scan parsing. They guard
builtins.open, io.open, os.open, os.write, and common tempfile
creation functions. They also check Python logs and captured
terminal output.

These checks provide bounded evidence for the current ingestion code.
Future UI, hosting, and operating-system behavior remain unverified.

## Additional progress

Implemented scoring arithmetic, Q23 applicability, scoring-entity
mappings, and technical finding evaluation. Automatic finding
generation and complete assessment orchestration remain pending.

## Remaining before issue #4 closes

- Complete and document the remaining ingestion privacy verification.
- Review evidence against the issue's acceptance criteria.
- Confirm final changes pass local tests and GitHub checks.

## Deferred checks

Future Streamlit upload behavior, session isolation, and hosting
configuration require verification when those components exist.