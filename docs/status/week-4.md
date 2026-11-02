# Week 4 status

## November 2 requirement review

Saved implementation checkpoint cc9c303 was pushed with green GitHub checks,
as reported by the user. Both Why this score and R16 provider requests were
confirmed in the app and TXT. See ../week-4-acceptance-review.md for the full
brief/Appendix B comparison and fresh baseline/answer-change demonstration.

Scope correction: practice-area arithmetic is an open Week 4 Appendix B item;
Week 5 covers its results presentation. Earlier Week-5-only statements below
are historical and superseded. Next: define practice mappings, denominators and
unassessed-coverage behavior, preserving the global score. Final rubric review,
original three-band benchmark reconciliation and midpoint publication remain
open. A LinkedIn draft is saved at ../week-4-linkedin-draft.md; nothing was posted.

## November 1, 2026 starting checkpoint

Done: reviewed the original Week 4 requirements. Existing scoring, caps, Critical
ceiling and Fix First ranking are already implemented. Added structured Why this
score data, a shared readable formatter, an app expander and TXT export.
See ../score-explanation.md for scope and checks.

Copyable requests are now implemented for confirmed Fix First actions; see
../provider-requests.md. Stale scoring implementation statements were updated.

Manual score explanation check: supplied screenshots show 34/47 Safeguards,
9 Exposure deduction, raw combined 79.8043 and final 80 for inventory-only
Lakeview. The user confirmed the matching Why this score TXT section.

Next: manually verify provider requests, then review remaining Week 4 requirements
and save/push a tested checkpoint.

Open: the original three-band benchmark conflicts with the later recorded sample
expectation decision. Preserve that decision and current 65/82/80 scenarios;
independent final rubric sign-off remains unverified. Practice-area scores belong
to the later results scope and require defined formulas before implementation.

This is a Week 4 implementation checkpoint, not milestone completion.

Validation November 1: 2,476 tests passed excluding the known locally stalled
Streamlit AppTest file. High-severity Bandit check passed (zero medium/high,
five existing low findings). Browser verification of the new expander remains
the next manual check; no new CI run is claimed.

Latest validation: 2,486 tests passed, excluding the known locally stalled
Streamlit AppTest file. High-severity Bandit check passed (zero medium/high;
five existing low findings). New UI/TXT manual checks and CI are not yet claimed.

## Manual confirmation before November 1 checkpoint

The supplied R16 Fix First screenshot shows priority 2 and a copyable request
for a controlled restore test. The user confirmed its appearance in the TXT
download. The Why this score preview and TXT were also confirmed earlier.
These checks cover the exercised Lakeview paths, not independent rubric sign-off.

## November 2 practice-area design

Draft v1 and complete primary mapping table saved in ../practice-area-scoring.md
and ../practice-area-mapping-draft.json. Checks confirmed unique attribution of
25 questions and 24 rules, total weight 47, and Lakeview 34/47 reconstruction.
Exposure uses known deductions and the full inventory denominator; missing
components stay unassessed. This is a proposed additive report view, not an
approved rubric or runtime change. Next: implement and test the versioned draft.

## November 2 draft practice results implementation

Added practice_scores data and shared app/TXT presentation labelled draft.
Coverage behavior, caps, grouping, Q23 exclusion, Q24 single weighting and
practice-local Critical ceilings are tested; global 65/82/80 and inventory-only
Lakeview 80 are preserved. Next manual check: regenerate Lakeview and expand
Practice-area results (draft), then verify its TXT section. Rubric sign-off
and final scope decisions remain open.

Final local validation November 2: 2,497 tests passed excluding the known
locally stalled Streamlit AppTest file. High-severity Bandit check passed
(zero medium/high findings; five existing low findings).

## November 2 manual verification

Supplied inventory-only Lakeview screenshots show Email Safeguards 50 with
unassessed Exposure; Endpoint Safeguards 66.67, Exposure 91 and combined 76;
Access Safeguards 100 with 12 review groups; Data Safeguards 62.50 with
unassessed Exposure. Draft labels, missing-component behavior and coverage
limits are visible. The user confirmed the same values in the TXT download.
This verifies the exercised presentation/export path, not independent rubric
approval or complete practice coverage. Latest local suite: 2,497 tests passed
with the known stalled UI file excluded; high-severity Bandit passed.

## November 2 final technical review packet

Prepared ../week-4-rubric-review.md and updated ../week-4-linkedin-draft.md.
The user reported ad87f3e pushed with green CI. No model or target band was
changed. Original three-band departure and draft practice policies are explicit.
Independent sign-off and post publication remain open; nothing was sent or posted.
