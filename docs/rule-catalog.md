# Starter rule catalog

Status: draft reconstructed from existing project documentation.
This is not a complete approved rule specification.

## Existing rule meanings

| ID | Meaning | Source |
| --- | --- | --- |
| R03 | Unsupported operating system | samples/EXPECTED.md |
| R05 | Portable-device encryption disabled or unknown | samples/EXPECTED.md |
| R07 | Remote-access safeguards missing or unknown | samples/EXPECTED.md; docs/framework-mappings.md |
| R08 | SMB on an unsupported operating system | samples/EXPECTED.md |
| R09 | Telnet service present | samples/EXPECTED.md |
| R10 | Default administrator password unchanged; decision pending | samples/EXPECTED.md |
| R11 | Medical-device network segmentation gap | samples/EXPECTED.md |
| R12 | Email MFA gap | samples/EXPECTED.md |
| R14 | Shared user accounts | samples/EXPECTED.md |
| R16 | Backup separation or restore-testing gap | samples/EXPECTED.md |
| R17 | Missing Business Associate Agreement | samples/EXPECTED.md |
| R18 | Guest Wi-Fi separation gap | samples/EXPECTED.md |
| R19 | Router security gap | samples/EXPECTED.md |
| R20 | Incident plan or named security responsibility gap | samples/EXPECTED.md; docs/scoring.md |
| R22 | Missing documented risk analysis | samples/EXPECTED.md; docs/scoring.md |
| R24 | Unknown or unverified software versions | samples/EXPECTED.md |

## Proposed definitions requiring review

| ID | Proposed meaning |
| --- | --- |
| R01 | Confirmed applicable vulnerability listed in CISA KEV |
| R02 | Other confirmed applicable CVE; EPSS informs priority |
| R04 | Unsupported application release |
| R06 | Internet-exposed remote administration service |
| R13 | Clinical-system MFA gap, using Q07 and software evidence |
| R15 | Antivirus protection gap, using Q03 |
| R21 | Security-reporting or breach-notification preparation gap, using Q21/Q22 |
| R23 | Staff security training gap, using Q25 |

These assignments are proposals, not previously approved definitions.
R01/R02 require confirmed applicability, not product-name similarity.
R06 exposure and R07 safeguards describe distinct risks.
Preserve separate evidence and actions within combined rules.

## Implementation requirements

- Define precise trigger and non-trigger conditions.
- Distinguish confirmed gaps from unknown information.
- Preserve the reviewed Q17 interpretation for R07.
- R20 uses Q20 and Q24a; R22 uses Q24b.
- Unknown versions must not produce invented CVE matches.
- Combine evidence for the same issue without losing distinct risks.
- Define severity, evidence, fix, owner, effort, and cost.
- Record framework references and their review status.
- Test each rule before connecting it to assessment scoring.