# Week 4 prototype scope acceptance

Recorded November 3, 2026 from Benjamin's reply pasted by the user. The original
message timestamp and email were not independently retrieved. This records
stakeholder acceptance, not an independent technical validation.

## Accepted decisions

- [x] Retain Lakeview 65, Southside 82 and Westside 80. The two-band outcome
  is an approved deviation from the original three-band benchmark; the original
  benchmark was not met as written.
- [x] Retain documented severity, scoring-entity grouping and uncertainty policies,
  with their limitations visible. Unresolved framework mappings remain unresolved
  and must not be represented as validated or publisher-endorsed.
- [x] Retain finding points divided by effort as the Fix First heuristic.
  It predicts neither score improvement nor actual risk reduction; caps,
  overlap and ceilings can change the effect of an action on a score.
- [x] Accept draft practice mappings and denominators for the prototype.
  Missing technical evidence stays unassessed. Compute a combined practice score
  only when both components are available. Do not sum practice scores into the
  global score or treat the mappings as an official crosswalk.
- [x] Accept fictional Westside 80 → 99 for demonstration only. The original
  At risk → Needs attention target is an accepted benchmark deviation; the
  retained model produces Needs attention → Good shape for the declared inputs.

No further scoring-model changes were requested.

## Conditions retained in the documentation

Scores remain provisional. Missing support/version/default-password evidence and
KEV/EPSS/applicability coverage remain limitations, not evidence of safety.
Westside retains seven coverage issues and 79 post-fix review groups. Its
Exposure 100 means no confirmed deduction in the supplied synthetic scope;
it does not demonstrate complete coverage or verified security improvement.

The synthetic changes in [the Westside comparison](westside-post-fix-verification.md)
are simulated remediation assumptions. No completed corrective actions, restore
tests, migrations, encryption deployment or real clinic security improvement are
established by this fixture. The original sample is preserved.

Acceptance covers the documented prototype scope only. It does not independently
validate clinical cybersecurity effectiveness, regulatory compliance or production
readiness. Existing framework-reference review gaps remain open.

## Closeout and next milestone

- [x] Record approval and approved benchmark deviations.
- [x] Preserve provisional scoring, unresolved evidence and coverage warnings.
- [x] Distinguish simulated remediation from completed corrective actions.
- [x] Prepare [Week 5 development plan](week-5-plan.md).
- [ ] User publishes midpoint LinkedIn post (planned November 6).

Week 4 technical/documentation scope is accepted. Full checklist closure still
requires publication confirmation. Latest recorded implementation checkpoint is
e321e06, with green GitHub checks reported by the user. Latest recorded local run
is 2,504 passing tests with the known stalled Streamlit AppTest file excluded;
Bandit reported zero medium/high and five existing low findings. These historical
results are not new validation runs for this documentation update.
