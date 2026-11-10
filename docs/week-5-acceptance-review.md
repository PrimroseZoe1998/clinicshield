# Week 5 acceptance review

Updated November 10, 2026 against the original Week 5 brief and recorded decisions.
The main implementation is complete and the prototype is hosted. Final acceptance
checks remain; this is not full milestone closure.

Live demo: https://clinicshield-uggyfds2f9etx6qo2qelpx.streamlit.app/

## Requirement disposition

| Requirement | Current evidence | Disposition |
| --- | --- | --- |
| Five-screen sample and real-upload flow | Guided UI and local AppTest coverage; user exercised sample flow and local uploads | Implemented; hosted missing-file and two-window isolation checks passed on exercised paths |
| Findings table, practice scores, explanation | Implemented; local browser and automated checks recorded | Implemented; hosted provisional/draft/unassessed and coverage warnings verified in user screenshots |
| One-page owner PDF and detailed appendix | Three sample artifacts rendered/reviewed; hosted Lakeview PDF confirmed by user | Implemented and exercised |
| Findings CSV and checklist JSON | Local download/re-upload tests and user checks; CSV/PDF samples committed for three clinics | Implemented; hosted CSV/JSON downloads and Lakeview saved-answer reuse confirmed |
| Dockerfile and clean environment execution | Container correction 7210788; user reported green after the build/offline-export/startup workflow | User-reported CI verification; Docker unavailable locally |
| Live v0.9 URL | User opened hosted app and verified 65/82/80 | Hosted; InPrivate access confirmed by user; checkout 6a4c285 verified in hosted panel; provider-adjusted dependencies recorded |
| Reading-level pass | 56 prose blocks at/below grade 8 by local heuristic; definitions and shorter wording added | First-time tester reported no issues; technical-text exceptions remain explicit |
| First-time sample and PDF in under five minutes without help | User reported a separate first-time tester finished in about one minute, without help, including PDF download | Passed by user report; approximate timing, not instrumented measurement |

## Hosted and user acceptance evidence

November 8 user reports/screenshots:

- InPrivate window opened the hosted app without sign-in. A search-engine detour
  was corrected before this observation; search results are not access evidence.
- Hosted original scenario scores matched 65/82/80. Lakeview PDF downloaded and
  opened with an owner summary and detailed appendix.
- Hosted Lakeview CSV and checklist JSON downloaded. Saved JSON was loaded with
  Lakeview fictional inventories, without a separate follow-up file. Upload-mode
  score was the expected 80, without importing synthetic scenario evidence.
- InPrivate retained its 80-point upload result while the normal browser showed
  Start your checkup. Returning to InPrivate preserved that result. This supports
  isolation for those two exercised sessions; it is not a universal privacy audit.
- Submitting empty inventory uploads showed the specific missing-assets/software
  error and kept the user on Upload, as shown in the supplied screenshot. A corrupt
  or malicious file was not manually tested in this hosted check.
- Supplied provider-log excerpt showed dependencies processed, server startup and
  Updated app, with no visible error in that excerpt. It did not establish complete
  log coverage, retention, temporary storage behavior or absence of all exceptions.

November 10 user reports/screenshots:

- A separate first-time tester completed the sample checkup and downloaded the PDF
  without help in about one minute. The user reported everything was good and no
  confusion/issues. This meets the under-five-minute benchmark by user report;
  the duration is approximate, and tester identity is not needed or recorded.
- On the hosted sample path, the user navigated Start, Upload, Checklist, Results
  and Fix First using the keyboard, reported visible focus, changed a dropdown
  with Alt+Down/arrow keys, and confirmed Enter downloaded the PDF. Enter alone
  initially did not open the dropdown; Alt+Down worked. This is a bounded keyboard
  check, not a full accessibility or screen-reader audit.
- The sleeping-app page was encountered; the app reopened after being woken.
  Provider sleep/cold-start behavior is separate from the tester's reported run.

November 10 hosted warning screenshots additionally confirm:

- Lakeview overall 65, Safeguards 72.3, Exposure 55.0 and At risk, with the
  Provisional score warning and the explanation that a higher score does not
  prove safety.
- Practice-area results (draft), draft provisional labels, and explicit statements
  that mappings are not an official HICP crosswalk and practice scores do not
  add or average into the overall result.
- Email Safeguards 50 (3/6), Endpoint 66.67 (2/3), Exposure 91 and combined 76;
  Access Safeguards 100 (10/10), Exposure 91 and combined 96; Data Safeguards
  62.50 (5/8); Network Safeguards 0 (0/5); Vulnerability Safeguards 50 (1/2),
  Exposure 73 and combined 59. These observed values are specific to this sample.
- Missing practice Exposure stays unassessed, and combined results stay
  unavailable when both components are not present. The denominator is 13
  entities, size factor 1/1, with a 25-point cap per entity.
- Six coverage warnings remain, including unavailable KEV/EPSS caches and four
  software entries with no supplied applicability records. Global coverage limits
  and the statement that missing components are not replaced/reweighted remain
  visible. No source coverage or mapping validation is inferred from this check.

## Remaining acceptance decisions and verification

- Hosted checkout 6a4c285 and provisional/coverage/draft labels are confirmed in
  November 10 screenshots. Preserve the observed PyArrow/Certifi drift and
  host-enabled usage statistics in the deployment record.
- Complete or document the limits of hosted temporary-data/log-retention checks
  against the existing threat model. Do not infer them from successful downloads.
- The original issue asks for a clean-machine local Docker run. CI build/offline
  exports/startup passed by user report, but local Docker is unavailable. Keep
  that distinction visible unless CI is explicitly accepted as equivalent.
- Human feedback and the 56-block heuristic support plain-language improvements;
  formal references, raw evidence and technical text still have documented grade
  exceptions. The literal all-text grade-8 condition is not universally validated.
- The combined framework-references/attribution issue item remains open because
  unresolved Week 3 mapping review is not completed by developer attribution.
- Finalize these dispositions before closing the Week 5 issue; do not convert
  bounded observations into production, compliance or complete security validation.

## Provenance and scope

Latest screenshot-verified hosted checkout is 6a4c285e7d84f8873644a19dbd4f7bd0d12c7107.
Hosted observations are user reports/screenshots, not independent agent browsing.
Previous full suite: 2,558 passed with no exclusions; later packaging/layout and
preparation checks are documented separately. This review changes documentation
only and does not imply new tests, security effectiveness or compliance validation.
Week 3 framework-reference gaps remain open. Repository transfer is already waived
by Benjamin's October 16 Gate 1 decision; it is not a deployment blocker.


## November 10 hosted dependency evidence

User log screenshots show Python 3.13.18, Streamlit 1.66.1, a provider PyArrow
25.0.1-to-24.0-series workaround and Certifi 2026.10.23 replacing the repository
pin. No commit SHA was visible. Runtime details panel added to expose checkout,
selected installed versions/pin drift and effective usage-statistics setting.
Official host override documentation means the repository's telemetry setting
must not be asserted as effective in Community Cloud. See hosted-runtime-review.md.
The pins remain unchanged; exact hosted runtime and provider policy limits remain
acceptance observations to record, not proven local/cloud equivalence.


The November 10 runtime panel screenshots confirm checkout 6a4c285, Python
3.13.18, Streamlit 1.66.1, PyArrow 24.0.0, Certifi 2026.10.23 and pip 26.3.
Effective usage statistics is true despite the repository's false request.
See hosted-runtime-review.md for exact pins, evidence limits and reboot behavior.
This resolves identification of the exercised checkout, not the remaining
provider-data-handling or scope-acceptance decisions.
