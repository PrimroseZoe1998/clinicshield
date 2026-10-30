# Week 3 acceptance audit

Reviewed October 30, 2026 against the original
ClinicShield_Project_Brief_Primrose_Mangwendeza.docx, Week 3 table, the current
implementation, dated decisions and fresh local checks.

Status: core engine implemented and focused regressions passing; original-brief
conformance has open gaps and design differences. This is not a declaration of
stakeholder approval or full Week 3 completion.

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
   successes are user-reported historical evidence; no new CI run was verified
   during this documentation audit.

The prior 2,429-test checkpoint and known local Streamlit AppTest hang remain
historical evidence. This focused audit did not rerun that entire suite. Neither
comprehensive vulnerability detection nor legal compliance is established.
