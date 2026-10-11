# ClinicShield Checklist Framework Mappings

This document records the sources and reasoning behind the mappings
for all 25 checklist questions.

Mappings are project interpretations and require review.
A related framework reference does not establish legal compliance.

## Official sources

- HICP 2023, including Technical Volume 1:
  https://hhscyber.hhs.gov/cornerstone-hicp.html
- HHS Healthcare Cybersecurity Performance Goals:
  https://hhscyber.hhs.gov/cybersecurity-performance-goals.html
- NIST SP 800-66 Rev. 2:
  https://csrc.nist.gov/pubs/sp/800/66/r2/final
- NIST Cybersecurity Framework 2.0:
  https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20

## Mapping rules

For each question, record:

- Question ID and topic.
- HICP practice and relevant sub-practice.
- Exact HHS performance goal, if applicable.
- Whether the goal is Essential or Enhanced.
- Relevant NIST CSF 2.0 function and subcategory.
- Precise HIPAA reference, where applicable.
- Source location and explanation of the relationship.
- Whether the mapping covers the whole question or only part of it.
- Review status and unresolved issues.

Use weight 3 only after confirming an Essential goal mapping.
Other questions have weight 1 under the initial scoring rubric.

Do not force a mapping when no direct relationship is supported.
Do not treat voluntary performance goals as legal requirements.
Check CSF version compatibility before copying an existing crosswalk.

## Q01 Multifactor authentication for email

- HICP: Practice 1, Email Protection Systems.
- Small-organization sub-practice: 1.S.A, Email System Configuration.
  Printed page 10 specifically recommends MFA before email access.
- HHS CPG: Multifactor Authentication, Essential.
  Email Security is also relevant.
- CSF 2.0: Protect, PR.AA-03, authentication.
- HIPAA: 45 CFR 164.312(d), person or entity authentication.
- Interpretation: MFA supports authentication. This citation alone
  does not establish a specific MFA requirement.
- Coverage: The checklist checks MFA for every work mailbox.
  It does not verify phishing resistance or every part of the CPG.
- Proposed weight: 3.
- Review status: Source-supported mapping; Gate 1 review pending.

## Q02 Email filtering and forwarding

- HICP: Practice 1, Email Protection Systems.
- Small-organization sub-practice: 1.S.A, Email System Configuration.
  Printed page 9 discusses active, updated spam and antivirus filtering.
- HHS CPG: Email Security, Essential.
- CSF 2.0: Protect, PR.PS-01, secure configuration practices.
  This is a project interpretation for email configuration.
- HIPAA: Precise mapping remains pending review.
  Do not assume transmission security directly covers every control.
- Coverage: The reviewed HICP section supports filtering.
  Blocking automatic external forwarding needs an additional source.
- Proposed weight: 3, based on the Essential Email Security goal.
- Review status: Partial mapping; forwarding reference and HIPAA
  mapping remain unresolved.

## Sources for Q01 and Q02

- HICP Technical Volume 1, printed pages 9–10:
  https://hhscyber.hhs.gov/Documents/HICP/tech-vol1-508.pdf
- HHS CPG Essential goals, Email Security and Multifactor Authentication:
  https://hhscyber.hhs.gov/cybersecurity-performance-goals.html
- NIST CSF 2.0, Appendix A, PR.AA-03 and PR.PS-01:
  https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf
- HIPAA technical safeguards:
  https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.312

## Q03 Antivirus protection

- HICP: Practice 2, Endpoint Protection Systems.
- Sub-practice: 2.S.A, Basic Endpoint Protection Controls.
  Printed page 14 recommends antivirus with automatic updates.
- HHS CPG: Detect and Respond to Relevant Threats and Tactics,
  Techniques, and Procedures, Enhanced; partial relationship.
  Basic antivirus alone does not establish the broader capability.
- CSF 2.0: Protect, PR.PS-05, prevention of unauthorized software;
  partial project interpretation.
- HIPAA: 45 CFR 164.308(a)(5)(ii)(B), protection from malicious software.
- Proposed weight: 1. No direct Essential mapping confirmed.
- Review status: Source-supported; Gate 1 review pending.

## Q04 Automatic updates

- HICP: Practice 2, sub-practice 2.S.A.
  Printed page 14 recommends automatic endpoint patching.
- HHS CPG: Mitigate Known Vulnerabilities, Essential.
- Coverage: Partial. The CPG focuses on known vulnerabilities in
  internet-accessible networks. This question covers all operating
  systems and browsers, but does not verify patch success.
- CSF 2.0: Protect, PR.PS-02, software maintenance.
- HIPAA: 45 CFR 164.308(a)(1)(ii)(B), risk management.
  Automatic updating is a supporting measure, not the complete standard.
- Proposed weight: 3, subject to approval of this partial relationship.
- Review status: Gate 1 decision required on weighting.

## Q05 Portable device encryption

- HICP: Practice 2, sub-practice 2.S.A.
  Printed page 14 recommends endpoint encryption, especially for laptops.
- HHS CPG: Strong Encryption, Essential, is related.
- Coverage gap: The reviewed CPG description addresses traffic in
  motion. Q05 checks device encryption for stored information.
  Do not equate these scopes without further supporting evidence.
- CSF 2.0: Protect, PR.DS-01, protection of data at rest.
- HIPAA: 45 CFR 164.312(a)(2)(iv), encryption and decryption.
  This is an Addressable implementation specification.
- Proposed weight: 1 until the Essential mapping is resolved.
- Review status: HICP and CSF relationship supported;
  CPG weighting requires review.

## Sources for Q03 to Q05

- HICP Technical Volume 1, section 2.S.A, printed page 14:
  https://hhscyber.hhs.gov/Documents/HICP/tech-vol1-508.pdf
- HHS Essential and Enhanced goal descriptions:
  https://hhscyber.hhs.gov/cybersecurity-performance-goals.html
- NIST CSF 2.0, Appendix A, PR.PS-05, PR.PS-02, PR.DS-01:
  https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf
- HIPAA administrative safeguards:
  https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.308
- HIPAA technical safeguards:
  https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.312

## Q06 Individual accounts

- HICP: Practice 3, sub-practice 3.S.A, Basic Access Management.
  Printed page 16 supports individual accounts and avoiding shared logins.
- HHS CPG: Unique Credentials, Essential.
- CSF 2.0: Protect, PR.AA-01, management of identities and credentials.
- HIPAA: 45 CFR 164.312(a)(2)(i), unique user identification.
- Coverage: Individual logins support accountability. This question
  does not verify password reuse or every part of credential management.
- Proposed weight: 3.
- Review status: Source-supported; Gate 1 review pending.

## Q07 Multifactor authentication for clinical systems

- HICP: Practice 3, sub-practice 3.S.A, printed page 18.
  Practice 2, sub-practice 2.S.A, printed page 15 also supports MFA.
- HHS CPG: Multifactor Authentication, Essential.
- CSF 2.0: Protect, PR.AA-03, authentication.
- HIPAA: 45 CFR 164.312(d), person or entity authentication.
- Coverage: The question checks several systems together.
  One unprotected applicable system means the answer is No.
  It does not verify phishing resistance.
- Proposed weight: 3.
- Review status: Source-supported; Gate 1 review pending.

## Q08 Removing access when staff leave

- HICP: Practice 3, sub-practice 3.S.A, printed page 17.
- HHS CPG: Revoke Credentials for Departing Workforce Members,
  Including Employees, Contractors, Affiliates, and Volunteers, Essential.
- CSF 2.0: Protect, PR.AA-01 and PR.AA-05, identity and access management.
- HIPAA: 45 CFR 164.308(a)(3)(ii)(C), termination procedures.
- Coverage: Same-day removal is ClinicShield's operational benchmark.
  HICP recommends immediate removal; same-day action may leave a gap.
  The cited HIPAA provision does not specify a same-day deadline.
- Proposed weight: 3.
- Review status: Source-supported; timing interpretation requires review.

## Q09 Limiting administrator rights

- HICP: Practice 3, sub-practice 3.S.A, printed pages 17–18.
  Practice 2, sub-practice 2.S.A, printed page 13 also supports limits.
- HHS CPG: Separate User and Privileged Accounts, Essential;
  related but not directly assessed by the current question.
- Coverage gap: Limiting who has administrator rights does not prove
  that those people use separate accounts for ordinary work.
- CSF 2.0: Protect, PR.AA-05, least privilege and separation of duties.
- HIPAA: 45 CFR 164.308(a)(4)(ii)(B), access authorization,
  and 164.312(a)(1), access control.
- Proposed weight: 1 until the Essential mapping is resolved.
- Review status: HICP and CSF relationship supported;
  CPG weighting requires review.

## Sources for Q06 to Q09

- HICP Technical Volume 1, sections 2.S.A and 3.S.A:
  https://hhscyber.hhs.gov/Documents/HICP/tech-vol1-508.pdf
- HHS Essential goals:
  https://hhscyber.hhs.gov/cybersecurity-performance-goals.html
- NIST CSF 2.0, Appendix A, PR.AA-01, PR.AA-03, PR.AA-05:
  https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf
- HIPAA administrative safeguards:
  https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.308
- HIPAA technical safeguards:
  https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.312

## Q10 Daily separated backups

- HICP: Practice 4, Data Protection and Loss Prevention.
  Volume 1, 4.S.B, printed page 21 covers controlled backup storage.
  Supplement: Volume 2, 4.M.D, printed pages 50–51 supports
  restricting access to backups and using offline copies.
- HHS CPG: Basic Incident Planning and Preparedness, Essential.
  Its published crosswalk includes Backup Strategies.
- CSF 2.0: Protect, PR.DS-11, backup creation and protection.
- HIPAA: 45 CFR 164.308(a)(7)(ii)(A), data backup plan.
- Coverage: Daily frequency is ClinicShield's benchmark, not an
  explicit interval in the cited HIPAA provision.
  A separate account alone does not prove ransomware isolation.
- Proposed weight: 3.
- Review status: Source-supported; frequency and isolation review pending.

## Q11 Testing backup recovery

- HICP: Practice 4.
  Supplement: Volume 2, 4.M.D, printed page 52 recommends
  periodic restoration testing.
- HHS CPG: Basic Incident Planning and Preparedness, Essential;
  restoration testing supports this broader goal.
- CSF 2.0: Protect, PR.DS-11, testing backups.
- HIPAA: 45 CFR 164.308(a)(7)(ii)(D), testing and revision procedures.
- Coverage: Six months is ClinicShield's benchmark.
  Restoring one file is a useful check, not a complete recovery exercise.
- Proposed weight: 3.
- Review status: Source-supported; testing benchmark review pending.

## Q12 Vendor agreements

- HICP: Practice 4, Volume 1, 4.S.B, printed page 21.
  Practice 1, 1.S.A, printed page 9 also discusses vendor agreements.
- HHS CPG: Vendor/Supplier Cybersecurity Requirements, Essential;
  partial relationship.
- CSF 2.0: Govern, GV.SC-05, supplier requirements in agreements.
- HIPAA: 45 CFR 164.308(b)(1) and (b)(3);
  164.314(a)(1) and (a)(2)(i), business associate arrangements.
- Coverage: Agreement presence does not verify its contents
  or the vendor's implementation. Assess applicability first.
- Proposed weight: 3, subject to review of the partial CPG relationship.
- Review status: Source-supported; applicability review pending.

## Q13 Secure disposal

- HICP: Practice 4, Volume 1, 4.S.B, printed page 21;
  Practice 5, 5.S.C, Decommissioning, printed page 23.
- HHS CPG: No direct Essential goal mapping confirmed.
- CSF 2.0: Identify, ID.AM-08, asset management throughout
  the lifecycle; Protect, PR.DS-01, protection of stored data.
  These are project interpretations for secure disposal.
- HIPAA: 45 CFR 164.310(d)(2)(i), disposal,
  and (d)(2)(ii), media re-use.
- Coverage: Requires an appropriate disposal process.
  Deleting files alone does not establish secure removal.
- Proposed weight: 1.
- Review status: Source-supported; Gate 1 review pending.

## Sources for Q10 to Q13

- HICP Technical Volume 1:
  https://hhscyber.hhs.gov/Documents/HICP/tech-vol1-508.pdf
- HICP Technical Volume 2, supplementary backup guidance:
  https://hhscyber.hhs.gov/Documents/HICP/tech-vol2-508.pdf
- HHS CPG goal descriptions and crosswalk:
  https://hhscyber.hhs.gov/cybersecurity-performance-goals.html
- NIST CSF 2.0, Appendix A:
  https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf
- HIPAA administrative safeguards:
  https://www.ecfr.gov/current/title-45/section-164.308
- HIPAA organizational requirements:
  https://www.ecfr.gov/current/title-45/section-164.314
- HIPAA physical safeguards:
  https://www.ecfr.gov/current/title-45/section-164.310

## Q14 Updated inventory

- HICP: Practice 5, 5.S.A, Inventory, printed pages 22–23.
- HHS CPG: Asset Inventory, Enhanced.
- CSF 2.0: Identify, ID.AM-01 and ID.AM-02,
  hardware and software inventories.
- HIPAA: 45 CFR 164.308(a)(1)(ii)(A), risk analysis;
  inventory supports identifying systems and information in scope.
  This is a supporting relationship, not the entire requirement.
- Coverage: Annual review is ClinicShield's benchmark.
  Inventories also need updates when assets change.
- Proposed weight: 1.
- Review status: Source-supported; Gate 1 review pending.

## Q15 Separate guest Wi-Fi

- HICP: Practice 6, 6.S.A, Network Segmentation, printed page 24;
  6.S.B, Physical Security and Guest Access, printed page 25.
- HHS CPG: Network Segmentation, Enhanced.
- CSF 2.0: Protect, PR.IR-01, restricting unauthorized network access.
- HIPAA: 45 CFR 164.312(a)(1), access control;
  supporting project interpretation.
- Coverage: Guest separation is one part of network segmentation.
  Different network names alone do not prove access is restricted.
- Proposed weight: 1.
- Review status: Source-supported; Gate 1 review pending.

## Q16 Router security

- HICP: Practice 7, 7.S.A, Vulnerability Management,
  printed page 26 covers default passwords and outdated software.
  Practice 6 provides related network-protection guidance.
- HHS CPG: Mitigate Known Vulnerabilities, Essential;
  partial relationship for firmware vulnerabilities.
- CSF 2.0: Protect, PR.PS-01, configuration;
  PR.PS-02, software maintenance; PR.AA-01, credentials.
- HIPAA: 45 CFR 164.308(a)(1)(ii)(B), risk management.
- Coverage: Changing a default password and updating within a year
  do not establish that the device is currently secure.
  Urgent patches may require much faster action.
- Proposed weight: 3, subject to review of the partial CPG relationship.
- Review status: Benchmark and weighting review required.

## Q17 Protected remote access

- HICP: Practice 3, 3.S.A, printed page 18 recommends MFA,
  including for VPN connections, and restricting inbound RDP.
- HHS CPG: Multifactor Authentication, Essential.
- CSF 2.0: Protect, PR.AA-03 and PR.IR-01,
  authentication and network-access protection.
- HIPAA: 45 CFR 164.312(d), authentication;
  164.312(e)(1), transmission security.
- Wording corrected: Enabled remote access must require MFA.
  A VPN alone does not satisfy the question.
- Answer interpretation: Yes if remote access is disabled, or only
  needed connections are enabled and all require MFA.
  No if access is unnecessarily enabled or any connection lacks MFA.
  Unknown if these settings have not been checked.
- Coverage: This does not verify phishing resistance, VPN configuration,
  or every aspect of remote-access security.
- Proposed weight: 3.
- Rule R07 must use this corrected interpretation.
- Existing synthetic Q17 answers require review against this wording.
- Review status: Wording corrected; rule implementation and sample
  evidence review pending.

## Sources for Q14 to Q17

- HICP Technical Volume 1, sections 3.S.A, 5.S.A, 6.S.A,
  6.S.B, and 7.S.A:
  https://hhscyber.hhs.gov/Documents/HICP/tech-vol1-508.pdf
- HHS Essential and Enhanced goals:
  https://hhscyber.hhs.gov/cybersecurity-performance-goals.html
- NIST CSF 2.0, Appendix A:
  https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf
- HIPAA administrative safeguards:
  https://www.ecfr.gov/current/title-45/section-164.308
- HIPAA technical safeguards:
  https://www.ecfr.gov/current/title-45/section-164.312

## Q18 Supported operating systems

- HICP: Practice 2, 2.S.A, printed page 14;
  Practice 7, 7.S.A, printed page 26.
- HHS CPG: Mitigate Known Vulnerabilities, Essential;
  partial relationship.
- CSF 2.0: Protect, PR.PS-02, software lifecycle maintenance.
- HIPAA: 45 CFR 164.308(a)(1)(ii)(B), risk management.
- Coverage: Vendor support, including applicable extended coverage,
  must be checked. Support alone does not prove patches are installed.
- Proposed weight: 3, subject to review of the partial CPG relationship.
- Review status: Q18 wording correction recorded; Gate 1 review pending.

## Q19 Checking installed updates

- HICP: Practice 7, 7.S.A, printed page 26;
  Practice 2, 2.S.A provides supporting patch guidance.
- HHS CPG: Mitigate Known Vulnerabilities, Essential;
  partial relationship.
- CSF 2.0: Protect, PR.PS-02, software maintenance.
- HIPAA: 45 CFR 164.308(a)(1)(ii)(B), risk management.
- Coverage: Monthly verification is ClinicShield's benchmark.
  It must not delay urgent vulnerability remediation.
- Proposed weight: 3, subject to review of the partial CPG relationship.
- Review status: Source-supported; verification interval review pending.

## Q20 Written incident plan

- HICP: Practice 8, 8.S.A, Incident Response, printed pages 27–29.
- HHS CPG: Basic Incident Planning and Preparedness, Essential.
- CSF 2.0: Identify, ID.IM-04, establishing and maintaining plans.
  Respond, RS.MA-01, is related to executing those plans.
- HIPAA: 45 CFR 164.308(a)(6)(i), security incident procedures.
- Coverage: A short plan is a starting point. This question does not
  verify exercises, complete playbooks, or successful execution.
- Proposed weight: 3.
- Review status: Source-supported; Gate 1 review pending.

## Q21 Reporting security problems

- HICP: Practice 8, 8.S.A, printed pages 27–29.
  Practice 2, 2.S.A, printed page 15 discusses reporting lost devices.
- HHS CPG: Basic Incident Planning and Preparedness, Essential;
  Basic Cybersecurity Training is also relevant.
- CSF 2.0: Protect, PR.AT-01, staff awareness;
  Respond, RS.CO-02, stakeholder notification, is related.
- HIPAA: 45 CFR 164.308(a)(6)(ii), response and reporting.
- Coverage: Knowing the reporting contact supports the process.
  It does not establish that reports are acted on or documented.
- Proposed weight: 3.
- Review status: Source-supported; Gate 1 review pending.

## Q22 Breach notification preparation

- HICP: Practice 8, 8.S.A, printed page 28 describes
  legal, privacy, and compliance roles in breach assessment.
- HHS CPG: Basic Incident Planning and Preparedness, Essential;
  supporting relationship, not a notification-specific goal.
- CSF 2.0: Respond, RS.CO-02, stakeholder notification.
- HIPAA: 45 CFR 164.400–414, Breach Notification Rule.
  This is separate from the Security Rule in Subpart C.
- Coverage: The question checks preparation to obtain guidance.
  It does not determine whether an incident is a reportable breach,
  identify every recipient, or calculate a legal deadline.
- Proposed weight: 1 until the Essential relationship is approved.
- Review status: Partial mapping; weighting and legal review pending.

## Sources for Q18 to Q22

- HICP Technical Volume 1:
  https://hhscyber.hhs.gov/Documents/HICP/tech-vol1-508.pdf
- HHS CPG goal descriptions:
  https://hhscyber.hhs.gov/cybersecurity-performance-goals.html
- NIST CSF 2.0, Appendix A:
  https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf
- HIPAA administrative safeguards:
  https://www.ecfr.gov/current/title-45/section-164.308
- HHS Breach Notification Rule overview:
  https://www.hhs.gov/hipaa/for-professionals/breach-notification/index.html

## Q23 Medical device inventory and separation

- HICP: Practice 9, 9.S.A, Medical Device Security, printed page 30.
  It directs readers to supplementary guidance in Volume 2.
  Practice 5, 5.S.A supports inventory; Practice 6, 6.S.A
  supports restricting medical devices to appropriate network zones.
- HHS CPG: Asset Inventory and Network Segmentation, both Enhanced.
- CSF 2.0: Identify, ID.AM-01; Protect, PR.IR-01 and PR.PS-02.
- HIPAA: 45 CFR 164.308(a)(1)(ii)(A) and (B),
  risk analysis and risk management, as supporting relationships.
- Coverage: Inventory, support status, and segmentation are separate
  controls. A single answer cannot identify which part is missing.
  Define how organizations with no medical devices should answer.
- Proposed weight: 1.
- Review status: Compound question and applicability require review.

## Q24 Security responsibility and risk analysis

- HICP: Practice 10, 10.S.A, Policies, printed pages 31–32;
  10.S.B, Cybersecurity Risk Assessment and Management,
  printed pages 33–34.
- HHS CPG: No direct Essential mapping confirmed for both components.
- CSF 2.0: Govern, GV.RR-02, roles and responsibilities;
  Identify, ID.RA-04 and ID.RA-05, risk assessment.
- HIPAA: 45 CFR 164.308(a)(2), assigned security responsibility;
  164.308(a)(1)(ii)(A), risk analysis.
- Coverage: The 12-month interval is ClinicShield's benchmark.
  Risk analysis must also respond to relevant changes.
- Proposed weight: 1 until an Essential relationship is supported.
- Review status: Compound question requires separate follow-up fields.
  A No answer must not automatically assert that both controls are absent.

## Q25 Staff security training

- HICP: Practice 10, 10.S.C, Security Awareness and Training,
  printed page 35 supports onboarding and annual training.
- HHS CPG: Basic Cybersecurity Training, Essential.
- CSF 2.0: Protect, PR.AT-01, staff awareness and training.
- HIPAA: 45 CFR 164.308(a)(5)(i), security awareness and training.
- Coverage: Completion does not prove effectiveness.
  The cited HIPAA provision does not itself specify an annual interval.
- Proposed weight: 3.
- Review status: Source-supported; Gate 1 review pending.

## Sources for Q23 to Q25

- HICP Technical Volume 1, practices 5, 6, 9, and 10:
  https://hhscyber.hhs.gov/Documents/HICP/tech-vol1-508.pdf
- HHS CPG goal descriptions:
  https://hhscyber.hhs.gov/cybersecurity-performance-goals.html
- NIST CSF 2.0, Appendix A:
  https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf
- HIPAA administrative safeguards:
  https://www.ecfr.gov/current/title-45/section-164.308