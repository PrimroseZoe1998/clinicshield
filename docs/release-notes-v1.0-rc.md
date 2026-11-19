# ClinicShield v1.0-rc â€” draft release notes

**Release candidate.** Gate 3 conditions are documented. The local tag exists.
Publication on GitHub is pending.

## Demo scope and limitations

- **Fictional data only.** Use only fictional examples. Do not upload real
  clinic inventories, patient information or credentials. Production deployment
  is outside the approved scope.
- **Provisional results.** Scores reflect the evidence and coverage assessed.
  Fix First prioritizes actions. The prototype provides no security or
  compliance certification.
- **Hosted data handling.** Provider retention, logs and temporary-file
  handling remain unverified. Complete isolation between concurrent hosted
  sessions is unverified.
- **Accessibility coverage.** Keyboard, zoom and Narrator/Edge findings apply
  to the paths tested. Broader accessibility testing remains open.
- **Framework mappings.** References are partial and draft. They do not
  constitute validated compliance assessments.

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
clinic examples. The owner supplied anonymized comprehension responses. First-time status remains unknown.
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
isolation and broad assistive-technology coverage remain unverified. The
[local Docker test](docker.md#november-18-local-docker-walkthrough) passed on a
fresh Docker Desktop installation on the existing development PC. Community Cloud may override package
versions and telemetry configuration. This candidate is not production-ready.

The primary button's deployed default/focused text colors were measured at
6.57:1 after reboot. This is not whole-app contrast certification. The three checked-in PDF
samples include semantic tags, document language and embedded source links.
The Lakeview sample passed a walkthrough of selected reading-order and link
checks with Narrator in Edge. See [PDF verification](pdf-report.md).

Report security concerns using [SECURITY.md](../SECURITY.md), not a public issue
with sensitive details. No response deadline or support window is promised.

## Finalization fields

- Local tag: `v1.0-rc`, November 19, 2026
- Reviewed application SHA: `ea194c3c8210acff92619aa87b3d68046957c40b`
- Reviewed application CI: [checks #231](https://github.com/PrimroseZoe1998/clinicshield/actions/runs/44342494103) and [container #24](https://github.com/PrimroseZoe1998/clinicshield/actions/runs/44342494055) passed on the tagged application revision.
- Pilot count: three owner-reported Week 6 testers; fictional-example scope confirmed for P02/P03; anonymized comprehension responses supplied
- Gate 3 response: approved with conditions for the fictional-data demo. The owner accepted the documented Docker run after Benjamin deferred the decision.

See the [Gate 3 decision and checklist](gate-3-review.md).
