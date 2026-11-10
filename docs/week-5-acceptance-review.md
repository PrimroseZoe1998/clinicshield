# Week 5 acceptance review

Updated November 10, 2026 against the original Week 5 brief and recorded decisions.
The main implementation is complete and the prototype is hosted. Final acceptance
checks remain; this is not full milestone closure.

Live demo: https://clinicshield-uggyfds2f9etx6qo2qelpx.streamlit.app/

## Requirement disposition

| Requirement | Current evidence | Disposition |
| --- | --- | --- |
| Five-screen sample and real-upload flow | Guided UI and local AppTest coverage; user exercised sample flow and local uploads | Implemented; hosted missing-file and two-window isolation checks passed on exercised paths |
| Findings table, practice scores, explanation | Implemented; local browser and automated checks recorded | Implemented; hosted warning presentation needs final check |
| One-page owner PDF and detailed appendix | Three sample artifacts rendered/reviewed; hosted Lakeview PDF confirmed by user | Implemented and exercised |
| Findings CSV and checklist JSON | Local download/re-upload tests and user checks; CSV/PDF samples committed for three clinics | Implemented; hosted CSV/JSON downloads and Lakeview saved-answer reuse confirmed |
| Dockerfile and clean environment execution | Container correction 7210788; user reported green after the build/offline-export/startup workflow | User-reported CI verification; Docker unavailable locally |
| Live v0.9 URL | User opened hosted app and verified 65/82/80 | Hosted; InPrivate access confirmed by user; exact running SHA still unverified |
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

## Remaining acceptance decisions and verification

- Verify the exact deployed revision and hosted provisional/coverage/draft labels.
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

Current intended deployment source is main after 519e44c; the provider's running
SHA has not been independently retrieved. Hosted observations are user reports.
Previous full suite: 2,558 passed with no exclusions; later packaging/layout and
preparation checks are documented separately. This review changes documentation
only and does not imply new tests, security effectiveness or compliance validation.
Week 3 framework-reference gaps remain open. Repository transfer is already waived
by Benjamin's October 16 Gate 1 decision; it is not a deployment blocker.
