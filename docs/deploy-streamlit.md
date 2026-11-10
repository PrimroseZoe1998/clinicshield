# Hosted v0.9 deployment preparation

## November 8 hosted verification update

Live demo: https://clinicshield-uggyfds2f9etx6qo2qelpx.streamlit.app/

The user deployed from PrimroseZoe1998/clinicshield, main, app.py, with Python
3.13 selected in the supplied settings screenshot. Deployment followed checkpoint
519e44c, whose GitHub checks were reported green. The exact provider-reported
running SHA and public access from an unauthenticated browser remain unverified.

The user confirmed hosted scenario scores Lakeview 65, Southside 82 and Westside
80 with fictional scenario evidence enabled and unchanged answers. The hosted
Lakeview PDF downloaded and opened with 65/100, an owner-summary first page and
a detailed appendix starting on page two. These are user-confirmed observations,
not independent agent browser checks. Hosted CSV/checklist reuse, separate-session
isolation, invalid-upload behavior, provider logs and the timed first-time-user
benchmark remain open. Earlier preparation-only statements below are historical.


Prepared November 8, 2026. Target: Streamlit Community Cloud, using the current
repository and Python 3.13. This prepares a prototype demo; no public URL,
provider authorization or successful hosted deployment is claimed yet.

## Repository decision already recorded

Gate 1 records Benjamin's October 16 email decision: no repository transfer is
required; the repository stays under Primrose's account. His October 18 decision
retains the brief's ChiEAC branding, hosted-instance and service terms and Primrose's
lead developer credit. See gate-1-review.md, accepted-decision table. Earlier
Week 5 statements treating transfer as an unresolved blocker were stale and are
superseded by this record. No new ownership approval or transfer is needed.

## Deployment fields

| Field | Value |
| --- | --- |
| GitHub repository | PrimroseZoe1998/clinicshield |
| Branch | main |
| Main file | app.py |
| Advanced settings: Python | 3.13 |
| Secrets | None required for the fictional sample demo |
| App URL | Use an available subdomain; record the actual assigned URL after deployment |

1. Commit/push this preparation and verify both check workflows.
2. Open https://share.streamlit.io and sign in. Connect the GitHub account if the
   service asks. Review provider permissions before granting them.
3. In the PrimroseZoe1998 workspace, choose Create app, then the existing-app /
   GitHub repository option. Enter the fields above; manually enter them if the
   repository is not suggested.
4. Select Python 3.13 in Advanced settings and save. Confirm the app visibility
   for the intended public prototype demo; repository visibility can set defaults.
5. Deploy, watch build logs, and record the resulting URL and deployed revision.
   A build error requires the failing log, not a change to the scoring model.

Official instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
Permissions/visibility: https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app

Community Cloud installs requirements.txt directly; it does not run this
repository's Dockerfile. Docker workflow success is separate packaging evidence.
The root Streamlit config requests disabled usage statistics/file watching,
headless mode and a 10 MB per-upload cap. Community Cloud can override settings,
including usage statistics; see hosted-runtime-review.md and the runtime panel. Existing application validators still
enforce JSON-specific, row/cell and combined-upload limits. No passwords, patient
data, personal inventories or local caches are included as deployment secrets.

## Hosted checks before Week 5 closure

- [ ] Record the actual HTTPS URL, revision, access settings and Python version.
- [x] User confirmed public InPrivate access and hosted sample flow.
- [x] User confirmed original hosted scenarios at 65/82/80 with scenario evidence enabled.
- [x] November 10 screenshots confirm provisional/draft labels, unassessed
      practice components, missing combined values and coverage warnings.
- [x] User downloaded/opened hosted Lakeview PDF: 65, owner summary and appendix.
- [x] User confirmed hosted CSV/JSON downloads and saved Lakeview checklist reuse at 80.
- [x] User confirmed missing-file error and two-window session separation.
      Other malformed-file cases were not manually exercised here.
- [ ] Review provider logs, temporary storage behavior and app error output.
- [x] Document the maintainer-selected private reporting route: SECURITY.md lists
      zmangwendeza@gmail.com, explicitly authorized by the user on November 8.
      No automated email was sent; mailbox delivery remains untested.
- [x] November 10 user report: separate first-time tester completed the sample and
      PDF download in about one minute, without help; no issues reported.
- [x] November 10 user confirmed keyboard navigation, visible focus, dropdown
      selection with Alt+Down/arrows and Enter-triggered PDF download.

Source references, readability-screen limits and unresolved Week 3 mappings remain
explicit. These checks do not establish compliance or production readiness. The
literal all-text reading-level target remains subject to documented technical-text
exceptions and human review. Do not mark Week 5 fully closed from Docker CI alone.


Preparation validation: Streamlit successfully loaded all four root config
settings. Twenty-seven sample/export tests passed. All three fictional CSV
artifacts match their report group counts and expected scores. Bandit medium/high
and git diff --check passed. The security contact is documented with user consent;
authenticated provider setup, public launch and hosted checks remain pending.


November 10 update: hosted checks, tester timing and keyboard observations are
recorded in week-5-acceptance-review.md. Provider logs were reviewed only through
the supplied excerpt; temporary storage/log retention and exact running SHA are
not thereby established. No independent human accessibility certification is made.


November 10 provider-log review: Python 3.13.18 and Streamlit 1.66.1 were visible,
along with provider overrides to PyArrow and Certifi. The exact Git SHA was not
shown. Build and runtime details now provides a targeted diagnostic view; hosted
verification of the new panel remains pending. See hosted-runtime-review.md.
