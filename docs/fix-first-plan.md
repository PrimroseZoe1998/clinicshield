# Fix First plan

The assessment preview and readable download now include a ranked action plan.
The plan is additive report metadata; it does not change any finding severity,
score formula, entity cap, evidence status or Critical ceiling.

## Numerators and effort

- Confirmed technical groups use the existing pre-cap technical risk points,
  including only the multipliers already assigned by the scorer.
- Confirmed administrative/checklist groups use severity points, with no asset
  multipliers and no extra Exposure or Safeguards deductions.
- A grouped action uses the highest effort of its confirmed occurrences (1–3).
- Priority is numerator divided by effort. Sorting uses exact fractions; display
  rounds the numeric priority for readability.

Tie order: confirmed applicable KEV membership, an existing reviewed Essential
question relationship, confirmed patient-information scope, rule IDs, entity ID,
then stable issue keys. R01 needs both `listed` KEV status and `match`
applicability to receive the KEV preference. EPSS does not override applicability
or this initial ranking formula; its existing context remains in detailed findings.

Essential ties use explicit No answers to the existing `ESSENTIAL_QUESTIONS`
registry. Confirmed inventory MFA gaps for R12/R13 use the already-reviewed Q01/Q07
relationships. An unrelated No in a combined question does not inherit another
question's Essential flag. These relationships are partial, not full CPG compliance.
Unknown or unsupported tie evidence receives no preference.

## Grouping and repeats

Existing same-risk grouping runs first, including R03/R08 as one OS-support action
with both sources preserved. Only confirmed occurrences contribute remediation
instructions, points and effort. Unresolved occurrences are listed separately even
when their group also has confirmed evidence.

Exact repeated recommendation sets on the same entity become one action card.
Their rule/issue IDs, owners and costs are retained; points and effort use their
respective maxima. Priorities are never summed. Distinct entities or distinct action
sets remain separate. The planner does not infer that different prose, an identical
owner or related router findings describe one universal fix. Detailed findings and
their evidence remain available below the plan.

## Action groups

Global ranks remain visible inside these views; group display order does not
change the global priority order:

- **Do today free:** effort 1 and every supplied cost is `none`.
- **This month low cost:** effort at most 2 and every supplied cost is `none`/`low`.
- **Ask your vendor:** other implementation actions, including unknown cost,
  budget-required work or effort 3. This is a request for an estimate and planning
  with the responsible IT/vendor role, not proof that a paid vendor is necessary.
- **Policy and training:** the explicit R17/R20/R21/R22/R23 agreement, governance,
  incident/reporting, risk-analysis and training actions. This routing takes
  precedence over cost/effort routing and does not assert that those actions are free.

Labels are planning buckets, not guaranteed completion dates or price quotes.

## Interpretation

Priority is not expected score gain. Caps, overlapping risks, inventory-size
adjustment and the Critical ceiling affect the effect of remediation. Confirmed
findings may still contain unknown scoring conditions; the detailed findings retain
those limitations. Verification items are not assigned confirmed remediation priority.

All plans remain scoped to supplied evidence. Sample plans are fictional.
Automated checks cover ranking, ties, duplicate sets, mixed evidence, costs,
grouped OS support and original 65/82/80 scores.

Verification: 2,379 local tests passed excluding the known stalled AppTest file.
The high-severity Bandit check passed with no medium/high findings.

## Manual checks completed October 29, 2026

The supplied Lakeview screenshot shows the Fix First plan, the four action-group
headings and R05 for LV-LT01 ranked first. The user confirmed:

- R05/LV-LT01 priority 4.5, using 9 points divided by effort 2.
- R03/R08 for LV-SRV01 appears once, priority 3, using 9 points divided by effort 3.
- The readable assessment includes those priorities, the grouped R03/R08 action
  and a separate Verify before planning remediation section.

These checks use fictional scenario evidence. They verify the exercised display
and download paths, not every ordering/cost boundary or real remediation outcomes.
