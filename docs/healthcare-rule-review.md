# Healthcare rule reference review

Source checked October 30, 2026. These are partial project interpretations, not publisher-endorsed crosswalks or compliance determinations. Rule definitions remain draft. No triggers, severities, checklist weights or score calculations changed.

## Sources and method

- HICP 2023 Technical Volume 1: https://hhscyber.hhs.gov/Documents/HICP/tech-vol1-508.pdf
- HHS voluntary CPGs: https://hhscyber.hhs.gov/cybersecurity-performance-goals.html
- HIPAA source sections: https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.308 ; https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.312 ; https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.314
- HICP locators use printed pages; PDF viewer page numbers are three greater in Volume 1. Extracted text was checked; attempted web screenshots failed with cache-miss errors, so visual page verification is not claimed.
- Existing NIST/CIS references retain their October 29 review and limits. New reviewed labels mean agent source-checking of these partial relationships only. They do not approve rule definitions or real clinic controls.

## Rule locators and project interpretation

| Rule | HICP Volume 1 (printed page) | HIPAA supporting locator | Project coverage limit |
| --- | --- | --- | --- | --- |
| R01 | 7.S.A (p. 26) | 164.308(a)(1)(ii)(B) | Applicability and KEV evidence identify a remediation candidate; they do not establish exploitation or completed risk treatment. |
| R02 | 7.S.A (p. 26) | 164.308(a)(1)(ii)(B) | Applicable CVE evidence supports follow-up; EPSS does not establish exploitation or remediation. |
| R03 | 2.S.A (p. 14) | 164.308(a)(1)(ii)(B) | OS support status is one risk input, not a full risk-management assessment or a specific legal product ban. |
| R04 | 2.S.A (p. 14) | 164.308(a)(1)(ii)(B) | Application support is assessed per supplied release; compensating controls and risk acceptance are not audited. |
| R05 | 2.S.A (p. 14) | 164.312(a)(2)(iv) | Portable-device encryption status is reported, not cryptographic effectiveness. Encryption/decryption is Addressable; this finding is not a legal determination. |
| R06 | 6.S.A (p. 24) | 164.312(a)(1) | An internet-facing administration listener prompts access review; authorization and actual ePHI access are not established. |
| R07 | 2.S.A (p. 15) | 164.312(d) | Q17 combines need for remote access and MFA; the MFA relationship applies only to that branch. Authentication does not by itself mandate a specific MFA method. |
| R08 | 2.S.A (p. 14) | 164.308(a)(1)(ii)(B) | SMB presence accompanies the OS-support issue; no exploitable SMB defect or separate legal prohibition is inferred. |
| R09 | 6.S.A (p. 24) | 164.312(e)(1) | Telnet presence prompts traffic/access review; the listener does not prove transmission of ePHI or a transmission-security violation. |
| R10 | 7.S.A (p. 26) | 164.308(a)(5)(ii)(D) | Unchanged-default-password evidence covers one credential condition. Password management is Addressable; no full credential audit is performed. |
| R11 | 9.S.A; 6.S.A (p. 30) | 164.312(a)(1) | Medical-device separation evidence is limited; effective access enforcement and complete device security are not verified. |
| R12 | 1.S.A (p. 10) | 164.312(d) | Email MFA evidence covers supplied accounts; phishing resistance and all authentication procedures are not verified. |
| R13 | 3.S.A (p. 18) | 164.312(d) | Clinical MFA evidence covers the supplied application; authentication procedures and all access paths are not audited. |
| R14 | 3.S.A (p. 16) | 164.312(a)(2)(i) | Shared-account evidence relates to user identification; individual identity tracking and legal applicability require separate evaluation. |
| R15 | 2.S.A (p. 14) | 164.308(a)(5)(ii)(B) | Q03 reports antivirus status, not a complete malware-defense capability. The cited malware specification is Addressable. |
| R16 | 4.S.B (p. 21) | 164.308(a)(7)(ii)(A); 164.308(a)(7)(ii)(D) | Q10 does not distinguish frequency from separation. Backup copies are Required; contingency testing is Addressable. Daily frequency and a six-month test interval are project benchmarks. |
| R17 | 4.S.B (p. 21) | 164.314(a)(1); 164.314(a)(2)(i) | Agreement presence does not establish BAA applicability, contract sufficiency or vendor implementation; evaluate the vendor relationship first. |
| R18 | 6.S.A; 6.S.B (p. 24) | 164.312(a)(1) | Guest separation is one access-boundary check; a checklist answer does not demonstrate technical isolation or a mandated topology. |
| R19 | 7.S.A (p. 26) | 164.308(a)(1)(ii)(B) | A combined router answer does not identify which setting failed; no specific CVE, enforced baseline or complete risk treatment is established. |
| R20 | 8.S.A; 10.S.A (p. 27) | 164.308(a)(6)(i); 164.308(a)(2) | Incident planning and security responsibility are separate branches. A combined finding does not mean both failed or that response procedures were exercised. |
| R21 | 8.S.A (p. 27) | 164.308(a)(6)(ii) | Q21 reporting preparation is related; Q22 requires separate breach/notification evaluation. No breach, legal notification duty, recipient or deadline is determined. |
| R22 | 10.S.B (p. 33) | 164.308(a)(1)(ii)(A) | Reported absence of documented risk analysis prompts follow-up; a Yes answer would not establish a thorough or sufficient legal risk analysis. |
| R23 | 10.S.C (p. 35) | 164.308(a)(5)(i) | Training answers do not verify attendance, coverage, effectiveness or all workforce roles. |
| R24 | 5.S.A (p. 22) | 164.308(a)(1)(ii)(A) | Unknown software versions are inventory uncertainty supporting risk-analysis follow-up, not confirmed vulnerabilities or a complete risk analysis. |

R16 additionally uses HICP Volume 2, 4.M.D, printed pp. 50-52 (PDF viewer page 57 for restoration testing), as an explicitly scoped medium/large-organization supplement: https://hhscyber.hhs.gov/Documents/HICP/tech-vol2-508.pdf#page=57

## HHS goal coverage

| Rule | Goal | Tier | Scope |
| --- | --- | --- | --- |
| R01 | Mitigate Known Vulnerabilities | Essential | Conditional on independently established Internet accessibility; this rule alone does not establish that condition. |
| R02 | Mitigate Known Vulnerabilities | Essential | Conditional on independently established Internet accessibility; this rule alone does not establish that condition. |
| R07 | Multifactor Authentication | Essential | Only the MFA branch, for Internet-accessible accounts where safe and technically capable; not proof of phishing resistance. |
| R09 | Configuration Management | Enhanced | Review of one service configuration; not evidence of an established baseline or a blanket ban on Telnet. |
| R10 | Configuration Management | Enhanced | One default-credential setting only; not a unique-credentials or complete baseline assessment. |
| R11 | Network Segmentation | Enhanced | Only the supplied medical-device boundary; no demonstration of all critical-asset segmentation. |
| R12 | Email Security | Essential | Email MFA is one component; filtering, forwarding and other email safeguards are outside this rule. |
| R13 | Multifactor Authentication | Essential | Conditional on independently verified Internet accessibility and safe technical capability; internal systems alone do not establish this scope. |
| R14 | Unique Credentials | Essential | Shared-account reports cover only part of identity controls; anomalous-activity detection and all lateral-movement paths are untested. |
| R15 | Detect and Respond to Relevant Threats and Tactics, Techniques, and Procedures | Enhanced | Basic antivirus is a limited supporting measure, not demonstrated endpoint detection and response. |
| R16 | Basic Incident Planning and Preparedness | Essential | Backup/restore checks support recovery; they do not demonstrate complete incident readiness. |
| R17 | Vendor/Supplier Cybersecurity Requirements | Essential | Agreement presence is narrower than verified supplier requirements and implementation. |
| R18 | Network Segmentation | Enhanced | Guest separation only; effective enforcement and all critical-asset boundaries are untested. |
| R19 | Configuration Management | Enhanced | Router settings are a limited configuration check; no organizational baseline is verified. |
| R20 | Basic Incident Planning and Preparedness | Essential | Incident-plan branch only; naming a responsible person alone does not demonstrate preparedness. |
| R21 | Basic Incident Planning and Preparedness | Essential | Reporting preparation only, not tested incident handling or a breach-notification determination. |
| R23 | Basic Cybersecurity Training | Essential | Reported training presence only; behavior change and training effectiveness are untested. |
| R24 | Asset Inventory | Enhanced | Version completeness for selected software only; no comprehensive asset discovery or inventory cadence is established. |

## No direct HHS goal selected

- R03: Support status alone does not establish an Internet-accessible known vulnerability.
- R04: Support status alone does not establish an Internet-accessible known vulnerability.
- R05: Stored-data encryption differs from the Strong Encryption goal scope of traffic in motion.
- R06: A listener alone does not demonstrate exploitability, absent MFA or deficient segmentation.
- R08: SMB on an unsupported OS does not alone establish the Internet-accessible known-vulnerability condition.
- R22: The single risk-analysis question does not directly assess a selected goal.

All 24 rules now carry partial HICP and HIPAA supporting references; 18 carry a partial/conditional HHS goal reference. The six omissions are deliberate, documented scope gaps rather than fabricated goal IDs. This does not satisfy a literal requirement that every rule map directly to every framework.

## Interpretation safeguards

Addressable specifications are labeled where relevant; that label is not interpreted as optional. The project does not decide legal applicability or substitute for the required evaluation. No HIPAA citation here mandates the project scoring model, backup interval, MFA technique or network topology. Q22 notification duties need separate analysis and are not asserted by the R21 incident-reporting reference.

## Validation

October 30: 2,468 tests passed, excluding the known locally stalled
`tests/test_app_preview.py` file. Scenario scores remain 65/82/80 and provisional.
Tests check report propagation, conditional MFA scope, Addressable labels and
deliberate HHS omissions. The subsequent supplied R16 screenshot and user-confirmed TXT download show
these references and limits. No new CI run or independent mapping approval
is claimed. All non-reference rule fields were compared before/after
and preserved.
