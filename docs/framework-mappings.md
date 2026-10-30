# ClinicShield Checklist Framework Mappings

This document records the sources and reasoning behind the mappings
for all 25 checklist questions.

Mappings were reviewed on October 16, 2026 under the accepted Gate 1
policy. They remain project interpretations with documented limitations.
A related framework reference does not establish legal compliance.

This document covers checklist questions. The separate October 29 rule-specific
CSF 2.0/CIS v8.1 source review, including conditional mappings and coverage limits,
is in `rule-framework-review.md`. It does not change checklist weights or claim
new HIPAA/HHS/HICP rule crosswalks. The separate October 30 rule-level
extension is in `healthcare-rule-review.md`; its conditional limits do not
change these question-level weights.

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
- Review weight: 3. Email MFA directly assesses a safeguard identified
  in the Essential Email Security goal's HICP crosswalk.
- Review status: Question-level review completed October 16, 2026
  under the accepted Gate 1 weighting policy. This does not establish
  full CPG compliance or verify phishing-resistant authentication.

## Q02 Email filtering and forwarding

- HICP: Practice 1, 1.S.A, Email System Configuration.
  Printed page 9 supports active, updated spam and antivirus filtering.
- HHS CPG: Email Security, Essential.
- CSF 2.0: Protect, PR.PS-01, secure configuration practices.
  This is a project interpretation for email configuration.
- HIPAA supporting references:
  45 CFR 164.308(a)(5)(ii)(B), protection from malicious software
  (Addressable), supports the malware-filtering component.
  45 CFR 164.308(a)(1)(ii)(B), risk management (Required), provides
  a broader supporting relationship for controls against unauthorized
  email forwarding.
- Mapping limitation: These are project interpretations.
  Neither cited provision specifically requires spam filtering
  or a blanket ban on automatic external forwarding.
- Filtering evidence: HICP supports this component.
- Forwarding evidence: Microsoft documents controls for blocking
  automatic external forwarding in Exchange Online.
- Scope: The Microsoft reference is provider-specific.
  Other email providers need equivalent verified guidance.
  It does not establish a universal legal requirement.
- Coverage: Q02 combines filtering and forwarding controls.
  Yes means both are in place; No means either is absent;
  Unknown means no confirmed failure but at least one is unverified.
- Review weight: 3. Filtering and forwarding restrictions directly
  assess email-security controls related to the Essential Email
  Security goal.
- Review status: Weight reviewed October 16, 2026 under the accepted
  Gate 1 policy. Forwarding guidance remains provider-specific;
  HIPAA references are supporting relationships, not direct
  requirements for these email settings.
  

Supplementary forwarding source:
https://learn.microsoft.com/en-us/defender-office-365/outbound-spam-policies-external-email-forwarding

## Sources for Q01 and Q02

- HICP Technical Volume 1, printed pages 9–10:
  https://hhscyber.hhs.gov/Documents/HICP/tech-vol1-508.pdf
- HHS CPG Essential goals, Email Security and Multifactor Authentication:
  https://hhscyber.hhs.gov/cybersecurity-performance-goals.html
- NIST CSF 2.0, Appendix A, PR.AA-03 and PR.PS-01:
  https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf
- HIPAA technical safeguards:
  https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.312
- HIPAA administrative safeguards, supporting Q02 interpretation:
  https://www.ecfr.gov/current/title-45/section-164.308

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
- Review weight: 1. The current question does not directly assess
  an Essential goal under the accepted Gate 1 policy.
- Review status: Mapping and weight reviewed October 16, 2026
  under the accepted Gate 1 policy. Coverage limitations above
  remain part of the mapping; this is not a compliance determination.

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
- Review weight: 1 under the accepted Gate 1 policy because the
  current question only partially assesses the Essential goal.
- Review status: Mapping and weight reviewed October 16, 2026
  under the accepted Gate 1 policy. Coverage limitations above
  remain part of the mapping; this is not a compliance determination.

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
- Review weight: 1. The current question does not directly assess
  an Essential goal under the accepted Gate 1 policy.
- Review status: Mapping and weight reviewed October 16, 2026
  under the accepted Gate 1 policy. Coverage limitations above
  remain part of the mapping; this is not a compliance determination.

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
- Review weight: 3. Individual staff logins directly assess a safeguard
  related to the Essential Unique Credentials goal.
- Review status: Question-level weight reviewed October 16, 2026
  under the accepted Gate 1 policy. This question does not establish
  password uniqueness across systems or complete credential security.

## Q07 Multifactor authentication for clinical systems

- HICP: Practice 3, sub-practice 3.S.A, printed page 18.
  Practice 2, sub-practice 2.S.A, printed page 15 also supports MFA.
- HHS CPG: Multifactor Authentication, Essential.
- CSF 2.0: Protect, PR.AA-03, authentication.
- HIPAA: 45 CFR 164.312(d), person or entity authentication.
- Coverage: The question checks several systems together.
  One unprotected applicable system means the answer is No.
  It does not verify phishing resistance.
- Review weight: 3. Requiring MFA for applicable clinical systems
  and remote access directly assesses the authentication safeguard
  in the Essential Multifactor Authentication goal.
- Review status: Question-level weight reviewed October 16, 2026
  under the accepted Gate 1 policy. The HHS goal emphasizes
  internet-accessible assets and accounts; ClinicShield asks more
  broadly. This answer does not verify phishing resistance.

## Q08 Removing access when staff leave

- HICP: Practice 3, sub-practice 3.S.A, printed page 17.
- HHS CPG: Revoke Credentials for Departing Workforce Members,
  Including Employees, Contractors, Affiliates, and Volunteers, Essential.
- CSF 2.0: Protect, PR.AA-01 and PR.AA-05, identity and access management.
- HIPAA: 45 CFR 164.308(a)(3)(ii)(C), termination procedures.
- Coverage: Same-day removal is ClinicShield's operational benchmark.
  HICP recommends immediate removal; same-day action may leave a gap.
  The cited HIPAA provision does not specify a same-day deadline.
- Review weight: 3. Disabling departing staff accounts directly
  assesses the Essential goal for revoking workforce credentials.
- Review status: Question-level weight reviewed October 16, 2026
  under the accepted Gate 1 policy. Same-day removal is ClinicShield's
  benchmark and must not justify delaying access removal when
  immediate revocation is needed.

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
- Review weight: 1. The current question does not directly assess
  an Essential goal under the accepted Gate 1 policy.
- Review status: Mapping and weight reviewed October 16, 2026
  under the accepted Gate 1 policy. Coverage limitations above
  remain part of the mapping; this is not a compliance determination.

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
- Review weight: 3. Creating and protecting backups directly assesses
  backup safeguards identified in the Essential Basic Incident
  Planning and Preparedness goal's HICP crosswalk.
- Review status: Question-level weight reviewed October 16, 2026.
  Daily frequency is a project benchmark; a Yes answer does not
  establish complete recovery readiness.

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
- Review weight: 3. Restoration testing directly checks whether
  backups can support recovery, within the Essential Basic Incident
  Planning and Preparedness goal's backup-strategy relationship.
- Review status: Question-level weight reviewed October 16, 2026.
  The six-month interval is a project benchmark. Restoring one file
  does not establish complete disaster-recovery capability.

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
- Review weight: 1 under the accepted Gate 1 policy because the
  current question only partially assesses the Essential goal.
- Review status: Mapping and weight reviewed October 16, 2026
  under the accepted Gate 1 policy. Coverage limitations above
  remain part of the mapping; this is not a compliance determination.

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
- Review weight: 1. No direct Essential goal mapping is established
  for the current question under the accepted Gate 1 policy.
- Review status: Question-level weight reviewed October 16, 2026.
  Supporting framework references do not establish full compliance.

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
- Review weight: 1. No direct Essential goal mapping is established
  for the current question under the accepted Gate 1 policy.
- Review status: Question-level weight reviewed October 16, 2026.
  Supporting framework references do not establish full compliance.

## Q15 Separate guest Wi-Fi

- HICP: Practice 6, 6.S.A, Network Segmentation, printed page 24;
  6.S.B, Physical Security and Guest Access, printed page 25.
- HHS CPG: Network Segmentation, Enhanced.
- CSF 2.0: Protect, PR.IR-01, restricting unauthorized network access.
- HIPAA: 45 CFR 164.312(a)(1), access control;
  supporting project interpretation.
- Coverage: Guest separation is one part of network segmentation.
  Different network names alone do not prove access is restricted.
- Review weight: 1. No direct Essential goal mapping is established
  for the current question under the accepted Gate 1 policy.
- Review status: Question-level weight reviewed October 16, 2026.
  Supporting framework references do not establish full compliance.

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
- Review weight: 1 under the accepted Gate 1 policy because the
  current question only partially assesses the Essential goal.
- Review status: Mapping and weight reviewed October 16, 2026
  under the accepted Gate 1 policy. Coverage limitations above
  remain part of the mapping; this is not a compliance determination.

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
- Review weight: 3. MFA for enabled remote access directly assesses
  the Essential Multifactor Authentication goal.
- Rule R07 must use this corrected interpretation.
- Synthetic Q17 scenario assumptions are documented in samples/EXPECTED.md.
- Review status: Wording approved by Benjamin at Gate 1.
  Question-level weight reviewed October 16, 2026.
  R07 implementation remains pending; fictional sample assumptions
  are recorded in samples/EXPECTED.md.

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
- Review weight: 1 under the accepted Gate 1 policy because the
  current question only partially assesses the Essential goal.
- Review status: Mapping and weight reviewed October 16, 2026
  under the accepted Gate 1 policy. Coverage limitations above
  remain part of the mapping; this is not a compliance determination.

## Q19 Checking installed updates

- HICP: Practice 7, 7.S.A, printed page 26;
  Practice 2, 2.S.A provides supporting patch guidance.
- HHS CPG: Mitigate Known Vulnerabilities, Essential;
  partial relationship.
- CSF 2.0: Protect, PR.PS-02, software maintenance.
- HIPAA: 45 CFR 164.308(a)(1)(ii)(B), risk management.
- Coverage: Monthly verification is ClinicShield's benchmark.
  It must not delay urgent vulnerability remediation.
- Review weight: 1 under the accepted Gate 1 policy because the
  current question only partially assesses the Essential goal.
- Review status: Mapping and weight reviewed October 16, 2026
  under the accepted Gate 1 policy. Coverage limitations above
  remain part of the mapping; this is not a compliance determination.

## Q20 Written incident plan

- HICP: Practice 8, 8.S.A, Incident Response, printed pages 27–29.
- HHS CPG: Basic Incident Planning and Preparedness, Essential.
- CSF 2.0: Identify, ID.IM-04, establishing and maintaining plans.
  Respond, RS.MA-01, is related to executing those plans.
- HIPAA: 45 CFR 164.308(a)(6)(i), security incident procedures.
- Coverage: A short plan is a starting point. This question does not
  verify exercises, complete playbooks, or successful execution.
- Review weight: 3. A written response plan directly assesses the
  Essential Basic Incident Planning and Preparedness goal.
- Review status: Question-level weight reviewed October 16, 2026.
  Plan completeness, exercises, and execution are not verified.

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
- Review weight: 3. Knowing how and where to report security problems
  directly assesses a staff behavior related to Essential Basic
  Cybersecurity Training and incident preparedness.
- Review status: Question-level weight reviewed October 16, 2026.
  The answer does not verify that reports are acted on or documented.

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
- Review weight: 1. The current question does not directly assess
  an Essential goal under the accepted Gate 1 policy.
- Review status: Mapping and weight reviewed October 16, 2026
  under the accepted Gate 1 policy. Coverage limitations above
  remain part of the mapping; this is not a compliance determination.

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
- Review weight: 1. No direct Essential goal mapping is established
  for the current question under the accepted Gate 1 policy.
- Gate 1 decision: Exclude Q23 from the Safeguards denominator only
  when the clinic explicitly confirms it has no medical devices.
  An incomplete inventory or Unknown answer does not justify exclusion.
- Review status: Applicability policy accepted October 16, 2026;
  input and scoring implementation remain pending.

## Q24 Security responsibility and risk analysis

- HICP: Practice 10, 10.S.A, printed pages 31–32;
  10.S.B, printed pages 33–34.
- HHS CPG: No direct Essential mapping confirmed for both components.
- CSF 2.0: Govern, GV.RR-02;
  Identify, ID.RA-04 and ID.RA-05.
- HIPAA: 45 CFR 164.308(a)(2), assigned security responsibility;
  164.308(a)(1)(ii)(A), risk analysis.
- Coverage: The 12-month interval is ClinicShield's benchmark.
  Risk analysis must also respond to relevant changes.
- Follow-ups: Q24a records security responsibility.
  Q24b records the recent documented risk analysis.
- Combined answer: Yes if both are Yes; No if either is No;
  Unknown otherwise. Score Q24 once.
- Rule evidence: R20 uses Q20 and Q24a.
  R22 uses Q24b. Do not infer both gaps from Q24 alone.
- Sample follow-ups are stored in followups.json.
  Tests verify consistency with each sample's combined answer.
- Review weight: 1. The current question does not directly assess
  an Essential goal under the accepted Gate 1 policy.
- Review status: Follow-up design documented;
  engine and export implementation pending.

## Q25 Staff security training

- HICP: Practice 10, 10.S.C, Security Awareness and Training,
  printed page 35 supports onboarding and annual training.
- HHS CPG: Basic Cybersecurity Training, Essential.
- CSF 2.0: Protect, PR.AT-01, staff awareness and training.
- HIPAA: 45 CFR 164.308(a)(5)(i), security awareness and training.
- Coverage: Completion does not prove effectiveness.
  The cited HIPAA provision does not itself specify an annual interval.
- Review weight: 3. Staff security training directly assesses the
  Essential Basic Cybersecurity Training goal.
- Review status: Question-level weight reviewed October 16, 2026.
  Annual frequency is a project benchmark; completion alone does
  not demonstrate training effectiveness.

## Sources for Q23 to Q25

- HICP Technical Volume 1, practices 5, 6, 9, and 10:
  https://hhscyber.hhs.gov/Documents/HICP/tech-vol1-508.pdf
- HHS CPG goal descriptions:
  https://hhscyber.hhs.gov/cybersecurity-performance-goals.html
- NIST CSF 2.0, Appendix A:
  https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf
- HIPAA administrative safeguards:
  https://www.ecfr.gov/current/title-45/section-164.308

## Gate 1 Review Decisions

Benjamin accepted the weighting policy by email on October 16, 2026.
Primrose completed the question-level weight review under that policy.

### Reviewed weights

Weight 3:
Q01, Q02, Q06, Q07, Q08, Q10, Q11, Q17, Q20, Q21, Q25.

Weight 1:
Q03, Q04, Q05, Q09, Q12, Q13, Q14, Q15, Q16, Q18, Q19,
Q22, Q23, Q24.

These are ClinicShield scoring choices, not weights assigned by HHS.
A direct safeguard relationship does not establish complete CPG
coverage or legal compliance.

### Accepted checklist decisions

- Q17 requires MFA for every enabled remote-access connection.
  Apply the same interpretation in R07.
- Q18 includes valid extended security-update coverage.
- Q24 uses separate responsibility and risk-analysis follow-ups,
  while the combined question is scored once.
- Q23 is excluded from the Safeguards denominator only when the clinic
  explicitly confirms that it has no medical devices.
  Unknown does not qualify for exclusion.

### Remaining work

- Implement the reviewed weights and Q23 applicability in scoring.
- Implement and test the accepted cloud-entity, unmatched-host,
  exposure, and duplicate-evidence scoring approach.
- Calibrate synthetic clinic scores and record any justified changes.
- Q02 now records supporting HIPAA references and their limitations.
  Do not present them as specific mandates for the email settings.
- Preserve documented coverage gaps in rule references and reports.
  Revisit mappings when question wording or official sources change.

See docs/gate-1-review.md for the decision record.
