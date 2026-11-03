# Practice-area scoring specification — draft v1

## November 3, 2026 — current acceptance status

Benjamin's reply, supplied by the user on November 3, accepts the documented
prototype scope. See [approval record](week-4-approval.md) for the decision,
conditions and evidence provenance. Earlier pending-approval statements below
are historical and superseded by this record; they are not current blockers.
The mappings and scores remain draft/provisional. Scope acceptance does not
validate clinical cybersecurity effectiveness, compliance or production readiness.


Prepared November 2, 2026. This is a reviewable implementation proposal, not a
publisher-endorsed crosswalk or independent rubric approval. The design initially made no runtime change; see the implementation
checkpoint below for the later additive draft view. Global scoring is unchanged. Existing global scores, severity assignments, weights and bands
remain authoritative. The original brief calls for the same arithmetic restricted
to ten HICP practices but leaves attribution and unavailable-component behavior
unspecified; the decisions below make those choices explicit.

## Attribution

Use the existing ten sections in docs/checklist.md as primary display categories.
Every weighted question belongs to exactly one category. Assign each rule one
primary practice below so grouped points are not repeated across views. These
are project display assignments; do not derive them from all partial framework
references or present them as official HICP mappings.

| Practice | Checklist questions | Primary rule IDs | Full applicable weight |
| --- | --- | --- | ---: |
| 1. Email protection | Q01, Q02 | R12 | 6 |
| 2. Endpoint protection | Q03, Q04, Q05 | R05, R15 | 3 |
| 3. Access management | Q06, Q07, Q08, Q09 | R10, R13, R14 | 10 |
| 4. Data protection | Q10, Q11, Q12, Q13 | R16, R17 | 8 |
| 5. Asset management | Q14 | R24 | 1 |
| 6. Network management | Q15, Q16, Q17 | R06, R07, R09, R18, R19 | 5 |
| 7. Vulnerability management | Q18, Q19 | R01, R02, R03, R04, R08 | 2 |
| 8. Incident response | Q20, Q21, Q22 | R20, R21 | 7 |
| 9. Network-connected medical devices | Q23 | R11 | 1 |
| 10. Security oversight and governance | Q24, Q25 | R22, R23 | 4 |

No rule changes scoring category: existing administrative rules still contribute
no technical Exposure points. Rule IDs above include review-only paths; their
assignment does not make them confirmed. R03/R08 remain one OS-support group
within practice 7. R01/R02 remain the same CVE risk family, not two deductions.

Some assignments are deliberately broader project categories: R10 is placed with
access management; R03/R04/R08 with vulnerability management; R20 remains with
incident response despite its separate responsibility branch. Q24 remains wholly
in governance. These limitations must be visible in the explanation; do not
split existing combined questions or infer their separate answers.

## Safeguards per practice

S = 100 x earned applicable weight / available applicable weight, retaining exact
fractions. Reuse the existing weight registry. Yes earns full weight; No and
Unknown earn zero. Distinguish Unknown from No in status and follow-up details.
Q23 is excluded only when medical devices are explicitly No. Then practice 9 has
no applicable questions and shows Not applicable, not 0 or 100. Q24 counts once
using its derived combined answer; Q24a/b add no extra weight.

Per-practice denominators total 47 (46 with Q23 excluded); earned weights sum to
the global numerator. Never average the ten percentages to recreate the global
Safeguards score, because denominators differ.

## Exposure per practice

Take only confirmed technical groups assigned to the practice. Preserve the
existing group severity, entity multipliers and unresolved-condition notices.
Sum those group risk points for each scoring entity; apply the same 25-point cap
per entity within that practice. Use the FULL assessment scoring-entity count
for the size factor (20/N when N > 20, otherwise 1). Do not normalize by only
entities with findings or by an unproven practice-specific inventory subset.

E = max(0, 100 - sum(capped practice points) x size factor).
Per-practice caps are views of restricted findings; totals across practices do
not reconstruct the globally capped Exposure deduction. Never add or average
practice scores into the global score. Every view labels known deductions,
source coverage and its denominator.

### Availability

The current engine does not certify complete practice-specific technical coverage.
- No confirmed technical groups: Exposure is unassessed (null), not an automatic
  100. Administrative-only practices have no technical score under this model.
- One or more confirmed technical groups: show the calculated Exposure score as
  provisional known-deduction context; it does not imply all other assets/rules
  were checked or found safe. Include review counts and coverage warnings.
- A future assessed-zero state needs explicit positive assessment-coverage data
  before it can display 100. Absence of findings alone is insufficient.

## Combined practice result

Only if both S and E are numeric: use the existing 60/40 blend, exact-half-up
rounding and band thresholds. Apply a 69 ceiling only for confirmed Critical
findings assigned to THAT practice, including administrative Critical findings.
Do not apply a different practice's Critical ceiling to every practice.

If either component is unavailable, combined score/band are null. Show an
available Safeguards component with that exact label, not a renormalized combined
score. Show Not applicable only for a practice with no applicable questions and
no relevant confirmed/review evidence; otherwise explain the unavailable component.
A future chart must identify which metric its bars represent rather than mixing
Safeguards and combined numbers under one unlabeled scale.

All numeric combined practice results remain provisional under this draft and
current coverage/rule limits. No new thresholds, weights or safety claims arise.
This is an explicit bounded interpretation of the brief, not complete ten-practice
assessment coverage.

## Lakeview safeguard example

With the existing sample checklist (independent of scenario evidence mode):

| Practice | Earned / available | Safeguards |
| --- | --- | ---: |
| Email | 3 / 6 | 50.00 |
| Endpoint | 2 / 3 | 66.67 |
| Access | 10 / 10 | 100.00 |
| Data | 5 / 8 | 62.50 |
| Assets | 1 / 1 | 100.00 |
| Network | 0 / 5 | 0.00 |
| Vulnerability | 1 / 2 | 50.00 |
| Incident response | 7 / 7 | 100.00 |
| Medical devices | 1 / 1 | 100.00 |
| Governance | 4 / 4 | 100.00 |

These reproduce 34/47 globally, not a simple average. A 100 here means all mapped
applicable checklist answers were Yes, not independently verified practice maturity.

## Implementation acceptance checks

- Complete unique assignments for 25 questions and 24 rules; denominator sums.
- Exact per-practice arithmetic, Q23 exclusion, Unknown handling and Q24 single count.
- R03/R08 counted once; administrative findings excluded from Exposure.
- Fixed full-inventory normalization and zero-finding entity preservation.
- Missing technical evidence produces null, never a fabricated 100 or component blend.
- Per-practice caps and ceiling isolation, including confirmed Critical cases.
- JSON and readable exports preserve status, denominators and coverage explanations.
- Existing 65/82/80 scenarios and inventory-only Lakeview 80 remain unchanged.

Next: implement this versioned proposal as additive report data with explicit
Draft/provisional labels; verify those checks before connecting a chart.

## November 2 draft implementation

Implemented in clinicshield/practice_scoring.py as an additive `practice_scores`
report field (schema 1, mapping draft-v1). A collapsed Practice-area results
(draft) section and matching TXT section use a shared formatter. No chart is
added yet. Runtime assignments are explicit constants, not inferred from
framework-reference strings or uploaded files. The draft JSON table above
remains the reviewable mapping document.

Each component preserves numerator/denominator arithmetic. Exposure records
include group contributions, all inventory entities when numeric, pre/post-cap
points and full-inventory normalization. Coverage warnings and review counts
remain attached. Unavailable components are null; no component reweighting is
performed. Practice critical groups are isolated, and global scoring is unchanged.

Focused validation passed 60 tests before the final inventory-only regression
check was added. Browser/TXT manual verification and new CI are not yet claimed.
Independent rubric approval remains open; this is a labelled prototype.

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
