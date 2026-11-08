# Guided assessment flow

The app now follows Start, Upload, Checklist, Results and Fix First screens.
The global scoring model, fixture evidence and export renderers are unchanged.

## Start

Choose a fictional clinic or uploaded inventory. Read the privacy notice before
continuing. Fictional scenario evidence is optional and remains explicitly
synthetic. Changing the source, clinic or scenario mode resets the working draft,
optional evidence and old result to avoid mixing assessments.

## Upload

Sample inventories are preloaded on the fictional path. The upload path accepts
CSV, JSON or an XLSX workbook with downloadable templates. Assets and software
are required; services remain optional. An optional existing Nmap XML scan requires
an authorization confirmation. ClinicShield does not perform scans. The inventory
must pass the existing validators before continuing.

Advanced evidence options retain the saved-cache, reviewed OS/NVD mapping and
CVE applicability paths and the observation-age setting. Public feeds are not
fetched in the assessment flow. File bytes stay in the session and loaded filenames
are displayed. Removing an uploaded file clears its stored bytes; changing inventory
format clears the prior inventory. Return navigation preserves loaded files.

## Checklist

The catalog in clinicshield/checklist_questions.json carries a plain-language
rendering of the criteria, definitions and why-we-ask text in docs/checklist.md.
See readability-review.md for wording review and limits. Samples start with their
existing answers; uploads start Unknown. Users can edit all 25 question outcomes,
with Q24 derived from two separate follow-ups and scored once. Q23 is excluded
when medical-device applicability is No, using the existing scoring policy.

The optional Load answers action accepts a saved checklist bundle or legacy
checklist/follow-up files. It validates before replacing answers and applicability.
Loaded and edited answers feed scoring and JSON export; technical evidence is
never inferred from a saved checklist. Edited sample answers may differ from the
original calibration scores. Unchanged scenario samples remain 65/82/80.

## Results and Fix First

Results show components, band, score arithmetic, draft practices, coverage warnings
and detailed confirmed/review findings. Fix First is a separate screen with the
ranked plan, provider requests and PDF/CSV/checklist JSON/TXT downloads. These use
the generated report from the current answers, not a regenerated default sample.

Back preserves answers and inputs. Edits clear the previous report. Generation
is required before results can be shown. Start a new assessment clears the draft,
report and widget state. No user input persistence or network scanning is added.

## Verification

State tests cover saved-bundle reuse, source isolation, invalid input, Q24/Q23,
answer retention and report invalidation. Streamlit AppTest exercises the real
five-screen sample flow, baseline scores, all four downloads, back navigation,
answer edits, applicability, source changes and missing-inventory blocking.
Mocked upload tests exercise generation and exported edited/saved answers.
November 8 manual verification: the user reached Fix First on the Lakeview sample
path, supplied a screenshot showing all four download buttons, and confirmed
Q02: No in the saved JSON after editing the checklist. This confirms the exercised
sample path, not every upload/input combination. Fresh GitHub CI remains pending.

The original risk-sorted findings table, reading-level review, Docker and public
hosting checks remain later Week 5 work. Existing framework-reference gaps remain
unresolved; UI progress is not validation of those mappings.

Local validation November 8: 2,550 tests passed with no exclusions, including all
10 AppTest cases. The earlier Windows stall was traced to sandbox-blocked loopback
socket creation; local network permission and a workspace temp folder allowed UI
tests to run. Changed-file medium/high Bandit and git diff --check passed.
