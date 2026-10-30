# Week 3 acceptance audit

Reviewed October 30, 2026 against the original
ClinicShield_Project_Brief_Primrose_Mangwendeza.docx, Week 3 table, the current
implementation, dated decisions and fresh local checks.

Status: core engine implemented and focused regressions passing; original-brief
conformance has open gaps and design differences. This is not a declaration of
stakeholder approval or full Week 3 completion.

## Verified October 30 checkpoint

Implementation commit: `1963a6f` (CVSS context, local cache default, healthcare
references and brief-based audit). The user reported the pushed commit's GitHub
checks green; that CI report was not independently retrieved by the agent.

Manual refresh run:
https://github.com/PrimroseZoe1998/clinicshield/actions/runs/41084601410
The user reported all feeds succeeded and confirmed artifact contents. The agent
then read the downloaded `public-feeds-41084601410.zip`, validated all five
snapshots with the project's cache readers, and checked refresh-status.json:
overall succeeded, five feed outcomes succeeded. The inspected artifact records
KEV/EPSS, Python and Windows lifecycle, and the allowlisted NVD CVE.

The validated snapshots were installed into the ignored local `data/cache/`
directory without rewriting their embedded retrieval timestamps. Previous cache
files were backed up in workspace scratch storage. An offline Lakeview assessment
and its TXT export loaded the new snapshots and CVSS context successfully.

Retrieval timestamps (UTC):
- KEV: 2026-10-30T15:52:19.311077+00:00
- EPSS: 2026-10-30T15:52:22.127643+00:00
- Python lifecycle: 2026-10-30T15:52:22.970422+00:00
- Windows lifecycle: 2026-10-30T15:52:23.149780+00:00
- NVD: 2026-10-30T15:52:23.582333+00:00

The user subsequently confirmed that the October 30 retrieval dates matched in
the app after enabling saved caches. Earlier screenshots and user confirmations
also exercised CVSS and R16 healthcare references in the preview and TXT download.

Latest broad local run: 2,468 tests passed, excluding the known stalled local
`tests/test_app_preview.py`. The subsequent ASCII UI-separator change passed
syntax validation and 28 focused tests. No new runtime changes were made for
this documentation checkpoint, so tests were not repeated.

Status: verified prototype checkpoint with documented scope differences. Core
Week 3 functionality is exercised; full original-brief conformance, independent
rule approval and legal compliance are not claimed. Scheduled execution remains
unobserved. CVSS support is source-reported v3.1 context, not recalculation or all
versions. Refresh artifacts require manual local synchronization. Six rules have
no selected direct HHS CPG relationship. Scoring/Fix First are Week 4 work already
started; Week 5 UI/report requirements are not Week 3 blockers.

Next: preserve this checkpoint and review the Week 4 scoring/rubric requirements
against the implemented model before selecting further implementation work.
No further status email to Benjamin is required for this checkpoint.

## Original Week 3 requirements

| Requirement | Evidence | Assessment |
| --- | --- | --- |
| Vendor/product/version normalizer | normalization.py and matching tests | Implemented conservatively; no fuzzy identity inference |
| Weekly KEV, EPSS, endoflife.date and NVD subset caching into data/cache/ | refresh-feeds.yml; refresh modules; user-reported successful manual run 40963762712 | Four-source workflow configured, but runner and app now use data/cache/; snapshots remain ignored local files distributed as 30-day artifacts, not committed repository data; scheduled execution unobserved |
| KEV, end-of-life, NVD/CVSS and EPSS matchers | Reviewed applicability/lifecycle evidence, KEV/EPSS lookup and narrow NVD adapter | Implemented within bounded reviewed matching scope; source-reported CVSS 3.1 base-score context is now interpreted; other CVSS versions and vector/score recalculation remain unsupported; unsupported NVD ranges/configurations require review |
| YAML schema/loader and first 20 rules, each tested | 24 YAML definitions, typed registries, individual rule tests | 24 implemented under later recorded rule-assignment decisions; not a claim that original Appendix D definitions were implemented unchanged |
| Finding evidence and framework references | RuleObservation, RuleFinding, YAML references, reports | Evidence and partial source-checked NIST/CIS references implemented; October 30 extension adds partial HICP/HIPAA relationships to 24 rules and HHS goal relationships to 18; six direct HHS mappings deliberately omitted (healthcare-rule-review.md) |
| Synthetic planted findings without unexplained false positives | Three-scenario inspection and regression suite | Confirmed findings match documented scenarios, including Lakeview R10 and Westside R11; extra unknown-evidence items remain needs_review rather than invented confirmed gaps |
| Unmatched versions produce a visible inability-to-check result | Unknown-version and vulnerability matching tests; explicit coverage reporting | Passing within tested scope; R24 is limited to patient-information access Y/Unknown, not every inventory row |
| Rule catalog, caches, engine and docs/rules.md | rules/, clinicshield/, refresh artifacts, new rules.md | Rule-authoring guide now present; cache delivery differs as recorded above |

## Fresh verification

162 focused tests passed on October 30, 2026: sample input validation, fictional
scenario evidence and scores, assessment runner, catalog validation/registration,
unknown versions, normalization, vulnerability matching and assessment scoring.
The first attempt hit a sandbox temporary-directory setup error (136 passed,
14 setup errors); repeating with an explicit writable scratch directory passed.
No application defect was inferred from that environment error.

A separate offline inspection evaluated all three scenarios using a fixed
2026-10-28 UTC clock and explicit fictional scenario evidence:

| Scenario | Confirmed rule IDs | Overall |
| --- | --- | --- |
| Lakeview | R03, R05, R07, R08, R10, R12, R16, R18, R19 | 65 |
| Southside | R12, R16, R17, R20, R22 | 82 |
| Westside | R03, R09, R11, R14, R16 | 80 |

Unknown versions remained review items. No R01/R02 CVE finding was fabricated.
Southside encryption uncertainty and absent service coverage remained unresolved.
Scores are provisional and use the October 29 recorded model decision, not the
superseded original target bands. These are synthetic regressions, not real
clinic validation or proof that every possible false positive has been excluded.

## Corrected milestone scope

The original brief places scoring and Fix First in Week 4 (November 2-6) and
Streamlit/results sub-scores/report delivery in Week 5 (November 9-13). Earlier
uncertainty over whether practice-area scores blocked Week 3 was too broad.
Additional real administrator observations are evidence needed for real assessments,
not a prerequisite to completing fictional Week 3 regression checks.

## Remaining decisions and work

1. The bounded CVSS 3.1 context path is implemented; see cvss-context.md.
   It preserves source assessments and does not recalculate scores or support
   every CVSS version. Full original-brief conformance is still not implied.
2. Default local and workflow cache paths now use data/cache/; the verified
   artifact has been installed locally (see local-feed-cache.md). Artifact
   extraction is still required for later updates; automatic repository
   persistence/synchronization remains a documented delivery difference.
3. The healthcare reference extension is implemented with source locators and
   limits (healthcare-rule-review.md). Six rules have no selected direct HHS goal.
   These deliberate omissions remain a difference from a literal all-frameworks
   mapping requirement; rule approval and compliance are not established.
4. Keep the scheduled-run observation and full rule review open. Prior manual/CI
   CI success on 1963a6f is user-reported. The latest downloaded refresh
   artifact was independently validated locally as recorded above; neither
   evidence source proves a scheduled run.

The prior 2,429-test checkpoint and known local Streamlit AppTest hang remain
historical evidence. The later 2,468-test run supersedes the initial focused-only verification,
with the documented local UI-test exclusion. Neither
comprehensive vulnerability detection nor legal compliance is established.
