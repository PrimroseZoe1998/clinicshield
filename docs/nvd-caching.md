# NVD scope and caching strategy

Status: implementation plan, not completed functionality.

## Initial scope

- Use the NVD CVE API 2.0.
- Fetch only CVE IDs from a reviewed repository allowlist.
- Start with CVEs needed by implemented starter rules.
- Limit the initial allowlist to 50 unique CVE IDs.
- Do not mirror the full NVD database.
- Do not automatically fetch every KEV entry.
- Report that coverage is limited to the allowlist.

## Privacy and offline operation

- Refresh public data separately from assessments.
- Never send uploaded inventories, hostnames, asset IDs, or patient
  information to NVD.
- Assessments read local caches without network requests.
- Select the allowlist independently of uploaded assessment data.

## Cache contents

Preserve each complete source CVE record, including:
- CVE ID, source identifier, and vulnerability status.
- Publication and last-modified timestamps.
- Descriptions, references, metrics, and configurations.
- CPE criteria, vulnerable flags, logical operators, negation,
  and version bounds.

Also record the request URL, retrieval timestamp, and cache
schema version.

Do not flatten configurations into product-name matches.

## Refresh policy

- Refresh the reviewed allowlist weekly and on manual request.
- Run requests sequentially, at least 10 seconds apart.
- Apply the same spacing to retry attempts.
- Use connection/read timeouts and response-size limits.
- Allow at most three attempts per CVE.
- Respect Retry-After; stop if it exceeds the run's time budget.
- Use bounded backoff for transient network errors, HTTP 429,
  and HTTP 5xx responses.
- Do not retry other HTTP errors automatically.
- Validate the returned CVE ID before replacing its cache.
- Reject empty or mismatched responses as refresh failures.
- Replace each validated cache atomically.
- Preserve the previous cache when a refresh fails.
- Record failures and return a nonzero workflow exit code.

Recheck NVD's current usage guidance before implementation.

## Assessment behavior

- Missing or invalid cache: report unavailable coverage.
- Retrieval age over eight days: report stale coverage.
- Future retrieval timestamp: require review.
- Missing analysis or configurations: require review.
- Rejected CVE: do not generate an active vulnerability finding.
- Unsupported version or configuration logic: require review.
- Product-name similarity alone never confirms vulnerability.
- A nonmatch never establishes that a product is safe.

The eight-day threshold is a project policy for weekly refreshes,
not a guarantee that NVD content is complete or current.

## Implementation acceptance checks

- Validate allowlist IDs, duplicates, and size.
- Test response identity and source-data preservation.
- Test throttling, retries, size limits, and failure reporting.
- Test preservation of the previous cache after refresh failure.
- Test offline assessment behavior and coverage warnings.
- Test supported applicability logic and cases that must not match.

## References

- https://nvd.nist.gov/developers/vulnerabilities
- https://nvd.nist.gov/developers/start-here
- https://nvd.nist.gov/vuln/Vulnerability-Detail-Pages