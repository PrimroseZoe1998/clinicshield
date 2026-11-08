# Hosted v0.9 deployment preparation

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
The root Streamlit config disables usage statistics and file watching, uses
headless mode and caps each upload at 10 MB. Existing application validators still
enforce JSON-specific, row/cell and combined-upload limits. No passwords, patient
data, personal inventories or local caches are included as deployment secrets.

## Hosted checks before Week 5 closure

- [ ] Record the actual HTTPS URL, revision, access settings and Python version.
- [ ] Open the URL in a separate browser session and follow all five screens.
- [ ] Verify original sample scenarios at 65/82/80 with scenario evidence enabled.
- [ ] Confirm provisional labels, unknown evidence and draft mappings remain visible.
- [ ] Download/open PDF and CSV; save/reload checklist answers on synthetic data.
- [ ] Check invalid-upload errors and session isolation using fictional inputs.
- [ ] Review provider logs, temporary storage behavior and app error output.
- [x] Document the maintainer-selected private reporting route: SECURITY.md lists
      zmangwendeza@gmail.com, explicitly authorized by the user on November 8.
      No automated email was sent; mailbox delivery remains untested.
- [ ] Have a first-time user complete the sample path and PDF download in under
      five minutes without help; record the result and comprehension feedback.

Source references, readability-screen limits and unresolved Week 3 mappings remain
explicit. These checks do not establish compliance or production readiness. The
literal all-text reading-level target remains subject to documented technical-text
exceptions and human review. Do not mark Week 5 fully closed from Docker CI alone.


Preparation validation: Streamlit successfully loaded all four root config
settings. Twenty-seven sample/export tests passed. All three fictional CSV
artifacts match their report group counts and expected scores. Bandit medium/high
and git diff --check passed. The security contact is documented with user consent;
authenticated provider setup, public launch and hosted checks remain pending.
