# Run ClinicShield with Docker

This package runs the prototype on port 8501 with Python 3.13 and the existing
pinned requirements. It includes source, fonts and licenses, 24 rules, templates,
the NVD allowlist and three fictional clinics. It excludes local environments,
Git history, development files, saved feed caches and generated sample reports.
The app runs as user 10001, rather than root. No image is published by the workflow.

## Local build and run

Install and start Docker Desktop with Linux containers, or use Docker Engine on
Linux. Run these commands from the repository root. The first build downloads
the base image and dependencies, so it needs internet access.

```powershell
cd C:\Users\zmang\ClinicShield
docker build --pull -t clinicshield:local .
docker run --rm --name clinicshield-local --read-only --tmpfs /tmp:rw,noexec,nosuid,size=128m --cap-drop ALL --security-opt no-new-privileges -p 127.0.0.1:8501:8501 clinicshield:local
```

If local Streamlit already uses port 8501, stop it first, or map
`-p 127.0.0.1:8502:8501` and open port 8502 instead. Open
[localhost:8501](http://localhost:8501), follow a sample through the five screens
and download the PDF. The container starts without loading public feeds.

In another terminal, check health or stop this named container:

```powershell
docker inspect --format='{{.State.Health.Status}}' clinicshield-local
docker stop clinicshield-local
```

The read-only root filesystem prevents writes to image files. The temporary
filesystem supports runtime scratch files and is discarded when the container
stops. It is not a promise of no persistence by the host: downloaded reports,
Docker logs, host swap and platform configuration have their own lifecycle.
ClinicShield's assessment/export paths process user inputs in memory. Do not
upload patient information. This local command publishes only to the local host;
it does not deploy a public service.

## Optional saved public feeds

Caches are deliberately not baked into the image. If needed, mount a prepared
cache folder read-only at `/app/data/cache`, and use that path under Advanced
evidence options. No refresh is run during app startup. Keep source freshness,
missing evidence and reviewed-applicability limits visible. Do not mount user
assessment folders as writable volumes for this prototype.

## Automated container verification

The ClinicShield container workflow builds the image on an Ubuntu GitHub runner.
An offline, non-root, read-only container checks all three scenario scores
(65/82/80), PDF and CSV generation, reusable checklist JSON, and excluded local
files. A separate container starts Streamlit; the workflow waits for its Docker
health check and requests `/_stcore/health` through the published local port.
Startup logs are shown and the named test container is removed even after failure.
This verifies packaging/startup and backend sample exports, not a timed browser
usability check or production readiness.

## Verification status and limits

Docker CLI and Docker Desktop were not found on this development computer on
November 8. Image build, dependency installation inside Linux, container health
and clean-machine execution therefore remain unverified until the new workflow
passes or a Docker-equipped machine runs the commands above. Do not mark the
original clean-machine benchmark complete from static file checks alone.

The Python 3.13 slim tag is maintained upstream and is not pinned by digest here.
Dependencies use the existing requirements file, including development tools.
A smaller runtime-only lockfile and digest-pinned release are later hardening
options. Repository transfer is waived by the recorded Gate 1 decision; see
deploy-streamlit.md. Hosted verification prerequisites remain open. Docker packaging does not validate unresolved framework mappings.

References: [Streamlit Docker guide](https://docs.streamlit.io/deploy/tutorials/docker),
[Dockerfile reference](https://docs.docker.com/reference/dockerfile/), and
[Docker run reference](https://docs.docker.com/engine/containers/run/).

Local preparation checks: YAML parsing, Python smoke-script syntax and JSON-form
Docker commands validated; 33 sample/export/PDF tests passed. Changed-script
medium/high Bandit and git diff --check passed. These are not container execution.


## Initial runner result and copy correction

The user-supplied November 8 runner screenshot confirms the image built. The
subsequent offline smoke check stopped at the excluded-content assertion; app
startup was skipped. The original error did not name the path, so the exact
unexpected entry was not established from that screenshot.

The Dockerfile now copies only the three named clinic directories instead of
the whole samples directory. The ignore file also explicitly excludes reports,
including empty directory structure. The smoke check retains its strict exclusion
rule and now names the unexpected path. Six local layout-check tests pass,
including rejection of empty report/cache/development directories and a dummy
secret file. Bandit medium/high and diff checks pass. A rebuilt runner check is
still required; startup and clean-machine acceptance are not yet established.


November 8 runner update: after 7210788 the user reported green checks. This is
user-reported CI evidence, not independently retrieved runner logs. The local
computer still has no Docker installation. Hosted behavior remains separate.
