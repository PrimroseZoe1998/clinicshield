# Week 6: hardening and pilot preparation

Status: In Progress. Started November 16, 2026.

## Starting point

The user confirmed Week 5 issue #7 was closed on November 11. The user
interprets Benjamin's reply, "you are looking great my friend keep going!",
as acceptance of the prototype checkpoint. This records that interpretation,
not an explicit item-by-item validation. Existing framework-review, hosted
storage/log, reading-level and local-Docker limitations remain applicable.
Week 3's unfinished framework-reference review remains open separately.

## First upload and data-handling review

Inspected the inventory readers, combined input limits, guided session helpers,
upload callbacks, assessment entry point, privacy notice and hosted-runtime notes.

Focused verification on November 16:

`python -m pytest tests/test_input_limits.py tests/test_runtime_privacy.py tests/test_privacy.py tests/test_assessment_input.py tests/test_app_uploads.py tests/test_guided_assessment.py -q`

Result: **141 passed**. This is a local focused run, not a fresh full-suite,
hosted penetration test, dependency audit or independent privacy certification.

Existing controls include per-file and combined byte limits, workbook expansion
limits, safe validation errors, authorized existing-scan parsing, guarded
in-memory ingestion, and report invalidation when guided inputs change.

## Next hardening work

- Restrict public UI cache reads to a server-configured public-feed directory.
  The current text field accepts a server filesystem path; uploaded data should
  not choose server resource locations. No arbitrary-file disclosure is claimed
  by this review; loaders and their response behavior need focused inspection.
- Narrow the user-facing privacy promise. The notice currently says inputs stay
  in the session and are not saved to disk. Parser tests support bounded
  application behavior, but do not establish provider storage, logs or temporary
  file handling. Preserve the fictional-data-only pilot boundary.
- Extend checks through guided upload changes, reset/error paths and optional
  evidence, with explicit separation from host behavior.
- Prepare a pilot guide and feedback form after documenting those boundaries.

## Still unverified

Provider retention/deletion guarantees; complete concurrent-session isolation;
hosted malicious-file exercise; separate clean-machine local Docker run; full
framework mapping validation. No new pilot participants or results are claimed.
