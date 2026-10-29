# Public-feed refresh results

Use `python -m clinicshield.refresh_feeds --cache-dir feed-output --status-file
feed-output/refresh-status.json` (on one line) to save a per-run JSON result.
The scheduled workflow also passes this option.

The result contains UTC run start/end timestamps, overall outcome and one entry
for KEV, EPSS and each distinct requested lifecycle product. Successful entries
include retrieval time; expected failures include the exception type without the
exception message. Feeds continue independently after expected download/validation
errors. The command returns nonzero if a feed or status-file write fails.

The JSON report is replaced atomically. Failed writes preserve the previous file;
check stderr, exit status and report timestamps before treating it as a new result.
Unexpected programming errors still propagate; an incomplete run may have no new
report. The Actions summary explicitly flags a missing report and directs readers
to the log. It must not imply successful refresh from an older cache alone.

The Actions run summary shows per-feed outcomes. Run artifacts retain the JSON,
refresh log and produced snapshots for 30 days, including expected partial failures.
This is per-run history in Actions artifacts, not a permanent aggregated ledger or
an additional email/notification integration. GitHub's configured workflow
notifications remain unchanged.

Successful retrieval does not prove source completeness or software applicability.
Assessments retain their independent freshness and coverage checks.

## Manual verification on October 29, 2026

[Run #3 on commit 6099acb](https://github.com/PrimroseZoe1998/clinicshield/actions/runs/40949949834)
completed successfully. The supplied summary screenshot lists KEV, EPSS,
endoflife.date:python and endoflife.date:windows as succeeded. The user confirmed
the artifact ZIP contains all six expected snapshots/log/status files. These are
manual success-path observations; injected local tests cover expected failure
and status-write paths. Scheduled execution and live failure notifications have
not been independently observed.
