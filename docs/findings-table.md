# Results findings table

Added November 8, 2026. Results now includes a findings overview with reference,
severity, explicit evidence status, title, affected scoring entity, rule IDs,
Exposure points before entity caps and source evidence. Nested evidence details
are shown as JSON within the evidence cell so values remain inspectable.

The initial order is confirmed-from-supplied-evidence findings first, then findings
needing review. Within each group, order by descending severity, descending pre-cap
Exposure points, entity ID and issue key. This is a transparent presentation order,
not a validated risk-reduction estimate or the Fix First points/effort ranking.
Administrative findings may legitimately have zero Exposure points because their
checklist answers are scored once. Review findings and missing evidence do not
establish safety even when they carry no confirmed deduction.

The Show findings filter offers All findings, Confirmed findings and Needs review.
Counts show the displayed and total group counts. References (F001, etc.) remain
stable across filtering within the same generated report and appear on existing
full-detail expanders below the table. References can change after regeneration.
Detailed sections remain available even when the overview is filtered. Users may
sort columns interactively; the reference still identifies the same report item.

The view does not alter the report, scoring, checklist answers, Fix First ranks or
export contents. Tests cover all three fictional clinics, status separation,
severity/points ordering, deterministic ties, evidence preservation, empty findings
and stable filter references. A real Streamlit AppTest verifies filtering, the
unchanged score and linkage to detailed expanders.

November 8 manual verification: user screenshots show Needs review filtering
32 of 38 Lakeview finding groups and F007 matching Application support requires
attention, R04, cloud:1 in the detailed review expander. Supporting evidence and
no confirmed-risk deduction remain visible. This verifies the exercised filter
and reference path; it does not validate the underlying software support status.
Fresh GitHub CI remains pending for this increment.

Local validation: 2,556 tests passed with no exclusions. Changed-file medium/high
Bandit and git diff --check passed. No new GitHub CI is claimed.
