# Week 4 rubric review packet

## November 3, 2026 — current acceptance status

Benjamin's reply, supplied by the user on November 3, accepts the documented
prototype scope. See [approval record](week-4-approval.md) for the decision,
conditions and evidence provenance. Earlier pending-approval statements below
are historical and superseded by this record; they are not current blockers.
The mappings and scores remain draft/provisional. Scope acceptance does not
validate clinical cybersecurity effectiveness, compliance or production readiness.


Prepared November 2, 2026 for implementation ad87f3e. Technical review completed;
independent rubric sign-off remains unverified. This packet is not an approval.

## Proposed checkpoint disposition

Retain the current global model and recorded scenario expectations. Do not
alter severities or thresholds to manufacture three bands. Keep the additional
practice-area views labelled draft/provisional and explicitly record their
unassessed components. This follows the October 29 reported model decision;
it does not expand that decision into approval of every implementation policy.

## Verified implementation

| Topic | Implemented behavior | Evidence |
| --- | --- | --- |
| Safeguards | Existing weights; Yes earns weight, Unknown/No zero; Q23 applicability; Q24 once | scoring.py; scoring and explanation tests |
| Exposure | Confirmed grouped technical points; multipliers; 25-point entity cap; full-entity size adjustment | grouped_scoring.py; cap, grouping and size tests |
| Combined | 60/40 exact arithmetic; half-up whole rounding; confirmed Critical ceiling 69 | scoring.py; boundary and ceiling tests |
| Explanation | Questions, groups, multipliers, entity totals and rounding as structured data and readable app/TXT | score_explanation.py; manual Lakeview check |
| Fix First | Points/effort; KEV/Essential/PHI ties; four groups; owners; unknown-cost handling | fix_first.py; ordering and mixed-evidence tests |
| Copyable requests | Confirmed evidence only; separate combined-control branches; owner/cost/evidence request | provider_requests.py; R16 preview/TXT check |
| Practice views | Draft mapping; retained weights; no fabricated technical 100; component availability; isolated Critical ceilings | practice_scoring.py; Lakeview preview/TXT and automated checks |

Scenario evidence ON: Lakeview 65 (At risk), Southside 82 (Needs attention),
Westside 80 (Needs attention). Inventory-only Lakeview is 80; do not confuse those
modes. Current samples occupy two bands. The later recorded decision supersedes
earlier sample targets only; the original Gate 2 three-band condition is therefore
an explicit scoped departure, not a passed three-band test.

## Decisions not independently approved

1. Practice primary attribution and unavailable-component policy. A numeric
   practice combined score needs both components; no-finding technical coverage
   is unassessed. Administrative-only practices therefore lack combined scores.
2. Scoring-entity denominator includes cloud/unmatched entities. Unknown Internet
   exposure remains flagged without an Internet multiplier. Primary practice
   views use the full inventory denominator rather than an inferred subset.
3. Fix First uses pre-cap finding points, not simulated marginal score benefit;
   cap/overlap/ceiling interactions mean these are different quantities.
4. Severity triggers differ from the brief's illustrations. October 28 decisions
   cover identified assignments/High unsupported OS/informational uncertainty,
   not blanket approval of all severities. CVSS remains source context rather
   than automatically upgrading R02.
5. Existing checklist Essential links control weights/ties. Partial rule-level
   HHS references do not silently change them. Framework-reference review limits
   from Week 3 remain open.

Keep these visible in docs/scoring.md and the implementation guides. A reviewer
can accept a bounded prototype scope or request a specific change; neither a green
CI result nor a general hands-off email is independent rubric sign-off. No further
email was sent, and no new approval is assumed.

## Evidence and remaining deliverables

The latest broad local run passed 2,497 tests with the known stalled local UI file
excluded. Bandit found zero medium/high findings and five existing low findings.
The user reported ad87f3e pushed and GitHub checks green. Supplied screenshots and
user confirmations cover the selected Lakeview app/TXT paths. This documentation
review changed no runtime code, so tests were not rerun.

- [x] Technical review packet and documented benchmark disposition prepared.
- [x] Draft practice-area implementation and exercised manual checks recorded.
- [x] Updated midpoint LinkedIn draft prepared, not published.
- [x] Explicit prototype scope acceptance recorded November 3; see week-4-approval.md.
- [ ] Midpoint post reviewed and published by the user.

Week 4 remains open; technical implementation for this bounded checkpoint is
saved. No real clinic control validation, breach probability or compliance claim
is made by the model.
