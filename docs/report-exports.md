# Findings CSV and saved checklist exports

Implemented November 8, 2026 as the first Week 5 development increment.
The results screen offers findings CSV and saved checklist JSON alongside TXT.
All export generation is in memory; no uploaded assessment data is saved.

## Findings CSV

One row represents one grouped finding, including confirmed findings and items
needing review. Columns retain severity, source entity/group IDs, rule IDs,
evidence, recommendations, owners, effort, costs, framework-reference review
status and EPSS context. Lists and objects are JSON inside CSV cells. Assessment
time, score status, score limitations, coverage issues and fictional-example
context accompany each row. An empty findings list produces column headers only.

Exposure points are pre-cap finding points, not an action's predicted score
improvement or risk reduction. Spreadsheet formula-like scalar cells are prefixed
with an apostrophe; ordinary CSV quoting also preserves commas/newlines/quotes.
Exports retain the current grouped finding order; a risk-sorted results table is
still a separate Week 5 deliverable.

## Saved checklist JSON

Version 1 includes checklist_schema_version, all 25 answers, Q24a/Q24b follow-ups
and medical_devices_present. It contains no inventory or technical evidence.
Upload it into Checklist answers (JSON), omit the separate follow-up file and
leave medical-device presence at Unknown to use the saved applicability value.
Conflicting explicit applicability or a separate follow-up file is rejected.
The existing flat checklist plus separate follow-up JSON import still works.

Reusing answers does not reuse or verify technical evidence. A score can change
with the inventory, evidence, freshness or policy. Unknown answers stay Unknown;
Q24 consistency and all existing answer validation remain enforced.

## Verification

Tests cover all three fictional clinics, exported answer round trips through the
upload path, applicability, malformed/conflicting bundles, evidence preservation,
CSV quoting/formula handling and the UI download wiring. The known locally
stalled tests/test_app_preview.py remains excluded from the broad local suite;
mocked upload UI checks are exercised.

November 8 user screenshots confirm both download buttons, the CSV opened in
Excel with headings and finding rows, and JSON containing all 25 answers,
follow-ups and medical-device presence. After restarting Streamlit, the saved
JSON uploaded successfully with Lakeview inventories and no separate follow-up
file: 80 overall, 72.3 Safeguards and 91.0 Exposure. Provisional and coverage
warnings remained visible. This manual check covers that path only.
Broad local validation: 2,526 tests passed; changed-file medium/high Bandit
check and git diff --check passed.

PDF export, five-screen navigation, findings table, Docker and hosted deployment
remain future Week 5 work. These exports do not validate unresolved framework
references or change the accepted scoring model.
