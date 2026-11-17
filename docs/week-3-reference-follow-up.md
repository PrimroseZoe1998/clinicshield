# Week 3 reference follow-up

Reviewed November 16, 2026. Status: metadata audit and targeted citation
corrections complete; full rule approval and literal all-framework conformance
are not claimed. This does not close issue #5 automatically.

## Catalog audit

All 24 typed rule definitions contain evidence fields, severity, fix, owner,
effort and cost. There are 24 NIST references, 22 CIS references, 25 HICP
references (R16 includes a Volume 2 supplement), 24 HIPAA supporting references
and 18 HHS goal relationships. Each existing reference has source, rationale and
source-review status. All 24 rule-level statuses remain draft.

The source-review label means a bounded project interpretation, not publisher
endorsement or validation of the whole rule. Metadata presence does not approve
severity, trigger completeness or clinical risk prediction. Week 4 approval of
prototype policies does not resolve every framework relationship.

## Official-source follow-up

Compared selected relationships and locators with:

- [HICP 2023 Volume 1](https://hhscyber.hhs.gov/Documents/HICP/tech-vol1-508.pdf):
  R17 now cites the general vendor-selection discussion, printed pp. 5–6, rather
  than relying on the narrower cloud-backup example. R20 separates incident
  planning p. 27 from governance pp. 31–32. The healthcare review table now
  matches existing YAML ranges for R11 (24, 30) and R18 (24–25).
- [CIS Navigator v8.1](https://www.cisecurity.org/controls/CIS-controls-navigator):
  selected vulnerability, default-account and supplier-contract relationships
  remain partial; the rules do not demonstrate full safeguard attainment.
- [HHS CPGs](https://hhscyber.hhs.gov/cybersecurity-performance-goals.html):
  retained conditional Internet-accessibility scope for vulnerability/MFA
  relationships; no new goal mapping was forced.
- [164.308](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.308),
  [164.312](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.312)
  and [164.314](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.314):
  retain supporting-only relationships and Required/Addressable distinctions.
  Authentication text does not itself prescribe the project's MFA method.

This is a targeted recheck, not a new exhaustive review of all 113 references.
NIST's PDF fetch timed out twice; no fresh NIST source-check date is asserted.
Unchanged references retain their October 29/30 review provenance. Text extraction
was available for HICP; PDF screenshot attempts were not reliably returned, so
this step does not assert complete visual page verification.

Only R17/R20 HICP reference fields changed in YAML. Rule triggers, descriptions,
severity, fix text, owner, effort, cost and review status must remain unchanged.
The [healthcare review](healthcare-rule-review.md) table is corrected in place;
this note supersedes its historical locators for those rows.

## What remains open

- Six direct HHS mappings (R03/R04/R05/R06/R08/R22) and two CIS mappings
  (R14/R22) remain deliberate omissions. Existing limits are explained in the
  healthcare and NIST/CIS review notes; absence is not a pending invented ID.
- Keep independent rule validation separate from source-checked partial links.
  Do not upgrade draft rules or claim compliance to finish a checkbox.
- A literal requirement for every rule to cover every framework still needs
  explicit scope disposition; citations cannot supply missing assessment scope.
- Issue #5 also retains other documented differences, including scheduled-feed
  observation and manual artifact synchronization. This reference work does
  not establish those outcomes.

The checkbox's metadata fields are present, but if it means complete rule and
framework validation, keep it open with this evidence linked. Completing a
source-checked prototype catalog and independently validating its effectiveness
are distinct decisions.

## Verification

151 focused tests passed: framework review, catalog/models/loader/integration,
CSV/JSON report exports and PDF generation. Scenario regressions remain 65/82/80
and provisional. Download text retains the revised R17/R20 locators. A structured
comparison with the pre-change YAML confirms only framework reference metadata
changed, in R17 and R20. All 24 rule metadata checks passed (113 references).
Medium/high Bandit and diff checks passed. No new full-suite run, independently
approved mapping, fresh NIST review or final Week 3 acceptance is claimed.
