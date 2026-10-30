# Rule authoring guide

This guide describes the implemented 24-rule prototype. Rule definitions remain
 draft; source-checked framework links do not establish independent approval or
 compliance. See rule-framework-review.md and the dated Benjamin decision records.

## Catalog and execution

- `rules/R01.yaml` through `rules/R24.yaml` contain validated metadata.
- `clinicshield/rule_models.py` defines the schema; unknown fields are rejected.
- `clinicshield/rule_loader.py` reads one bounded YAML mapping (64 KiB maximum),
  rejects duplicate keys and aliases, and validates it with Pydantic.
- `clinicshield/rule_catalog.py` requires exactly 24 files, matching filenames,
  unique IDs R01 through R24, and exactly one callable handler registration each.
- `clinicshield/rule_engine.py` dispatches explicit (rule_id, handler, kind) keys.
  YAML does not execute arbitrary expressions or Python imports.
- `clinicshield/assessment_runner.py` connects validated inputs and evidence to
  handlers. Scoring and grouping are separate from finding generation.

## Change an existing rule

1. Define the trigger, non-trigger and uncertainty cases before changing code.
   Read the dated decision records so an older brief does not overwrite a later
   recorded decision.
2. Edit its YAML definition: schema_version, rule_id, title, kind, handler,
   description, severity, unknown_severity, evidence_fields, fix, owner, effort,
   cost, framework_references and review_status. Kind is technical or checklist;
   effort is 1, 2 or 3; cost is none, low, budget_required or unknown.
3. Implement the registered handler in the appropriate handler module. Return
   RuleObservation with the same rule ID, a stable entity ID, confirmed or
   needs_review status, and the required evidence fields; return None only for
   a justified non-trigger. Use existing typed evidence and freshness checks.
4. Keep confirmed risk separate from uncertainty. Missing versions must not
   invent CVE applicability. R24 reports unknown versions for software whose
   patient-information access is Y or Unknown; software marked N is excluded
   from R24, which does not establish safety. Unsupported matching logic must
   stay visible through review findings or coverage warnings.
5. Give each framework reference its framework, reference, source, rationale
   and pending/reviewed status. Preserve partial and conditional scope. Leave
   rule review_status draft until a rule review justifies changing it.
6. Add meaningful tests for positive, negative, unknown and conflicting evidence,
   missing/stale/future evidence where relevant, wrong registration and required
   evidence. Include grouping/scoring tests if the change affects deductions.
7. Re-run the relevant rule tests, catalog integration and all three fictional
   scenarios. Update samples/EXPECTED.md only with an explained decision.

## Add a rule beyond R24

Dropping an R25 YAML file into rules/ is deliberately rejected. Extending the
catalog requires changing the ID pattern in rule_models.py, the file count and
expected ID set in rule_catalog.py, and the catalog integration assertions.
Register the new handler in exactly one applicable registry; connect any new
input/evidence type and evaluation route in assessment_runner.py. Review scoring,
grouping, reports and Fix First behavior explicitly. Do not reuse an existing ID
for a different meaning without a documented migration.

## Verification commands

From the repository root in the project's virtual environment:

```powershell
python -m pytest tests/test_rule_loader.py tests/test_rule_models.py tests/test_rule_catalog.py tests/test_rule_catalog_integration.py -q
python -m pytest tests/test_samples.py tests/test_sample_evidence.py tests/test_assessment_runner.py tests/test_unknown_version_engine.py -q
```

Run the edited handler's tests too. If the environment cannot create its default
temporary directory, supply --basetemp with a new writable scratch directory.
Scenario evidence is fictional and opt-in; it must never be applied to real uploads.

## Week 3 intelligence limits

Normalization is conservative and does not imply fuzzy product identification.
KEV/EPSS membership or a cached NVD record alone does not establish applicability.
NVD uses an allowlist and reviewed mappings; complex configurations and version
ranges remain unresolved. Raw NVD content is preserved. Source-reported CVSS 3.1 base scores are
interpreted as context; other versions and score recalculation remain unsupported
(see cvss-context.md). Scheduled refreshes are configured; manually successful
runs do not prove scheduled execution. Artifacts currently expire after 30 days
and must be extracted locally rather than being committed to data/cache/.
