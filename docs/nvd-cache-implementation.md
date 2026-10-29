# Limited-CVE NVD cache

Implemented October 29, 2026. Source envelope and fields were checked against the
[official NVD API schema](https://csrc.nist.gov/schema/nvd/api/2.0/cve_api_json_2.0.schema)
and a [live CVE-2021-44228 API response](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2021-44228).
The developer-guide pages did not render in the web reader; a direct request to
the start-here page returned HTTP 403. The project retains its conservative
ten-second spacing, honors server Retry-After, and does not claim newly verified
published rate limits. Recheck the guide before expanding the list or adding keys.

## Scope and provenance

`config/nvd-allowlist.json` requires reviewed status, a review basis, unique valid
CVE IDs and at most 50 entries. The initial single ID, CVE-2021-44228, is a public
transport/configuration-preservation case for the R01/R02 path. Its selection does
not establish that any clinic uses affected software. The review basis records
the coding agent's source check, not independent stakeholder approval.

The list is repository configuration. Assessment uploads never select or initiate
downloads. Changing the list requires a separate repository review. Extra files
left from an older allowlist are ignored by assessments unless still allowlisted.

## Refresh command

```powershell
python -m clinicshield.refresh_feeds --cache-dir feed-output --status-file feed-output/refresh-status.json --nvd-allowlist config/nvd-allowlist.json --eol-product python --eol-product windows
```

The weekly/manual workflow now passes the NVD option. Snapshots are stored at
`feed-output/nvd/CVE-ID.json`. A new NVD row per CVE appears in the existing status
JSON and Actions summary. Failure makes the overall command fail without discarding
successful other feeds. An invalid allowlist sends no NVD requests. Empty scope is
explicitly skipped. The revised workflow has not yet run on GitHub.

The client makes sequential requests to a fixed HTTPS endpoint, without redirects
or an API key. Request starts are spaced by at least ten seconds, including retries
and transitions between IDs. There are at most three attempts per CVE, bounded
backoff, connection/read timeouts, a 4 MiB decompressed response limit and a shared
600-second NVD budget. HTTP 429/5xx and selected transient transport errors are
retryable; other HTTP errors fail immediately. Retry-After accepts seconds or an
HTTP date and also constrains the next CVE after exhausted retries. A delay beyond
the remaining budget stops requests rather than ignoring the server's delay.

## Cache validation and preservation

The cache validates the requested ID, fixed request URL, single-record API envelope,
required core fields, timestamps and size. It rejects duplicate JSON keys and
non-finite values. It preserves the complete parsed source response, including
unknown metadata, metrics, references, configurations, version bounds and logical
conditions. This is core-field validation and opaque source preservation, not a
claim to implement every field of the external JSON Schema.

Validated records are written atomically. Download, validation or replacement
failure preserves the prior cache; partial temporary files are cleaned up. Failed
refresh status does not make an old cache current. Assessments check cache age
separately. Per-run artifacts retain the source snapshots and status/log for 30 days.

## Offline assessments

With saved caches enabled, the app reports the allowlist scope, available count,
retrieval age, API-response age and whether analysis is available. No mapping means
no NVD applicability. Old CVE publication/modification dates are preserved as record
history; source freshness uses the API response timestamp, not the age of the CVE.
Offset-free NVD source timestamps are interpreted as UTC, as emitted by the live API.

Optional **Reviewed NVD software mappings (JSON)** associate an inventory software
row with a specific allowlisted CVE and simple CPE. Each item requires:

- `review_status`: `reviewed`, and a nonblank `review_basis`.
- `software_entry_id`: for example `software:1`, the first uploaded software row.
- `cve_id`: an ID in the repository allowlist.
- `vendor` and `product`: matching the supplied inventory using existing normalization.
- `cpe23`: an application CPE with explicit vendor, product and version, and wildcard
  remaining attributes, such as the synthetic `cpe:2.3:a:example_vendor:example_app:1.0:*:*:*:*:*:*:*`.

For a known inventory version, the mapped CPE version must match it. Unknown
inventory versions remain review items. The review assertion does not override
source freshness, source status or actual applicability evaluation. Conflicting
manual evidence for the same software/CVE is rejected instead of overwritten.

Only one unnegated OR configuration containing one OR node and one vulnerable,
explicit-version application CPE is interpreted. Source vendor/product CPE fields
must match the reviewed CPE identity. Exact source version mismatch is a nonmatch,
not proof of safety. Ranges, nested/multiple nodes, AND, negation, environment
dependencies, wildcard/escaped versions, platform-specific attributes and absent
configurations require review. The code never extracts version lists from prose.

Only analyzed records with supported configurations can be active evidence.
Rejected records never create active vulnerability findings. Missing analysis,
inconsistent record chronology, stale/future cache/response times and unknown
versions remain unresolved. Existing KEV/applicability/EPSS handlers still make the
finding and prioritization decisions. No network requests or cache writes occur
during assessment generation.

## Verification checkpoint

The original 65/82/80 scenarios are unchanged. A real public CVE-2021-44228 download,
atomic cache round trip and offline availability report passed locally. Lakeview
without scenario evidence remains 80/72.3/91.0 with that cache and no mapping.
This verifies public-record transport, not applicability to Lakeview.

Automated checks cover identity/size/schema failures, source preservation, retries,
spacing, Retry-After seconds/dates, budget exhaustion, prior-cache preservation,
reviewed mapping links, exact matches/nonmatches, unsupported configurations,
rejected/unknown/stale/future records, offline operation and end-to-end reports.
2,429 local tests passed excluding the known stalled AppTest file. The
high-severity Bandit check passed with no medium/high findings. No dependencies
changed.

The supplied browser screenshot shows one fresh allowlisted NVD record, no inferred
software applicability and scores of 80/72.3/91.0. The user confirmed the readable
download retains the available-record count and no-mapping/no-applicability notice.
This completes the exercised availability/no-mapping browser path. Manual mapping
upload cases and the revised GitHub refresh workflow remain unverified; automated
checks cover supported mappings, nonmatches and unsupported logic.
