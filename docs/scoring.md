# ClinicShield Scoring Rubric

ClinicShield reports a score from 0 to 100. Higher scores indicate
stronger reported safeguards and fewer detected technical exposures.

The score supports prioritization. It does not certify compliance,
measure the probability of a breach, or replace a formal risk analysis.

This document defines the initial rubric. Changes must include
a written reason and updated tests.

## Safeguards score


Question-level mappings and weights were reviewed on October 16,
2026. See docs/framework-mappings.md.

Weight 3:
Q01, Q02, Q06, Q07, Q08, Q10, Q11, Q17, Q20, Q21, Q25.

All remaining questions have weight 1.

Answers receive:
- Yes: the question's full weight.
- No: zero.
- Unknown: zero, with a follow-up action to establish the answer.

Q23 is excluded from both earned weight and total applicable weight
only when medical-device presence is explicitly No.
Yes, Unknown, and the default Unknown keep Q23 applicable.
Do not infer absence from an empty inventory.

Q24 is scored once using its combined answer.
Q24a and Q24b do not add separate scoring weight.

Safeguards score =
100 × earned applicable weight ÷ total applicable weight.

The denominator is 47 when all questions apply and 46 when
Q23 is excluded.

Keep full precision until calculating the final combined score.

## Question 18 correction

The project brief asks whether unsupported operating systems exist.
For that original wording, Yes indicates a problem.

The ClinicShield checklist instead asks:

"Are all devices running operating systems that still receive
security updates, including any valid extended support coverage?"

For this wording, Yes earns safeguards points.
No indicates unsupported systems.
Unknown earns no points and requires investigation.

Do not reuse the original question's answer interpretation.
Benjamin accepted this wording correction at Gate 1 on October 16, 2026.

## Finding severity points

| Severity | Points |
| --- | --- |
| Critical | 10 |
| High | 6 |
| Medium | 3 |
| Low | 1 |
| Info | 0 |

An informational finding about missing data is not evidence of safety.

## Technical finding multipliers

Apply these multipliers to technical findings only.

| Asset condition | Multiplier |
| --- | --- |
| touches_phi is Y or Unknown | 1.5 |
| Confirmed internet-facing | 1.5 |
| Network-connected medical device | 1.25 |

Applicable multipliers multiply together.

Finding risk points =
severity points × applicable multipliers.

The largest combined multiplier is 2.8125.
Keep that exact value during calculation; 2.81 is a display approximation.

Unknown internet exposure must remain visibly unresolved.
Do not label it internal or safe. The initial rubric applies the
internet multiplier only to confirmed exposure; review this policy
at the scoring gate.

## Exposure score

Scoring entities include inventory devices, grouped cloud services,
and provisional unmatched hosts.

- Each device has its own entity.
- Cloud rows share an entity when normalized vendor, product,
  and purpose match. Version differences do not create extra entities.
  Separate tenants cannot currently be distinguished by these fields.
- Unmatched services share an entity by normalized host, or by
  their asset ID when no host is supplied.
- Local software and explicitly linked services map to their device.
- Cloud and unmatched IDs are local to the current assessment.

For each entity:

1. Count each finding ID once.
2. Reject duplicate finding IDs with conflicting risk points.
3. Sum technical finding risk points.
4. Cap the entity total at 25 points.

Sum the capped totals across all entities, including entities with
no findings.

If there are more than 20 entities, multiply that total by
20 divided by the entity count.

Exposure score = maximum of 0 and (100 minus the adjusted total).

Unknown conditions remain recorded for explanations.
Unknown patient-data status receives the 1.5 multiplier.
Unknown internet exposure receives no internet multiplier.
Unknown medical-device status receives no medical-device multiplier
and remains flagged for review.

Checklist findings do not enter Exposure scoring.
They influence Safeguards scoring and the Critical ceiling.

The arithmetic functions and inventory mappings are implemented.
Automatic finding generation and complete assessment orchestration
remain pending. Missing data must not be presented as evidence of safety.

## Combined Cyber Safety Score

Raw combined score =
0.6 × Safeguards score + 0.4 × Exposure score.

Round the combined score to the nearest whole number.
Implemented tie rule: values ending in exactly .5 round upward.

If any open finding is Critical, cap the final score at 69.
This includes Critical technical findings and Critical checklist findings.

Show the uncapped score, the cap, and the findings responsible
in the explanation panel.

## Score bands

| Final score | Label |
| --- | --- |
| 85 to 100 | Good shape |
| 70 to 84 | Needs attention |
| 50 to 69 | At risk |
| 0 to 49 | Urgent |

## Worked example

Suppose an organization has 10 scoring entities and all 25
checklist questions apply.

Three weight-3 questions are answered No; all others are Yes.
The checklist earns 38 of the 47 available points.

Safeguards score = 100 × 38 ÷ 47 = approximately 80.8511.
The calculation retains the exact fraction.

A Critical technical finding affects a device that accesses patient
information and is confirmed internet-facing.

Finding risk = 10 × 1.5 × 1.5 = 22.5 points.

Assume all technical findings total 30 points after deduplication
and per-entity caps.

With 10 entities, no size adjustment applies.
Exposure score = 100 - 30 = 70.

Raw combined score =
0.6 × (3800 ÷ 47) + 0.4 × 70
= 3596 ÷ 47
= approximately 76.5106.

The rounded score is 77.
The open Critical finding caps the final score at 69.

Final result: 69, At risk.

The explanation must retain the raw score, rounded score,
Critical ceiling, and finding IDs responsible for the ceiling.

## Fix First ranking

Initial priority =
finding risk points ÷ effort value.

For checklist findings, use severity points without asset multipliers.

| Effort | Meaning |
| --- | --- |
| 1 | Under an hour and free |
| 2 | A day of work or a small cost |
| 3 | Vendor involvement, budget, or several weeks |

Break ties in this order:

1. A match in CISA's Known Exploited Vulnerabilities catalog.
2. An HHS Essential Cybersecurity Performance Goal.
3. An asset that accesses patient information.

Use the rule ID and asset ID as final tie-breakers for consistent output.

Group actions into:

- Do today free
- This month low cost
- Ask your vendor
- Policy and training

Explain that this initial ranking uses finding points, which may
differ from the actual score improvement because of asset caps,
overlapping findings, and the Critical ceiling.

## Implementation status and remaining work

Implemented and tested:
- Reviewed checklist weights and Q23 applicability.
- Technical severity points and condition multipliers.
- Device, cloud-service, and provisional unmatched-host mappings.
- Per-entity caps, duplicate-finding handling, and size adjustment.
- Combined scoring, upward rounding of exact .5 ties, score bands,
  and the Critical ceiling.

Remaining:
- Connect automatic finding generation to assessment scoring.
- Ensure every open Critical finding reaches the combined scorer.
- Preserve uncertainty and incomplete-data warnings in reports.
- Define practice-area score formulas and their denominators.
- Review ambiguous entity grouping and contradictory evidence.
- Implement Fix First ranking and duplicate-fix handling.
- Calibrate all three sample clinics against generated findings.

Westside's initial findings include Critical risks, so its initial
score cannot exceed 69. It may reach Needs attention after those
Critical findings are fixed.

## Q24 follow-up scoring and findings

Q24a records whether a named person is responsible for security.
Q24b records whether a recent documented risk analysis exists.

Derive Q24:
- Yes if both follow-ups are Yes.
- No if either follow-up is No.
- Unknown otherwise.

Use the combined Q24 answer for Safeguards scoring once.
The follow-ups do not add weight to the scoring denominator.

For findings:
- R20 uses Q20 for the incident plan and Q24a for security responsibility.
- R22 uses Q24b for the recent documented risk analysis.
- Unknown follow-ups require explicit uncertainty and follow-up actions.
- Never infer both missing controls from the combined Q24 answer alone.

Q24's reviewed weight is 1. The combined answer is scored once.
This policy was accepted at Gate 1 and must be included in
sample score calibration.