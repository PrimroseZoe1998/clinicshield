# Rule framework source review

Reviewed October 29, 2026 by the coding agent against the official sources below.
These are project interpretations of partial relationships, not publisher-endorsed
crosswalks, full safeguard assessments, legal conclusions or reviewer approval
of rule triggers and severities. Rule definitions remain draft.

## Sources

- [NIST CSF 2.0, NIST CSWP 29, February 26, 2024](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf), Appendix A. Printed page numbers are used below.
- [CIS Controls v8.1 official Navigator](https://www.cisecurity.org/controls/CIS-controls-navigator), exact safeguard IDs below. Version 8.1 was selected and checked.

CSF outcomes are broad. The mappings below identify related areas; all have
partial coverage. A source-checked reference does not establish a clinic control.
No new HICP, HHS CPG or HIPAA rule crosswalk is asserted by this review. Existing
question-level crosswalks retain their own scope. No CIS mapping is forced for
R14 or R22. These omissions are deliberate and not unresolved placeholder IDs.

## Source locators

| Rule | CSF 2.0 IDs | Printed pages | CIS v8.1 IDs |
| --- | --- | --- | --- |
| R01 | ID.RA-01; ID.RA-06 | 18-19 | 7.7 |
| R02 | ID.RA-01; ID.RA-06 | 18-19 | 7.7 |
| R03 | PR.PS-02 | 20 | 2.2 |
| R04 | PR.PS-02 | 20 | 2.2 |
| R05 | PR.DS-01 | 20 | 3.6 |
| R06 | PR.IR-01 | 20 | 4.8 |
| R07 | PR.AA-03; PR.IR-01 | 19-20 | 6.4; 4.8 |
| R08 | PR.PS-02 | 20 | 2.2 |
| R09 | PR.PS-01 | 20 | 4.6 |
| R10 | PR.AA-01 | 19 | 4.7 |
| R11 | PR.IR-01 | 20 | 12.2 |
| R12 | PR.AA-03 | 19 | 6.3 |
| R13 | PR.AA-03 | 19 | 6.3 |
| R14 | PR.AA-01 | 19 | No direct mapping selected |
| R15 | PR.PS-01 | 20 | 10.1; 10.2 |
| R16 | PR.DS-11 | 20 | 11.2; 11.4; 11.5 |
| R17 | GV.SC-05 | 18 | 15.4 |
| R18 | PR.IR-01 | 20 | 12.2 |
| R19 | PR.PS-01 | 20 | 4.2 |
| R20 | ID.IM-04; GV.RR-02 | 17,19 | 17.1; 17.4 |
| R21 | RS.CO-02 | 22 | 17.2; 17.3 |
| R22 | ID.RA-04; ID.RA-05 | 19 | No direct mapping selected |
| R23 | PR.AT-01 | 20 | 14.1 |
| R24 | ID.AM-02 | 18 | 2.1 |

## Per-rule coverage limits

### R01

Explicit CVE applicability and KEV membership inform this finding. Neither establishes organizational exploitation, a remediation program or its cadence.

### R02

Applicability is evaluated independently of EPSS. Priority context does not establish completed remediation or a comprehensive vulnerability program.

### R03

The rule evaluates a supplied OS release and support coverage. It does not assess every software exception, compensating control or residual-risk acceptance.

### R04

Application support evidence covers one supplied release. Inventory authorization, documented exceptions and ongoing review are outside this finding.

### R05

This rule covers portable assets and supplied encryption status only. It does not inventory every sensitive-data location or verify cryptographic configuration.

### R06

An internet-facing administration listener is a project risk signal. Necessary, authorized remote access is not categorically prohibited by these references.

### R07

Q17 combines remote-access necessity and MFA. Apply the CIS references to their relevant branches; a VPN alone does not satisfy the project checklist.

### R08

The support-related finding also records SMB presence. It does not identify an exploitable SMB defect or require disabling every file-sharing service.

### R09

A Telnet listener prompts configuration review. Actual management use, transmitted credentials and any operational necessity are not established by the listener.

### R10

Unchanged default-password evidence covers one credential condition. It does not independently audit all default accounts or their necessity.

### R11

Supplied medical-device separation evidence supports a project segmentation finding. The rule does not assess the complete architecture or vendor constraints.

### R12

Email MFA coverage is a project check. CIS 6.3 applies conditionally to externally exposed applications where supported; all account configurations are not verified.

### R13

Clinical MFA is assessed from Q07 and supplied software. CIS 6.3 is conditional on external exposure and support; it is not a universal mandate for every internal application.

### R14

A shared-login answer prompts identity accountability review. It does not establish absent authorization or independently verify unique identities for every user.

### R15

Q03 combines protection and automatic updating. A combined No does not identify the affected computers or which component failed; detection effectiveness is not tested.

### R16

Q10/Q11 combine daily backup, separation and restore testing. Project daily frequency differs from CIS 11.2; the answers do not establish CIS isolation methods or quarterly sampling.

### R17

A reported missing BAA is a narrow agreement gap. These references concern security agreements generally; they do not establish BAA applicability, contractual sufficiency or legal compliance.

### R18

Q15 reports guest-network separation. Traffic filtering, alternate designs and the full architecture are not independently tested.

### R19

Q16 combines router safeguards. A combined No does not identify every failed setting or establish the documented configuration process and review cadence.

### R20

Q20 and Q24a distinguish an incident plan from security responsibility. General security ownership is broader than the CIS incident-handling role; neither answer tests execution.

### R21

Q21/Q22 address reporting and notification preparation. Preparation is narrower than actual incident notification; no breach, recipient, deadline or legal obligation is determined.

### R22

Q24b reports documented risk analysis. It does not verify assessment quality, complete threat coverage, likelihood methods or legal sufficiency.

### R23

Q25 reports training provision. Completion, effectiveness, role coverage, onboarding and annual curriculum review are not independently verified.

### R24

Unknown versions require inventory follow-up. Versions are identifiers here, not proof of vulnerability; the rule does not audit every inventory field or its review cadence.

## Review status meaning

`reviewed` on a framework reference means the coding agent checked the cited
version/identifier and documented a partial relationship on the date above. It
does not mean Benjamin approved this crosswalk. The separate rule-level
`review_status: draft` remains unchanged. Scores and finding severity are unchanged.
Additional framework families require their own source review before being added.

## Verification

2,360 tests passed locally with the known stalled `test_app_preview.py` file
excluded. Source-check scope and URLs survive report generation/download rendering;
pending references still retain a distinct label when supplied. All scenario scores
remain 65/82/80 and provisional. The high-severity Bandit check passed, with no
medium or high findings, and `git diff --check` passed. The revised browser
presentation has not yet been manually checked. No dependency changes were made.
