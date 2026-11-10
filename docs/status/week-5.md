# Week 5 status

## Done

November 10: user reported green for 6a4c285. Hosted checkout 6a4c285 verified in
runtime-panel screenshots after reboot: Python 3.13.18, Streamlit 1.66.1,
PyArrow 24.0.0, Certifi 2026.10.23, pip 26.3 and usage statistics true.
PyArrow/Certifi differ from pins; host setting overrides the local request.
These deployment differences are recorded, not silently reconciled.

Hosted warnings, 65/82/80 samples, four exports, JSON reuse at 80, missing-file
error, two-window isolation, about-one-minute unassisted first-time PDF completion
and bounded keyboard checks are recorded. See ../week-5-acceptance-review.md
and ../hosted-runtime-review.md.

Last code validation: 2,569 tests passed without exclusions; Bandit/diff checks
passed. This update changes documentation only; no fresh runtime tests claimed.

## Next

Push this acceptance update. Resolve/document provider log/temp-data limits,
CI-versus-local Docker wording, technical reading exceptions and outstanding
framework-reference disposition before closing Week 5.

## Blocked

Local Docker unavailable; CI passed by user report. Week 3 mapping gaps and full
host storage/log-retention review remain unresolved.

## Ask

Keep Week 5 In Progress. Week 4 LinkedIn publication remains unconfirmed.
