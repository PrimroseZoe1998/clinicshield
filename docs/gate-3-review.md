# Gate 3 review package

Prepared November 16, 2026. **Draft: review pending; Week 6 remains In Progress.**
Planned Gate 3: Friday November 20, per the original project brief.
No message has been sent, approval recorded or release tag created by this file.

## Proposed checkpoint

Review ClinicShield as a fictional-data prototype release candidate, not as a
production service, clinical security validation or compliance certification.
The hosted demonstration is available at
https://clinicshield-uggyfds2f9etx6qo2qelpx.streamlit.app/.
No real clinic inventories, patient information or credentials are authorized
for this pilot. Previously approved scoring remains unchanged.

## Implemented and exercised

| Area | Evidence | Limits |
| --- | --- | --- |
| Guided checkup and reports | Five screens, fictional examples, PDF/CSV/JSON/text exports; 65/82/80 scenario regressions | Scores provisional; synthetic remediation is not completed work |
| Week 6 cache restriction | Browser path field removed; evaluation ignores stale path values and uses repository data/cache | Operator Python APIs retain directory parameters; server setup remains trusted |
| Rejected inputs and reset | Report invalidation on validation failure; replacement/removal and reset regressions; owner confirmed hosted CSV rejection, valid replacement and empty reset fields | Hosted observation covers these exercised paths, not every format or malicious payload |
| Security checkpoint | 2,579 local tests; Bandit zero High/Medium, eight reviewed Low findings; 77 pinned packages audited with zero known advisories/skips; pip check passed | November 16 source checkpoint, not final tagged artifact; dependency audit fallback and host version drift documented |
| Pilot | One Week 6 attempt reported as four minutes, no assistance, no problems reported | Brief requires 3–5 testers; first-time status and direct comprehension answers unconfirmed |
| Accessibility | Owner confirmed keyboard-only Lakeview journey through score explanation and PDF download, visible focus and no traps; Start, Results and Fix First readable/reachable at 200% zoom | Exercised paths only; not full screen-reader, contrast, WCAG or universal reading-level validation |

Detailed evidence: [Week 6 status](status/week-6.md), [verification](week-6-verification.md),
[pilot report](pilot.md), [readability review](readability-review.md).

## Upload, runtime and reporting boundary review

Code limits in `clinicshield/input_limits.py`: 10 MiB per general upload, 20 MiB
combined assessment uploads, 64 KiB for checklist/follow-up JSON, 10,000 inventory
rows, 50 columns and 10,000 characters per cell. Workbooks also limit decompressed
content to 50 MiB, 1,000 archive members and 20 sheets. Reader-specific limits and
aggregate entry-point tests exist; browser extension filters are not the sole
content validation. Existing Nmap parsing requires authorization and does not
execute scans. Some application paths read trusted static rules/templates/caches;
no-persistence evidence must not be described as no filesystem activity.

Runtime privacy tests guard selected file/temporary-file functions, logging and
terminal output during ingestion. Assessment evaluation tests also guard writes
and network requests. State checks establish report invalidation and reset in
exercised flows. They do not prove memory erasure, provider upload-manager
cleanup, full worker isolation, host logs/temp-file behavior or retention.
Downloads intentionally create user-device copies. The revised UI states these
limits and requires fictional data.

[Threat model](threat-model.md) now separates current implementation review from
the historical October review. [SECURITY.md](../SECURITY.md) has the
owner-authorized private reporting contact and no invented response SLA.
Mail delivery has not been independently tested. Neither a privacy audit nor
an external security assessment has been completed by these checks.

## Open limitations to discuss, not silently close

- Community Cloud retention/log/temp-file guarantees and comprehensive session
  isolation are unverified. Host-enabled usage statistics and PyArrow/Certifi
  drift were observed in November; local pins are not a hosted runtime manifest.
  See [hosted runtime review](hosted-runtime-review.md).
- Framework relationships remain partial/draft. Week 3's reviewed-reference
  task remains open; prototype acceptance does not validate those mappings.
- CI container checks do not replace the separate clean-machine local Docker
  verification requested by the brief, which remains unperformed.
- Raw evidence, identifiers and formal source names are outside the selected
  prose screening target; direct comprehension feedback is still pending.
- Committed sample PDFs are untagged and have no document language or embedded
  URI link annotations. Owner copy/layout/link checks do not establish semantic
  reading order or screen-reader support. Decide tagged-PDF scope explicitly;
  see [contrast/PDF review](contrast-review.md). No accessibility exception has
  been accepted by this document.
- A known-advisory scan is time-bound. Bandit's reviewed Low findings remain
  visible; no suppressions or dependency pin changes were used to obtain a pass.

## Completion and decision record

Before proposing the final tag:

- [ ] Record at least three distinct Week 6 pilot testers, including failures,
  assistance, first-time status and actual comprehension responses.
- [ ] Review feedback and any required fixes/retests; retain explicit limits
  where additional accessibility coverage is deferred.
- [ ] Confirm final intended source revision and fresh CI/test/audit results;
  keep local/hosted environment differences explicit.
- [ ] Review the fictional-only release scope and outstanding limitations at
  Gate 3; record Benjamin's actual response and the owner's interpretation
  accurately, without fabricating item-by-item validation.
- [ ] Finalize [release notes](release-notes-v1.0-rc.md), create the approved
  v1.0-rc tag at the reviewed revision, and record its SHA and date.

Reviewer response: pending.
Accepted scope/limitations or requested changes: pending.
Final source SHA, CI evidence and tag: pending.

The package is prepared for review now. It does not close Week 6, approve a
release or count outstanding testers as completed.


PDF follow-up: language metadata and embedded single-source web links are now
implemented and checked (14 PDF tests; regenerated three synthetic samples).
Semantic tags, reading order and screen-reader validation remain pending;
the earlier missing-language/link observation is superseded by this change.
