# Week 5 development plan â€” November 9â€“13, 2026

Prepared November 3 after Benjamin accepted the Week 4 prototype scope.
This is a proposed implementation sequence, not a new stakeholder-approved
expansion of scope. The recorded brief places Streamlit/results sub-scores and
report delivery in Week 5; confirm detailed acceptance criteria against the
original brief before implementation.

## Objective

Make the accepted scoring explanations, draft practice-area results and Fix First
plan easier to inspect in the results interface and downloaded report, while
preserving the current scoring model and explicit evidence limits.

## Planned sequence and review criteria

1. Review the existing Streamlit results and report path against the Week 5 brief;
   record gaps and the required report format before selecting implementation.
2. Improve practice-area results presentation, including charts if required.
   Unassessed components must appear as unassessed, not zero or perfect scores;
   combined values require both components. Preserve draft labels and denominators.
3. Align report delivery with the results view. Keep score explanations, Fix First
   owners/effort/provider requests, provisional status and coverage warnings visible.
   Keep the fictional Westside comparison explicitly separate from completed work.
4. Verify exercised app/export paths and relevant regressions. Preserve 65/82/80
   scenario baselines and the separate synthetic 80 â†’ 99 fixture. Record exact test
   commands, exclusions and CI provenance when the implementation is verified.
5. Prepare a review packet with screenshots/export samples, remaining limitations
   and requirement-by-requirement disposition.

## Constraints carried forward

Benjamin requested no scoring-model changes. Fix First remains a points/effort
heuristic, not predicted benefit. Practice mappings stay draft and framework
references remain unvalidated where unresolved. Acceptance conveys no clinical
effectiveness, regulatory compliance or production-readiness conclusion.

## Starting status

Planning only; no Week 5 implementation or validation is claimed. Week 4 midpoint
publication remains a separate user action planned for November 6.


## November 8 requirements correction and first increment

Original brief Sections 4.2 and Week 5 explicitly require a five-screen flow,
interactive 25-question checklist, risk-sorted findings table, owner-summary PDF
with detailed appendix, findings CSV, checklist JSON, Dockerfile, public v0.9,
reading-level pass and an under-five-minute first-time sample check. Commit PDF
and CSV samples for all three fictional clinics. The earlier plan above was
incomplete; charts are not an explicit requirement in the reviewed Week 5 text.
Section 14 also requires repository ownership/transfer resolution before deployment.

Findings CSV and reusable checklist JSON are now implemented locally; see
report-exports.md. They preserve the existing model. Remaining order: PDF report,
five-screen/checklist/results work, readability/sample verification, packaging
and deployment. Week 4 publication is not assumed complete without confirmation.
