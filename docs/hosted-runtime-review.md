# Hosted runtime and dependency review

Reviewed November 10, 2026 using the user-supplied Community Cloud log screenshots,
repository requirements and current official Streamlit documentation. The public
log screenshots are observations, not a complete environment manifest.

## Observed differences

| Component | Repository expectation | Supplied hosted-log observation |
| --- | --- | --- |
| Python | Python 3.13 selected | 3.13.18 |
| Streamlit | 1.66.1 | 1.66.1 |
| PyArrow | 25.0.1 | Provider detected 25.0.1, cited a known-segfault workaround, removed it and installed the 24.0 series; full patch version not established from the clipped screenshot |
| Certifi | 2026.10.19 | Provider replaced it with 2026.10.23 |
| pip | Not pinned in requirements.txt | Provider installed/reinstalled 26.3 |

Logs also show repository cloning, dependency processing, server startup and code
updates. No exact checkout SHA is visible. Success in these excerpts does not
prove that all pinned packages remain installed or that all runtime paths pass.

The exact provider PyArrow workaround was not independently found in public
Streamlit documentation. Do not promote the log message into a verified diagnosis
of every PyArrow 25.0.1 installation. The existing repository pins are unchanged;
they have passed local/CI checks, while the hosted app must be recorded as a
provider-adjusted environment. This step adds visibility instead of guessing a
new cross-platform pin or bypassing the host workaround.

## Provider configuration overrides

Official Community Cloud status documentation lists host-enforced settings,
including browser.gatherUsageStats=true. Consequently the repository's false
setting is a request, not proof that hosted usage statistics are disabled. Local
and Docker configuration checks do not establish the effective cloud setting.
This observation does not itself establish collection of assessment contents;
provider telemetry, storage and log policies require their own review.

Sources checked November 10:
- https://docs.streamlit.io/deploy/streamlit-community-cloud/status
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies

## Runtime details panel

Every app screen now has an optional Build and runtime details expander. It shows
Python, installed Streamlit/PyArrow/Certifi/pip versions, corresponding repository
pins and mismatch flags, the effective usage-statistics setting exposed by
Streamlit, and a local Git checkout commit if available. It never dumps the
environment, credentials, filesystem paths, assessment inputs or exception text.
The Git command has fixed arguments, no shell, captured output and a two-second
timeout. Missing Git/metadata produces unavailable rather than breaking the app.
The Docker image deliberately omits Git history, so its commit may be unavailable.

The commit identifies the checkout at inspection time, not a signed build or proof
that every running worker has identical code. Installed package metadata and
reported settings also are not a full security audit. Record the hosted panel
after deployment before resolving the exact-revision/runtime acceptance item.

## Acceptance disposition

Dependency/configuration differences remain documented, not silently reconciled.
Prior sample scores, downloads, user timing and keyboard observations remain
valid for the exercised hosted state; they do not prove local/cloud equivalence.
Hosted temporary-file/log-retention limits, unresolved framework mapping review,
technical reading exceptions and CI-versus-local Docker wording remain explicit.

Local verification: 2,569 tests passed without exclusions, including real UI flows
and five drift/revision/fallback tests. Medium/high Bandit and diff checks passed.
No new hosted panel values or fresh GitHub CI are claimed yet.
