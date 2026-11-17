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

- Complete the brief's 3–5-person fictional-data pilot; one Week 6 attempt is
  recorded so far. Collect at least two more distinct participants and record
  first-time status, comprehension, assistance and failures.
- Review fresh release-candidate security checks, accessibility and runtime
  evidence; prepare Gate 3 and v1.0-rc after the completion requirements are met.
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
framework mapping validation. Pilot evidence is limited as recorded below.

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
The developer sent no invitations. Subsequent owner-reported results appear below.
The Week 5 approximately one-minute first-time result remains historical evidence.

This checkpoint changes documentation only. Markdown links and diff checks were
reviewed; no fresh code tests or GitHub workflow results are claimed for it.

## Pilot result and original brief review

The user reported checks green for 5188075. They then reported a tester completed
everything in the pilot guide in four minutes, without help, and reported no
confusion or broken/unreadable behavior. Recorded as P01 in [docs/pilot.md](../pilot.md),
with unconfirmed first-time status, environment and direct comprehension answers
left explicit. This is one reported Week 6 attempt; the Week 5 tester is not
silently counted again.

The original project brief specifies 3–5 testers, feedback with changes in
docs/pilot.md, zero High findings from Bandit/pip-audit at Gate 3, a threat model,
SECURITY.md, runtime no-persistence review, accessibility and v1.0-rc. The pilot
report now tracks these requirements. Week 6 remains In Progress; one successful
timed attempt is not full milestone completion. No new defects were reported by
this participant, so no pilot-driven fix is claimed.

This checkpoint changes documentation only; local Markdown links and diff checks
are checked. It adds no fresh code test, audit, release tag or Gate 3 approval.

## Fresh security checkpoint, November 16

See [verification details](../week-6-verification.md): Bandit scanned all severities
with zero High/Medium, eight reviewed Low findings and no scan errors. A direct
audit of all 77 exact pinned requirements returned zero known vulnerabilities
and no skipped packages; installed versions match pins and pip check passed.
The default resolver-backed local audit failed at temporary-environment setup;
the successful fallback and its limits are explicit in the verification note.
No dependency versions, security suppressions or CI audit settings changed.
The fresh full local regression suite passed **2,579 tests**, without exclusions.

The accessibility review distinguishes prior bounded keyboard/label evidence
from unperformed zoom, screen-reader and direct comprehension checks. A manual
pass is prepared; no new human results or Gate 3 acceptance are claimed.

## Hosted zoom check and next requirements

The user subsequently confirmed readability and reachability at 200% browser
zoom on Start, Results and Fix First, with no overlap or clipped text reported.
Normal zoom was restored through the browser menu. See the
[verification note](../week-6-verification.md) for coverage and evidence limits.
No app defect or code change resulted from this check. This updates the earlier
pending-zoom status, without claiming a full accessibility audit.

Current completion work remains:

- At least two further distinct Week 6 pilot testers (three minimum in the brief).
- Direct comprehension feedback and review of any defects, with retests if needed.
- Final release-scope security/runtime review and Gate 3 discussion with Benjamin.
- v1.0-rc tag after required checks and disposition, not before.

This update records user-reported evidence only. No fresh code tests or hosted
privacy guarantees are claimed. Week 6 remains In Progress.
