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

Those target bands are not currently achieved. Do not describe
calibration as complete or change evidence to force those outcomes.

## Current scoring behavior

- Overall uses the existing 60% Safeguards / 40% Exposure formula.
- Unsupported operating systems use High severity.
- Unknown evidence remains informational.
- No Critical finding is invented to impose a score ceiling.
- R03 and R08 share the same asset OS-support contribution.
- Administrative findings do not add Exposure deductions.
- Checklist answers are scored once.
- Missing coverage and conflicting evidence remain visible.

## Interpretation requiring review

Southside's Exposure score of 100 means no confirmed technical
risk points were assigned within the assessed scope. It does not
mean the clinic is safe: service coverage is missing, application
versions are unknown, and administrative gaps remain.

The blend of checklist scoring, technical risk points, entity caps,
and inventory-size adjustment can produce higher overall scores
than the earlier qualitative sample expectations.

Review whether the earlier target bands should be revised or the
scoring model should change. Any formula or classification change
must be documented, justified, and regression tested.

## Manual verification

- Lakeview fictional scenario displays 65 overall, 72.3 Safeguards,
  and 55 Exposure in the preview.
- R03/R08 retains both evidence sources with one 9-point contribution.
- Downloaded reports retain the fictional-scenario notice.
- Scores remain labeled provisional.

## Remaining limitations

- The preview does not load live intelligence caches.
- No real CVE applicability is asserted for fictional sample products.
- Full framework mapping validation remains pending.
- Real-upload and expanded source integration remain unfinished.

## Follow-up for Benjamin

Share the labeled example report with:
- The current score and component explanation.
- Findings, supporting evidence, and recommended actions.
- Coverage and unresolved-data warnings.
- This comparison with the earlier proposed target bands.