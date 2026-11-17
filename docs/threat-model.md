# ClinicShield Threat Model

Status: Initial review October 19; implementation review added November 16, 2026.
Scope: Ingestion readers and the implemented guided assessment application.

## November 16 implementation update

The application now scores validated records and displays findings, provisional
scores, coverage warnings and a Fix First heuristic. It offers in-memory PDF,
CSV, JSON and text downloads. CSV formula neutralization, session-state helpers,
source-change reset behavior and safe upload errors have tests. These replace
the planned/future status in the original review below; remaining-work entries
in that historical table are not a current completion checklist.

The focused upload/privacy/state run passed 141 tests. See
[Week 6 status](status/week-6.md) for its exact scope and follow-up work.
Existing guards cover selected filesystem and temporary-file APIs during
ingestion, Python logging and captured terminal output. They do not establish
host-wide persistence or retention guarantees.

The public cache-folder text field and the scope of the privacy notice require
hardening. Community Cloud package and usage-statistics overrides were observed
on November 10; see [hosted runtime review](hosted-runtime-review.md). No new
provider-policy verification was performed for this code review. Continue using
fictional inputs. Framework mappings remain provisional and sample benchmarks
are demonstrations, not independent effectiveness validation.

## Original October 19 review (historical)

## Assets to protect

- Uploaded inventories and checklist answers.
- Infrastructure details, including hosts and software versions.
- Assessment results and their integrity.
- Application availability.
- Repository code, dependencies, and deployment credentials.

## Data flow and trust boundaries

1. A user supplies an inventory, checklist, or existing Nmap file.
2. Untrusted bytes enter the ingestion readers.
3. Readers validate content and produce in-memory records.
4. Planned scoring and reporting consume validated records.
5. A future UI displays results and offers exports.

Uploaded content remains untrusted after parsing. Validation
does not make text safe for HTML, spreadsheets, logs, or URLs.

Hosting, browser sessions, external feeds, and exports introduce
additional boundaries that must be reviewed before deployment.

## Threats and controls

| Threat | Current controls | Remaining work |
| --- | --- | --- |
| Sensitive data in uploads | Prohibited-header checks and safe validation messages | Values may still contain sensitive information; review UI guidance and deployment data handling. |
| Uploaded data saved or logged | In-memory readers; runtime tests guard builtins.open and io.open and check logs and terminal output | Verify other filesystem APIs, temporary files, hosting logs, and UI behavior. |
| Malformed or oversized input | Format validation; upload, row, column, cell, and workbook archive limits | Extend malformed-file tests and enforce combined assessment limits. |
| XML entity attacks | Nmap parsing uses defusedxml; entity rejection tests exist | Retain regression tests and review parser updates. |
| Unauthorized scanning | Application parses existing scans and requires authorization confirmation | Preserve the no-scan-execution boundary. |
| Misleading assessment results | Typed records, link validation, and documented scoring decisions | Implement and test scoring, uncertainty handling, deduplication, and sample calibration. |
| HTML or spreadsheet injection | No completed UI or export security verification | Escape displayed text and handle spreadsheet formula injection before exports ship. |
| Cross-user data disclosure | No completed hosted-session verification | Review session isolation, caches, cleanup, and concurrent-user behavior. |
| Unintended outbound requests | External enrichment is planned | Prevent uploaded values from selecting arbitrary request destinations; review timeouts and data sent externally. |
| Dependency compromise | Dependencies are pinned and checks run in CI | Review dependency advisories and updates; protect repository and deployment secrets. |

## Verification evidence

The full suite passed 342 tests on October 19, 2026.

Eight runtime privacy cases exercise successful and rejected
CSV, JSON, Excel, and Nmap inputs. They check two file-access
functions, Python log records, and captured terminal output
during parsing.

This is bounded evidence, not proof that every input path,
filesystem API, operating-system mechanism, or deployment
configuration prevents persistence or disclosure.

## Before deployment

- Complete remaining ingestion acceptance checks.
- Verify session isolation and runtime data handling.
- Review hosting logs, caches, temporary files, and error traces.
- Verify safe UI rendering and exports.
- Review external feed requests and failure behavior.
- Validate scoring and sample expectations.
- Confirm a working private vulnerability-reporting channel.
- Review this model whenever a new data boundary is introduced.
