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
- Latest full local suite: 466 tests passed.

## Privacy verification

Eight runtime cases cover successful and rejected CSV, JSON,
Excel, and Nmap inputs. They guard builtins.open and io.open
and check Python logs and captured terminal output during parsing.

This does not yet verify every filesystem API or the complete
assessment path. Future UI and hosting behavior remain unverified.

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