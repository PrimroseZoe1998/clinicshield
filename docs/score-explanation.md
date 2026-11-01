# Score explanation data

Added November 1, 2026 as the first Week 4 implementation step.

The scorer now attaches a versioned JSON-compatible arithmetic trail, exported
as `score_explanation` by `build_assessment_report`. Numbers retain exact integer
numerators and denominators alongside display values. The existing scoring
functions remain authoritative; weights, severities, thresholds and grouping
policies are unchanged.

Included:
- All 25 question IDs, submitted/derived answers, weights, earned and available
  weight; Q23 exclusions and Unknown answers remain explicit.
- Q24 contributes once; follow-up answers do not become extra weighted questions.
- Each confirmed technical risk group, its entity, contributing rule IDs, severity
  points, multipliers, exact risk points and unresolved scoring conditions.
- All scoring entities, including zero-deduction entities; totals before and
  after the 25-point cap; inventory-size factor and adjusted deduction.
- Safeguards/Exposure weights, exact raw combined score, rounding rule and result,
  confirmed Critical ceiling and responsible group IDs, final score and band.

A collapsed Why this score section appears in the app beneath the score warnings.
The TXT download includes the same explanation through a shared formatter.
No new persistence or network use is introduced. This explains arithmetic within
the assessed scope; missing evidence is not safety. Review-only technical items
add no confirmed Exposure deductions; administrative findings are not charged a
second time in Exposure. Scores remain provisional where evidence/rules require it.

Tests reconcile exported fractions and totals for all three clinics, verify an
isolated weighted-answer change, Q23 exclusion, Unknown answers, Q24 single count,
R03/R08 grouping, zero-point entities, a per-entity cap, and a binding Critical
ceiling. Synthetic cap/ceiling cases are test fixtures, not clinic observations.

Remaining Week 4 work includes vendor-ready action sentences, final rubric and
scope review, and the midpoint post. The original three-different-bands benchmark
must be reconciled with the later recorded decision to retain measured scenario
expectations; no score has been forced into a target band. Independent rubric
sign-off is not implied by this implementation.

Validation November 1: 2,476 tests passed excluding the known locally stalled
Streamlit AppTest file. High-severity Bandit check passed (zero medium/high,
five existing low findings). Browser verification of the new expander remains
the next manual check; no new CI run is claimed.
