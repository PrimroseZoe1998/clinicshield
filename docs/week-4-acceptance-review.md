# Week 4 acceptance review

Reviewed November 2, 2026 against the original project brief's Week 4 table and
Appendix B, implementation checkpoint cc9c303, recorded decisions and observed
manual checks. Status: implementation substantially progressed; milestone open.
The user reported cc9c303 pushed and GitHub checks green on November 1. That CI
result was not independently retrieved. No stakeholder sign-off is inferred.

## Requirement checklist

- [x] Safeguards and Exposure scoring with the existing 60/40 combined score.
- [x] Structured Why this score data, exact fractions, readable app/TXT presentation.
- [x] Confirmed Critical ceiling, responsible group IDs and per-entity caps.
- [x] Fix First ranking, four action groups, owner tags and copyable provider requests.
- [x] docs/scoring.md and implementation guides published in the saved repository.
- [x] Regression tests and an exact single-answer-change demonstration.
- [x] Manual Lakeview preview/TXT checks for arithmetic and provider requests.
- [x] Draft practice-area data, mappings and missing-component behavior implemented
      and labelled provisional; see practice-area-scoring.md. Lakeview app/TXT
      manual verification passed; independent rubric approval remains open. Chart presentation can follow in
      Week 5; the arithmetic is implemented as a draft Week 4 interpretation.
- [ ] Original three-different-bands benchmark: current samples occupy two bands.
      Preserve the October 29 recorded model/expectation decision; do not force
      scores or infer that it independently validates every Gate 2 requirement.
- [ ] Final rubric review/sign-off, including unresolved severity and coverage policy.
- [ ] Midpoint LinkedIn post published by the user. A draft is prepared separately.

## Fresh November 2 benchmark demonstration

Offline evaluation with explicit fictional scenario evidence and a fixed test
clock reproduces these baselines:

| Clinic | Safeguards | Exposure | Overall | Band |
| --- | ---: | ---: | ---: | --- |
| Lakeview | 72.3404 | 55.0000 | 65 | At risk |
| Southside | 70.2128 | 100.0000 | 82 | Needs attention |
| Westside | 80.8511 | 78.6842 | 80 | Needs attention |

Lakeview Q02 No -> Yes, with all other inputs/evidence fixed:
- Earned safeguards weight rises by 3 of 47.
- Safeguards increases exactly 300/47 points.
- Exposure is unchanged at 55.
- Raw combined score rises exactly 180/47 points, from 61.574468... to 65.404255....
- Rounded final score changes from 62 to 65. No Critical ceiling applies.

The 80 shown in the user's November 1 screenshots used inventory-only Lakeview;
the 65 baseline includes explicit fictional scenario evidence. These are different
input/evidence modes, not a score regression.

## Rubric comparison and open decisions

Core numeric severity points, technical multipliers, 25-point cap, inventory-size
normalization, 60/40 blend, bands and Critical ceiling follow the recorded rubric.
Exact stacked multipliers use 2.8125 rather than the brief's display approximation
2.81. Rounding uses documented upward exact-half ties.

Implementation differences requiring explicit scope/decision records:
- Appendix B illustrative Critical triggers differ from current rule severities.
  October 28 accepts High unsupported OS, informational unknowns and specified
  rule assignments; it does not constitute blanket independent approval of every
  severity. CVSS is contextual and does not dynamically change R02 severity.
- Current normalization uses scoring entities including cloud/unmatched entities,
  not only physical assets. Uncertain Internet exposure is flagged but does not
  receive the Internet multiplier. Keep these documented policies visible.
- Fix First uses pre-cap finding points divided by effort, not a simulated score
  improvement. The brief's risk-removed wording must be read with this limitation.
- HHS tie preference uses the existing reviewed checklist relationship registry;
  the later partial rule references do not silently redefine question weights.

## Practice-area design review record

The mapping and implementation now exist in practice-area-scoring.md and
practice_scoring.py. Their explicit design choices cover:
1. Per-practice earned/applicable question weights and Q23/Q24 handling.
2. Whether a question/group can belong to multiple practices and how overlap is
   disclosed without summing practice scores into the overall result.
3. Per-practice technical grouping/caps and the inventory-size denominator.
4. What appears when a practice has no applicable questions or unassessed technical
   coverage. Do not treat missing coverage as a perfect score or invent a denominator.
5. Whether a combined practice score is justified when one component is unavailable.

This is the design-review record for an implemented draft, not an approved rubric. Keep the global
score unchanged while working through it. Independent sign-off remains unverified;
Benjamin's preference not to receive routine reports does not supply rubric approval.

## Validation provenance

Latest implementation run: 2,486 tests passed excluding the known locally stalled
Streamlit AppTest file. The high-severity Bandit check passed with zero medium/high
and five existing low findings. The November 2 work only re-evaluated the documented
sample/answer-change cases and updated documentation; the full suite was not rerun.
No real clinic validation or compliance conclusion is established.

## November 2 manual verification

Supplied inventory-only Lakeview screenshots show Email Safeguards 50 with
unassessed Exposure; Endpoint Safeguards 66.67, Exposure 91 and combined 76;
Access Safeguards 100 with 12 review groups; Data Safeguards 62.50 with
unassessed Exposure. Draft labels, missing-component behavior and coverage
limits are visible. The user confirmed the same values in the TXT download.
This verifies the exercised presentation/export path, not independent rubric
approval or complete practice coverage. Latest local suite: 2,497 tests passed
with the known stalled UI file excluded; high-severity Bandit passed.

## November 2 rubric review packet

Technical review and benchmark disposition are recorded in week-4-rubric-review.md.
The midpoint draft now reflects practice views and the 2,497-test checkpoint.
Independent sign-off and user publication remain outstanding.

## November 2 Westside comparison

- [x] Verify the documented original Westside baseline and a separate explicit
  synthetic post-fix scenario: 80 -> 99, both provisional.
- [ ] Obtain Benjamin approval of the post-fix assumptions/result and remaining
  benchmark differences. See westside-post-fix-verification.md.

Latest local validation is 2,504 passing tests with the documented UI exclusion.
