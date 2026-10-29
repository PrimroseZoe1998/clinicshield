# Reviewed evidence inputs

The example preview accepts two optional JSON uploads when synthetic scenario
evidence is off. Uploaded evidence is parsed in memory, with a 64 KiB limit per
file. Unknown fields, duplicate associations and references to absent inventory
entries are rejected. Review labels are supplied assertions, not independent
verification by ClinicShield.

## Lifecycle mappings

Enable saved public-feed caches, choose the cache folder, and upload a JSON list:

```json
[
  {
    "asset_id": "YOUR-ASSET-ID",
    "review_status": "reviewed",
    "mapping": {
      "os_name": "Example OS",
      "os_version": "1.0",
      "product": "example-os",
      "release_name": "1",
      "mapping_basis": "Describe the source and review supporting this exact mapping."
    }
  }
]
```

This is a format illustration, not a real mapping. OS and version must match the
inventory using the existing normalization rules; product and release must match
the saved `eol-example-os.json` snapshot. No prefix matching or version inference
occurs. Product slugs cannot contain path separators. Missing or malformed feeds,
missing releases and unmatched mappings remain unassessed. Retrieval and source
freshness are displayed in the preview and readable download.

Extended-support coverage remains unknown. A lifecycle feed alone cannot establish
whether an asset has additional support coverage. Existing rule handlers continue
to require that evidence before confirming unsupported-system findings.

## CVE applicability

Upload a JSON list of reviewed source records. Each item has:

- `review_status`: `reviewed`.
- `review_basis`: nonblank explanation of the source comparison.
- `evidence`: the existing `VulnerabilityEvidence` schema.

Within `evidence`, supply `software_entry_id` (`software:1` refers to the first
software inventory row), `record_status` (`active`, `rejected`, or `unknown`),
`source_generated_at` (timezone-aware timestamp or null), and `record`.
The record requires `vulnerability_id` (CVE ID), `source`, `source_url`,
`retrieved_at` (timezone-aware), `vendor`, `product`, `version_rule` (`exact`
or `unsupported`), `affected_versions` (list), and optional `version_evidence`.

Use `exact` only for source-supported exact affected-version lists. Unsupported
range interpretation remains subject to review. Review basis is retained alongside
version evidence in finding details. Existing matchers still check vendor, product,
version, record status and timestamps. A review label cannot override an unresolved
match. KEV membership and EPSS scores never establish applicability.

Uploads cannot replace existing scenario evidence. Original fictional scenario
scores and notices remain unchanged. This interface still evaluates fictional
inventories; real inventory upload integration is the next step.

## Validation

October 29, 2026: 191 focused lifecycle, applicability, assessment, report,
vulnerability routing and enrichment tests passed. Direct example-to-report checks verified missing-feed warnings and the
unchanged Lakeview synthetic score of 65.

Pre-commit verification: 2,330 tests passed with `tests/test_app_preview.py`
excluded. The attempted full run stalled in Streamlit AppTest while Python was
creating its asyncio socket pair (`socket.accept`), and was interrupted. Automated
UI tests are therefore not claimed as passing. `git diff --check` passed.

Manual verification completed on October 29, 2026:

- Original Lakeview synthetic scenario still displays 65 overall, 72.3 Safeguards
  and 55 Exposure.
- Missing KEV and EPSS cache warnings appear in the preview and readable download.
- A synthetic LV-WS01 lifecycle mapping loads with fresh retrieval/source status;
  extended-support coverage remains unknown and other assets remain unassessed.
  The mapped-evidence message is preserved in the download.
- Uploaded synthetic CVE evidence for LV-SRV01 retains its Unknown inventory
  version, `needs_review` applicability, synthetic notice, and both version-review
  and missing-KEV explanations. The explanation is preserved in the download.

These checks verify the exercised paths, not every interactive input or a real
vendor support/CVE assertion. Synthetic manual fixtures remain outside the repository.
