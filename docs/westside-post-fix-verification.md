# Westside initial and synthetic post fix comparison

Verified November 2, 2026. This is a reproducible regression fixture, not real
remediation, vendor verification or a forecast. The original Westside sample
files and 80-point scenario baseline are unchanged. The helper is isolated in
clinicshield/sample_remediation.py and is not applied to uploaded inventories
or silently substituted into the app's Westside sample.

## Explicit fictional changes

1. WH-MD02 and WH-LT01 migrate to Fictional Supported OS / synthetic-1, with
   synthetic matched support evidence. This is not a claim about an actual
   vendor release, support entitlement or medically approved migration.
2. WH-LT01 encryption is assumed enabled with Q05 changed Unknown -> Yes.
3. The WH-PR01 TCP 23 Telnet service is assumed disabled and removed from the
   supplied services inventory. No unobserved replacement service is invented.
4. Individual accounts are assumed established: Q06 No -> Yes and the related
   Site Management note updated with a synthetic label.
5. A controlled restore test is assumed successful: Q11 No -> Yes and the backup
   note updated with a synthetic label. Backup frequency/separation is unchanged.
6. WH-MD02 restricted network access is assumed effective with explicit synthetic
   separation evidence: Q23 No -> Yes. Other device placement is unchanged.
7. Q18 No -> Unknown because the other OS support records are still unassessed;
   replacing the two known unsupported systems does not establish support for all.

Software versions remain Unknown. Checklist weights, severities, global formula,
entity count, cloud rows and denominators are unchanged. Timestamp 2026-11-02
17:00 UTC is a fixed fixture-generation clock, not an external observation.

## Measured results

| Metric | Initial scenario | Synthetic post fix |
| --- | ---: | ---: |
| Safeguards earned / available | 38 / 47 | 46 / 47 |
| Safeguards | 80.8511 | 97.8723 |
| Exposure | 78.6842 | 100.0000 |
| Overall | 80 | 99 |
| Band | Needs attention | Good shape |
| Confirmed rule IDs | R03, R09, R11, R14, R16 | None in this fixture |
| Review groups | 80 | 79 |
| Coverage issues | 7 | 7 |
| Provisional | Yes | Yes |

R05 starts as an Unknown encryption review item, not a confirmed encryption
failure. Its review item disappears after the synthetic encryption change.
The 8/47 safeguards gain comes from Q05 (+1), Q06 (+3), Q11 (+3), and Q23 (+1).
Q18 remains zero-weight-earned in both No and Unknown states. Technical points
for the known OS, Telnet and separation findings are removed under the fixture.

The post-fix Exposure 100 means no remaining confirmed technical deduction in
the supplied scope. It does not resolve unknown OS support, software versions,
default-password evidence or missing KEV/EPSS/applicability coverage. The Good
shape label is produced by existing thresholds and must be presented with those
warnings; it is not a safety/compliance conclusion.

## Benchmark disposition

The original brief proposed At risk initially and Needs attention after fixes.
The retained model yields 80 -> 99 for these declared inputs. The October 29
reported decision revised initial sample expectations; it did not independently
approve this new post-fix result. The comparison is technically verified, while
benchmark/rubric acceptance remains an open item for Benjamin. Do not alter
thresholds or invent Critical findings to force the old bands.

## Reproduction and evidence

Read the original sample with read_assessment, build_sample_evidence for
westside_health, and score_assessment. Apply build_westside_post_fix to a COPY,
then score the returned assessment and evidence with the same clock and policy.
See tests/test_sample_remediation.py for the executable setup. Tests also reject
wrong/changed baseline identities and naive clocks, preserve input files, retain
unknown versions and verify synthetic/uncertainty notices in the TXT export.

The output review bundle contains initial and post-fix TXT and JSON reports.
No live feed downloads or real inventory are used. Manual app verification of
the post-fix fixture is not claimed: it is a backend comparison with saved outputs.

Validation November 2: 2,504 tests passed excluding the known locally stalled
Streamlit AppTest file. High-severity Bandit check passed (zero medium/high;
five existing low findings). No new CI run or independent post-fix rubric
approval is claimed.
