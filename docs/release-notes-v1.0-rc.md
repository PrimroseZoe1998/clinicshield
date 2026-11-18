# ClinicShield v1.0-rc â€” draft release notes

**Unreleased.** Prepared November 16, 2026. Tag, release date, final SHA and Gate 3
disposition are pending. This file must not be presented as a published release.

## Intended scope

A fictional-data cybersecurity checkup prototype for demonstration and usability
feedback. No production, compliance or independently verified risk-effectiveness
claim is made. Do not upload patient information, real inventories or credentials.

The prototype includes guided Start, Upload, Checklist, Results and Fix First
screens; three fictional clinics; score explanations and coverage warnings;
draft practice views; and PDF, CSV, reusable checklist JSON and readable text
downloads. Docker packaging and automated checks support repeatable evaluation.
These features span prior milestones; they are not all new in Week 6.

## Week 6 hardening

- Guided saved-feed reads use the repository's data/cache directory; browser
  input and stale session values cannot select another server folder.
- Privacy wording distinguishes session-memory application processing from
  unverified host storage/log handling and explains downloaded copies.
- Rejected inventory validation explicitly clears stored reports; regression
  checks cover malformed inputs, file replacement/removal and new-assessment reset.
- Pilot guide, feedback template, pilot report and Gate 3 evidence are documented.

## Evidence at the current checkpoint

November 16 source checkpoint: 2,579 tests passed locally; Bandit zero High and
Medium with eight reviewed Low findings; all 77 pinned requirements queried with
zero known vulnerabilities and no skipped packages; installed pins match and
pip check passed. Audit method and caveats are in
[verification](week-6-verification.md). Final tagged-revision results: **pending**.

Three Week 6 testers were reported at approximately four, two and two minutes,
without help or reported problems, including opening their PDFs. The minimum
participant count is met as reported. The owner confirmed P02/P03 used fictional
clinic examples. First-time status and direct comprehension feedback remain unconfirmed.
Owner also confirmed a keyboard-only sample journey with visible focus, no traps
and PDF download. Keyboard and zoom observations are bounded to exercised views. See
[pilot report](pilot.md) for the count and evidence limits.

## Interpretation and limitations

Scores remain provisional. Missing coverage is unassessed, not safe. The approved
65/82/80 scenario scores and two-band benchmark deviation remain unchanged.
Fix First points/effort does not predict score improvement or actual risk
reduction. Westside's modeled 80-to-99 comparison is simulated, not completed
remediation. Framework relationships are partial/draft and do not prove compliance.

Provider retention/temp-file/log guarantees, complete concurrent-session
isolation, broad assistive-technology coverage, and separate clean-machine local
Docker verification remain unverified. Community Cloud may override package
versions and telemetry configuration. This candidate is not production-ready.

The primary button's deployed default/focused text colors were measured at
6.57:1 after reboot. This is not whole-app contrast certification. The three checked-in PDF
samples include semantic tags, document language and embedded source links.
The Lakeview sample passed a walkthrough of selected reading-order and link
checks with Narrator in Edge. See [PDF verification](pdf-report.md).

Report security concerns using [SECURITY.md](../SECURITY.md), not a public issue
with sensitive details. No response deadline or support window is promised.

## Finalization fields

- Release/tag date: pending
- Reviewed source SHA: pending
- Final tests, audit and CI evidence: pending
- Pilot count: three owner-reported Week 6 testers; fictional-example scope confirmed for P02/P03; feedback disposition pending
- Gate 3 scope/limitations response: pending

Finalize these fields and the [Gate 3 checklist](gate-3-review.md) before tagging.
