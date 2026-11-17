# ClinicShield fictional-data pilot guide

Prepared November 16, 2026. Status: ready for a small usability pilot.
This guide does not authorize testing with real clinic or patient data.

## Purpose and boundaries

Check whether a new user can finish a sample checkup, understand its limits and
download a readable report. This is usability feedback, not a security audit,
clinical validation, compliance review or production-readiness assessment.

Use only the built-in fictional clinics. Do not upload patient information,
real inventories, credentials, scan files or other sensitive information.
Do not make changes to real systems based on the demonstration's actions.
Host storage and logs have not been fully checked. Downloaded reports create
copies on the tester's device. Participation is optional; stop at any time.

## Instructions to send to a tester

1. Open https://clinicshield-uggyfds2f9etx6qo2qelpx.streamlit.app/.
   If it is asleep, use the wake-up button and wait for Start. Record this wait
   separately from checkup time. No GitHub account should be needed to try the demo.
2. Read the privacy notice. Choose **Fictional example**, then **Lakeview Family
   Dental**. Tick **Include documented fictional scenario evidence**. This
   evidence is simulated, not evidence of work completed at a real clinic.
3. Click **Continue to Upload**, then **Continue to Checklist**. Leave advanced
   evidence options at their defaults; do not enable saved public-feed caches.
4. Review the prefilled checklist answers without changing them. Use the word
   guide or explanations if helpful. Click **Generate assessment**.
5. Look at the scores, provisional warning and coverage information. Explain in
   your own words what the score can and cannot tell you. You may open
   **Why this score** or a finding to understand it.
6. Click **Continue to Fix First**. Find one action, identify who should handle
   it, and explain what its priority means.
7. Click **Download assessment (PDF)**. Open the downloaded file and check that
   its first-page summary and detailed appendix are readable.
8. Click **Start a new assessment**. Confirm Start appears. Complete the
   [feedback form](pilot-feedback-form.md). Record any confusion or failure;
   successful completion is not required for useful feedback.

## Observer record

Use a tester code such as P01 rather than a name. Record the date, browser,
device type and source revision from **Build and runtime details**, if available.
Do not request logs, account details or screenshots containing private material.
Record time from starting the ready app's checkup to downloading and opening the
PDF. Separate cold-start time. Note assistance, retries and whether instructions
were read aloud. Do not coach during the attempt; if help is needed, record it
and then help or stop. Feedback should never be presented as unassisted if coached.

The existing benchmark is an unassisted first-time sample checkup and report
download within five minutes. Report each observation and the number of testers;
one successful attempt does not establish general usability or accessibility.

For the unchanged documented Lakeview scenario, the regression expectation is
65 overall, 72.3 Safeguards and 55 Exposure. Record a mismatch rather than editing
answers to force that result. Scores must remain provisional. Missing coverage
must stay visible. A high score does not prove safety; unassessed is not safe.
Fix First points divided by effort is a heuristic, not predicted score gain or
real risk reduction. A modeled improvement is not completed remediation.

## Recording and follow-up

Use [the blank form](pilot-feedback-form.md) for each tester. The form defines no
collection endpoint; the project owner must choose a private return route before
sharing it. Do not post raw feedback containing personal or infrastructure details
in GitHub issues. Summarize anonymized results and link tracked fixes separately.
Keep completed forms out of the repository unless reviewed and anonymized.

For security concerns, use the private reporting route in [SECURITY.md](../SECURITY.md)
rather than a public issue. Do not include patient data or credentials in a report.

Resolve blocking navigation/download failures before a wider pilot. Retest fixes
and retain unsuccessful attempts in the summary. Hosted retention, concurrent
session behavior and unfinished framework mappings remain separate review items;
this exercise cannot close them.
