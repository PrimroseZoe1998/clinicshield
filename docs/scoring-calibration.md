# Week 3 scoring calibration

## Verified baseline on October 28 2026

All examples are fictional and all scores remain provisional.

| Clinic | Safeguards | Exposure | Overall | Current band |
| --- | ---: | ---: | ---: | --- |
| Lakeview Family Dental | 72.34 | 55.00 | 65 | At risk |
| Southside Counseling Collective | 70.21 | 100.00 | 82 | Needs attention |
| Westside Community Health | 80.85 | 78.68 | 80 | Needs attention |

These results use the documented fictional scenario evidence.
They do not establish real vendor support status or CVE applicability.

## Differences from earlier expectations

Earlier sample documentation proposed:
- Lakeview: Urgent, 0–49.
- Southside: At risk, 50–69.
- Westside: At risk, 50–69 before remediation.

These earlier targets are superseded by the measured scenario baselines above.
On October 29, 2026, the user reported Benjamin's agreement to retain the current
model and revise the earlier expected bands. See
`benjamin-decisions-2026-10-29.md` for the decision and its scope.
No evidence, severity, formula or global band threshold was changed to force a target.

## Current scoring behavior

- Overall uses the existing 60% Safeguards / 40% Exposure formula.
- Unsupported operating systems use High severity.
- Unknown evidence remains informational.
- No Critical finding is invented to impose a score ceiling.
- R03 and R08 share the same asset OS-support contribution.
- Administrative findings do not add Exposure deductions.
- Checklist answers are scored once.
- Missing coverage and conflicting evidence remain visible.

## Interpretation and limitations

Southside's Exposure score of 100 means no confirmed technical
risk points were assigned within the assessed scope. It does not
mean the clinic is safe: service coverage is missing, application
versions are unknown, and administrative gaps remain.

The blend of checklist scoring, technical risk points, entity caps,
and inventory-size adjustment can produce higher overall scores
than the earlier qualitative sample expectations.

Decision: retain the current model for the prototype and use the measured sample
expectations. This resolves the earlier sample-band decision, not empirical
validation of risk prediction or review of every severity/framework reference.
Future formula or classification changes require justification and regression tests.

## Manual verification

- Lakeview fictional scenario displays 65 overall, 72.3 Safeguards,
  and 55 Exposure in the preview.
- R03/R08 retains both evidence sources with one 9-point contribution.
- Downloaded reports retain the fictional-scenario notice.
- Scores remain labeled provisional.

## Remaining limitations

- Saved KEV/EPSS and explicitly mapped lifecycle caches are now connected;
  freshness and missing coverage remain visible.
- No real CVE applicability is asserted for fictional sample products.
- The October 29 source check adds partial CSF 2.0 and selected CIS v8.1
  rule mappings; see `rule-framework-review.md`. Rule definitions remain draft,
  and independent review/additional framework families are not implied.
- CSV, JSON and XLSX upload integration is implemented and manually exercised
  with fictional files. Real clinic data has not been verified.
- NVD ingestion and comprehensive source coverage remain out of scope of these tests.

## Historical follow-up for Benjamin (sent before the decision)

Share the labeled example report with:
- The current score and component explanation.
- Findings, supporting evidence, and recommended actions.
- Coverage and unresolved-data warnings.
- This comparison with the earlier proposed target bands.
