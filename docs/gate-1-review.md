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
- Typed schemas and in-memory CSV, Excel, Nmap XML, and checklist readers
  are implemented and connected.
- Inventory links, Q24 consistency, privacy headers, and input limits
  are validated.
- The latest verified test suite contains 239 passing tests.
- Implementation pull requests #11–18 are merged; GitHub checks passed.

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

### Ownership and handoff

Confirm repository transfer arrangements with ChiEAC before deployment.

## Next milestone

Core Week 2 ingestion and validation work is implemented ahead of schedule.

Next: review remaining ingestion gaps, including header aliases and
explicit scan-to-asset mapping, then begin feed enrichment after the
relevant Gate 1 decisions are recorded.

## Decision record

Complete during or after the review.

| Topic | Decision | Reviewer | Date | Follow-up |
| --- | --- | --- | --- | --- |
| Mappings and weights | Pending | | | |
| Checklist interpretation | Pending | | | |
| Scoring boundaries | Pending | | | |
| Lab variation | Pending | | | |
| Repository ownership | Pending | | | |