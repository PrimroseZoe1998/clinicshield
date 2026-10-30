# CVSS context from cached NVD records

Implemented October 30, 2026. `clinicshield/cvss.py` interprets source-reported
CVSS 3.1 base assessments from the cached NVD `cvssMetricV31` list. Every accepted
assessment retains its source, Primary/Secondary designation, version, score,
severity band and vector. Multiple sources are retained; no highest-score or
preferred-source selection is made.

Numeric scores must be finite numbers between 0 and 10 with at most one decimal
place; booleans and numeric strings are rejected. Source severity must match the
CVSS 3.1 band. Vector validation requires each base metric exactly once, validates
allowed values, accepts arbitrary metric order and optional temporal/environmental
metrics. The source score is NOT recalculated from the vector. This is a bounded
source-score interpretation, not a CVSS calculator or full NVD schema validator.

Missing metrics are unavailable, not zero. Malformed entries, unsupported families
(including v2, v3.0 and v4.0), and more than 100 assessments in a list are explicitly
marked for review; raw cached records remain preserved. Supported entries may
still be shown alongside review warnings about other entries.

The cache status messages display CVSS context even without a software mapping.
That display is catalog information only. With a reviewed mapping, the same
context is carried into R01/R02 evidence and the existing preview/TXT report.
Freshness and applicability remain separate checks. Critical source severity does
not make an unresolved finding confirmed, change ClinicShield rule severity,
change scoring weights, or establish exploitation probability or clinic risk.
No new network requests or dependencies are introduced during assessment.

Tests cover boundary bands, malformed/nonfinite scores, invalid/duplicate/missing
vector metrics, optional metrics, multiple sources, mutation preservation,
unsupported metric families, offline report propagation and unresolved applicability
with a Critical source score. Existing fictional scenario baselines remain tested.

Sources checked October 30, 2026:
- NVD API schema: https://csrc.nist.gov/schema/nvd/api/2.0/cve_api_json_2.0.schema
- FIRST CVSS 3.1 specification, sections 5 and 6:
  https://www.first.org/cvss/v3.1/specification-document

The NVD developer guide returned no readable text in the browsing tool; schema
and FIRST specification informed this implementation. Support for all CVSS versions
and score/vector arithmetic consistency remains outside this bounded step.

Validation: 2,465 tests passed on October 30, excluding the previously documented
locally stalled tests/test_app_preview.py file. The CI-equivalent high-severity
Bandit check passed (zero medium/high findings; five existing low findings).
Subsequent screenshots show live cached CVSS context and the user confirmed
it in the downloaded TXT. No new CI run is claimed.
