# Week 6 security and accessibility checkpoint

Reviewed November 16, 2026, against source revision f1c37fa. Documentation-only
updates follow this revision. This is evidence for Gate 3 review, not approval
of the release candidate or a claim of production readiness.

## Dependency audit

`python -m pip_audit -r requirements.txt --no-deps --disable-pip --format json`

Result: **77 packages, zero known vulnerabilities, zero skipped packages**.
All 77 requirement entries are exact version pins; installed package metadata
matches each pin. `python -m pip check` reports no broken requirements.

The initial resolver-backed local audit failed because its temporary virtual
environment could not be created under the sandbox temporary directory. The
successful run queried the complete pinned requirements directly, with dependency
resolution and pip execution disabled, using a writable cache directory. It did
not ignore advisories or packages. It does not prove completeness of the lock
file or re-installability on every platform. CI retains its normal requirements
audit and install steps. Known-advisory results are time-dependent and must be
rerun for the actual release candidate. They do not cover provider-adjusted
Community Cloud packages; see [hosted runtime review](hosted-runtime-review.md).

## Code security scan

`python -m bandit -r clinicshield app.py docs/create_workbook.py -f json`

Result: **zero High, zero Medium, eight Low findings**, no scan errors.
The all-severity scan is recorded here without suppressing findings:

| Finding | Location | Review disposition |
| --- | --- | --- |
| B105, twice | credential_handlers.py, lines 40 and 48 | Yes/No status comparisons for default-password-change evidence, not embedded credentials |
| B106 | sample_evidence.py, line 80 | Fictional default_password_changed="No" status, not a password value |
| B405, twice | nmap_input.py line 2; workbook.py line 4 | Standard-library ParseError imports; Nmap parsing uses defusedxml with entities/external references forbidden; workbook ingestion has archive limits and regression tests |
| B404/B607/B603 | runtime_details.py lines 6 and 13 | Fixed git rev-parse command, no shell or browser arguments, bounded timeout and validated revision output; trusted server PATH/root remain operator responsibilities |

These Low findings are retained for review. No unsafe arbitrary command or
credential is introduced to silence them. This scan is not a penetration test
and cannot validate every parser, dependency or hosting behavior.

## Accessibility evidence and next manual pass

Fresh full local regression suite: **2,579 passed**, no exclusions. This includes
real Streamlit AppTest flows and the upload/reset/privacy regressions. Automated
tests do not replace the manual accessibility checks below.

Existing evidence: Week 5 user-reported keyboard navigation through the sample
flow, visible focus, dropdown selection using Alt+Down/arrow keys and Enter PDF
download. Automated flows check labels, guidance and reset behavior. All 56
selected prose blocks remain subject to the local grade-8 screening test; this
does not establish universal reading level or comprehension.

One Week 6 tester reportedly completed the guide in four minutes without help
and reported no issues. Direct comprehension responses and screen-reader use
were not recorded. See [pilot report](pilot.md). Do not mark a complete
accessibility audit based on those observations.

For a fresh bounded manual pass, use fictional Lakeview inputs only:

- Navigate Start, Checklist, Results and Fix First with Tab/Shift+Tab. Record
  whether focus stays visible and whether any control cannot be reached.
- Use the keyboard to change a dropdown, open/close an explanation and download
  the PDF. Record the actual keys needed, rather than assuming Enter works for
  every control. Do not change the documented scenario answers when checking
  benchmark scores.
- At 200% browser zoom, check whether privacy/score warnings, labels, navigation
  buttons and recommendations remain readable and reachable. Scrollable tables
  may require horizontal scrolling; log hidden/clipped controls or text.
- Confirm severity/status and warnings are conveyed in text, not color alone.
- Ask pilot testers to explain provisional scores, unassessed coverage and
  priority in their own words. Log misunderstandings and retest fixes.

## Hosted 200% zoom observations reported November 16

After reporting GitHub checks green for 43337ba, the owner performed the guided
200% browser zoom check and reported:

| Screen | Owner-reported result |
| --- | --- |
| Start | No text overlap or clipping; all controls reachable, including notice, clinic selection and Continue to Upload |
| Results | Scores, provisional warning, explanations and Continue to Fix First readable and reachable |
| Fix First | Opened action content and download control readable/reachable; no overlap or clipping reported |

The owner restored normal zoom using the browser menu after Ctrl+0 did not
restore it. This is a browser interaction observation, not an app defect
diagnosis. No code change was required by the reported zoom exercise.

These are owner-reported checks on the exercised hosted views, not independent
screenshots or measurements. Browser/device, viewport dimensions and exact
checkout revision were not supplied for this pass. Do not generalize the result
to every table cell, optional control, viewport, PDF magnification or assistive
technology. Upload and Checklist were traversed but not separately confirmed as
complete zoom-review screens. That zoom exercise did not establish keyboard-only,
contrast measurement, screen-reader or WCAG conformance results. Full host persistence/
retention review, framework mapping validation and Gate 3 disposition remain open.

## Subsequent hosted keyboard-only check

The owner confirmed completing all four requested steps without the mouse:
selecting the fictional Lakeview scenario, proceeding through Checklist to
Results, opening a score explanation, and continuing to Fix First to download
the PDF. The owner explicitly confirmed visible focus throughout, no keyboard
traps, and successful PDF download. No mouse-only control or defect was reported.

This is a user-reported check of the exercised journey, not an independent
observation of all widgets, optional uploads, table interactions or browser/device
combinations. Exact keys used, browser version and source SHA were not supplied;
the guide offered Alt+Down if Enter did not open a dropdown. No assistive-technology,
contrast or WCAG conformance claim follows. This is separate owner verification,
not a second pilot participant. No code change or fresh test run was needed.
