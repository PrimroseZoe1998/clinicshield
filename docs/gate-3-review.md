# Gate 3 review package

Prepared November 16, 2026. **Gate 3 conditions met. Week 6 closed November 19, 2026.**
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
| Pilot | Three owner-reported fictional sessions, about 4, 2 and 2 minutes, no help or reported problems; anonymized comprehension responses supplied | First-time status unknown |
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
  prose screening target. The owner supplied anonymized comprehension
  responses on November 18.
- The owner required semantic PDF tags and verified screen-reader reading order
  before v1.0-rc. All three sample PDFs were refreshed with tags. See the
  [PDF verification record](pdf-report.md) for the sampled Narrator walkthrough.
- A known-advisory scan is time-bound. Bandit's reviewed Low findings remain
  visible; no suppressions or dependency pin changes were used to obtain a pass.

## Completion and decision record

Before proposing the final tag:

- [x] Record three owner-reported Week 6 pilot testers with timing, assistance and reported problems.
- [x] Owner confirmed P02/P03 used fictional clinic examples.
- [x] Record the owner-supplied anonymized comprehension responses.
- [ ] Confirm first-time status if available.
- [ ] Review feedback and any required fixes/retests; retain explicit limits
  where additional accessibility coverage is deferred.
- [x] Implement semantic PDF tags and inspect the generated structure locally.
- [x] Complete the sampled screen-reader walkthrough of the owner summary,
  appendix transition and source link. Refresh all three release sample PDFs.
- [x] Confirm the reviewed application revision and its passing CI runs.
- [x] Record Benjamin's conditional approval of the fictional-data demo.
- [x] Prominently disclose the release scope and limitations in the draft notes.
- [x] Document the [local Docker verification](docker.md#november-18-local-docker-walkthrough).
- [x] Record Benjamin's deferral and the owner's decision to accept the Docker run.
- [x] Finalize [release notes](release-notes-v1.0-rc.md) and create the local
  v1.0-rc tag at the reviewed application revision.
- [x] Verify the tag and closeout documentation on GitHub.

### Benjamin's decision

> I approve Gate 3 with conditions for the fictional-data prototype demonstration and proposed v1.0-rc release.

Before tagging, Benjamin requires documented clean-machine Docker verification
and prominent disclosures covering fictional-only use, provisional results,
absence of security or compliance certification, and the hosted retention,
session isolation and accessibility limits. Broader accessibility, hosted
verification and framework refinements may remain open as follow-up. The
approval applies to the fictional-data demonstration scope.

Reviewed application revision is ea194c3c8210acff92619aa87b3d68046957c40b.
[Checks #231](https://github.com/PrimroseZoe1998/clinicshield/actions/runs/44342494103)
and [container #24](https://github.com/PrimroseZoe1998/clinicshield/actions/runs/44342494055)
passed on that revision. Local Docker verification also passed.

In response to the follow-up about the Docker environment, Benjamin wrote:

> I'm going to have to default to you on this one, my friend, because I don't fully understand your question 😅😅

The project owner accepted the fresh Docker installation on the existing
development PC for this milestone. The run used a clean copy of the reviewed
commit, a no-cache build, an offline smoke test and a browser/PDF walkthrough.
The locally created November 19, 2026 tag points to the reviewed application
revision. GitHub publication was verified November 19, 2026. The tag
resolves to ea194c3c8210acff92619aa87b3d68046957c40b, and the closeout
documentation commit 975bf8f is on main.
