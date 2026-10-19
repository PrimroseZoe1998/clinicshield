# ClinicShield Gate 1 Review

Scheduled review October 16 2026.
Prepared by Primrose Mangwendeza.

## Progress

- Repository, MIT license, and pinned dependencies are in place.
- CSV and Excel inventory templates are available.
- Three fictional clinic datasets and expected findings are documented.
- All 25 checklist questions have draft framework mappings.
- Assigned framework reading is complete.
- Q17 now requires MFA for enabled remote access.
- Q24 has separate responsibility and risk-analysis follow-ups.
- An authorized Nmap fixture was captured in an isolated WSL lab.
- Typed schemas and in-memory CSV, JSON, Excel, Nmap XML, and checklist
  readers are implemented and connected.
- Inventory links, Q24 consistency, privacy headers, and input limits
  are validated.
- Upload limits, workbook hardening, explicit scan-to-asset mapping,
  and privacy-first header aliases are implemented and documented.
- The latest verified test suite contains 334 passing tests.
- Implementation pull requests #11–21 are merged; GitHub checks passed.

## Decisions requested

### Checklist mappings and weights

Review the proposed weights and partial mappings in
docs/framework-mappings.md.

Q03, Q05, Q09, Q22, and Q24 currently have proposed weight 1
where a direct Essential goal relationship remains unconfirmed.

Q04, Q12, Q16, Q18, and Q19 have proposed weight 3 based on
partial Essential relationships requiring review.

Approve final mappings and weights, or record required changes.

### Checklist interpretation

Confirm the corrected Q18 wording so Yes represents supported systems.

Confirm the Q17 MFA requirement and consistent interpretation in R07.

Confirm Q24 follow-ups are used separately for R20 and R22,
while the combined question is scored once.

Decide how Q23 should behave when no medical devices are present.

### Scoring boundaries

Confirm how cloud services and unmatched hosts contribute to
Exposure scoring and per-asset caps.

Confirm treatment of missing inventories and unknown exposure.

Confirm rounding and duplicate-evidence handling.

Sample score bands remain targets until the engine is implemented
and calibrated. Westside cannot exceed 69 with open Critical findings.

### Lab variation

The ARM64 Windows computer uses WSL network namespaces rather
than separate VirtualBox VMs.

Scanner and target have only the connected lab route, with no
default route. They share the Linux kernel and filesystem.

Confirm this benign service-testing setup meets the fixture requirement.

### Ingestion implementation choices

Review explicit aliases without fuzzy matching, the unsupported
ambiguous Hostname alias, and the IP address blocklist conflict.

Review the use of defusedxml instead of python-libnmap.

See docs/ingestion-review.md for remaining acceptance gaps.

### Ownership and handoff

Confirm repository transfer arrangements with ChiEAC before deployment.

## Next milestone

Core Week 2 ingestion and validation work is implemented ahead of schedule.

Next: review ingestion acceptance criteria and remaining edge cases,
then begin feed enrichment after the relevant Gate 1 decisions
are recorded.

## Decision record

Gate 1 was reviewed asynchronously by email on October 16, 2026.
Benjamin accepted the recommendations below. Acceptance does not mean
the corresponding code changes are already implemented.

| Topic | Decision | Reviewer | Date | Follow-up |
| --- | --- | --- | --- | --- |
| Mappings and weights | Accepted direct Essential mappings at weight 3; partial or uncertain mappings at weight 1. | Benjamin Drury by email | 2026-10-16 | Review every mapping and update final weights. |
| Checklist interpretation | Approved revised Q17, Q18, and separate Q24 follow-ups. Accepted Q23 exclusion only when no medical devices are explicitly confirmed. | Benjamin Drury by email | 2026-10-16 | Implement Q23 applicability and denominator adjustment; Unknown remains scored. |
| Scoring boundaries | Accepted separate cloud entities, provisional unmatched hosts, confirmed-only internet multiplier, and deduplication of the same finding on the same entity. | Benjamin Drury by email | 2026-10-16 | Document entity counting, caps, uncertainty, and deduplication; implement and calibrate. |
| Lab variation | Accepted WSL namespaces for the benign service-parsing fixture. | Benjamin Drury by email | 2026-10-16 | Retain documentation of shared kernel and filesystem. |
| Ingestion implementation | Accepted explicit aliases without fuzzy matching and defusedxml for Nmap parsing. | Benjamin Drury by email | 2026-10-16 | Maintain validation and malformed-input tests. |
| Repository ownership | No repository transfer required; repository remains under Primrose's account. | Benjamin Drury by email | 2026-10-16 | Update transfer references in project documents. |
| Branding and service rights | Confirmed the brief's existing ChiEAC name, branding, hosted-instance, and service-offering terms remain unchanged. | Benjamin Drury by email | 2026-10-18 | Retain ChiEAC credit and Primrose as lead developer. |
| Scope and fallback priorities | Accepted the fallback order and retained requirements in Primrose's confirmation email. | Benjamin Drury by email | 2026-10-18 | Apply the agreed fallback order if the schedule becomes tight. |
| Public repository link | Approved sharing the public repository link on LinkedIn and in Primrose's portfolio. | Benjamin Drury by email | 2026-10-18 | Public sharing is permitted. |