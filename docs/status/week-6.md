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

## Next work

- Arrange a small fictional-data usability pilot using the guide below and
  summarize actual feedback, assistance and failures without inventing results.
- Continue reviewing host retention/log boundaries and other unresolved scope.

## Rejected uploads and reset checks, November 16

The user reported GitHub checks green for e15bd3d. A supplied hosted screenshot
shows saved feeds enabled without the folder text field. The user also confirmed
the revised Start privacy notice. These are bounded UI observations, not a new
host retention audit.

Inventory validation failures now explicitly clear any stored report on both
InputError and generic ValueError/OSError paths. Upload callbacks already
invalidate reports when files are replaced or removed; new tests exercise both.

New coverage includes malformed CSV, JSON, XLSX and authorized Nmap XML;
combined-size rejection; generic errors that do not echo the sentinel input;
replacement/removal callbacks; and a real AppTest restart journey that removes
filenames, optional evidence and reports, returns upload answers to Unknown,
and requires new inventory before proceeding. Template downloads remain
available on Upload; assessment report downloads do not.

Verification: focused upload/UI/limits/privacy run **122 passed**. After adding
two generic-error cases and tightening authorized XML coverage, the upload test
file passed **30 tests**. These sets overlap and must not be added together.
Medium/high Bandit and diff checks passed. The prior 2,570-test full-suite result
predates this change; no new full-suite or hosted malformed-file run is claimed.

UI callback tests use a mocked Streamlit surface; the reset journey uses real
AppTest state. Neither measures browser upload transport, provider logs, memory
erasure or concurrent hosted workers.

## Still unverified

Provider retention/deletion guarantees; complete concurrent-session isolation;
hosted malicious-file exercise; separate clean-machine local Docker run; full
framework mapping validation. No new pilot participants or results are claimed.

## Hosted upload checks reported November 16

The user reported GitHub checks green for afa72b4, then performed these checks
in the public app using supplied fictional test files:

| Check | User-reported observation |
| --- | --- |
| Invalid assets CSV plus valid fictional software CSV | Unsupported-columns error; stayed on Upload; no scores; fictional sentinel not echoed in error |
| Replace invalid assets with valid fictional Lakeview assets | Checklist opened and previous error disappeared |
| Generate with Unknown answers, proceed to Fix First, start a new assessment, choose Upload inventory | Both upload fields empty and no previous results displayed |

These are user-reported UI observations, not independently captured browser
evidence or claims about secure memory erasure, retained uploads, provider logs,
malicious payloads, all formats or concurrent sessions.

## Pilot preparation

Added [pilot testing guide](../pilot-testing-guide.md) and
[blank feedback form](../pilot-feedback-form.md). They define a fictional-only
Lakeview journey, separate wake-up time, the existing five-minute benchmark,
PDF checks, comprehension questions, assistance reporting and private feedback
handling. The owner must choose a private return route before sending the form.
No invitations were sent and no additional pilot sessions or feedback are claimed.
The Week 5 approximately one-minute first-time result remains historical evidence.

This checkpoint changes documentation only. Markdown links and diff checks were
reviewed; no fresh code tests or GitHub workflow results are claimed for it.
