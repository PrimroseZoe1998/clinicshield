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

## Cache and privacy hardening implemented November 16

- Removed the browser's server cache-folder text field. The guided UI now reads
  only `<repository>/data/cache` when saved feeds are enabled, including during
  assessment generation with a stale session path. Operator-facing Python APIs
  retain their explicit directory arguments for local tools and tests. Server
  administrators remain responsible for the configured directory and its files.
- Replaced the absolute no-disk/session-only privacy promise with bounded app
  behavior, unverified host storage/log handling and a reminder that downloads
  save a copy on the user's device. Fictional data only is explicit.
- UI/wording checks: 14 passed, including all three fictional scenario scores,
  navigation/reset behavior and stale-path rejection at the evaluation boundary.
  The revised notice screens at estimated grade 6.5 under the project's local
  heuristic; this is not an accessibility certification.
- Full local regression suite: **2,570 passed**, without exclusions. Bandit at
  medium/high severity and `git diff --check` passed. Hosted deployment and fresh
  GitHub checks remain pending until this commit is pushed.

No exploit or arbitrary-file disclosure was established. This removes unnecessary
browser control of server resource locations. No scoring formula or dependency
pins changed. Existing committed demonstration reports remain historical samples.

## Next hardening work

- Extend checks through guided upload changes, reset/error paths and optional
  evidence, with explicit separation from host behavior.
- Prepare a pilot guide and feedback form after documenting those boundaries.

## Still unverified

Provider retention/deletion guarantees; complete concurrent-session isolation;
hosted malicious-file exercise; separate clean-machine local Docker run; full
framework mapping validation. No new pilot participants or results are claimed.
