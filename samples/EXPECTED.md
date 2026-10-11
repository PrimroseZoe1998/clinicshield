# Expected Findings for Synthetic Clinics

All clinic datasets are fictional.
These expectations will become regression tests as rules are implemented.
They are not results from a completed assessment engine.

## Lakeview Family Dental

Files are in lakeview_dental.

### Expected technical findings

- R03: Unsupported operating systems on LV-WS01, LV-WS02,
  and LV-SRV01, which access patient information.
- R05: Encryption is off on the portable device LV-LT01.
- R07: Internal Remote Desktop on LV-SRV01 with Q17 answered No.
- R08: SMB on LV-SRV01, which runs an unsupported operating system.
- R12: Email MFA is disabled.
- R24: Unverified versions on software that accesses patient information.

Validate operating system support status against the dated support cache.
The sample explicitly states that older Windows systems have no
extended security update coverage.

### Expected checklist findings

- R16: Backups exist but have not been test-restored.
- R18: Guest Wi-Fi is not separated.
- R19: Router security question answered No.

Q01 also supports R12. Combine matching evidence rather than
showing duplicate email MFA findings.

### Rule decisions to resolve

LV-RT01 notes state that its default administrator password is unchanged.
R10 may therefore apply as well as R19. Decide how to combine the
shared remediation while preserving both evidence sources.

Unknown software versions must not generate invented CVE matches.
Record Info findings and explain how to obtain the missing versions.

### Score expectation

Target band: Urgent, 0 to 49.

The actual score is pending implementation and calibration.
Any open Critical finding also imposes the ceiling of 69.

## Southside Counseling Collective

Files are in southside_counseling.
No services inventory is supplied; network exposure remains unassessed.

### Expected findings

- R05: Encryption status is Unknown on SC-LT03 and SC-LT05.
- R12: Email MFA is not enabled for every account.
- R16: Backups are not separated from daily work access.
- R17: Missing Business Associate Agreements for Consumer Texting
  and Personal Cloud Drive.
- R20: No written incident plan or named security official.
- R22: No documented risk analysis.
- R24: Unknown versions on software accessing patient information.

Phone operating system support status is unresolved.
Report that uncertainty without inventing vulnerability matches.

Combine checklist and inventory evidence for the same issue.
R20 and R22 may share Q24 evidence but describe distinct actions.

### Score expectation

Target band: At risk, 50 to 69.
Actual score is pending implementation and calibration.
Open Critical findings impose the ceiling of 69.

## Westside Community Health

Files are in westside_health.

### Expected findings

- R03: Unsupported operating systems on WH-MD02 and WH-LT01,
  which access patient information.
- R05: Encryption status is Unknown on portable device WH-LT01.
- R09: Telnet is listening on printer WH-PR01.
- R11: Ultrasound workstation WH-MD02 shares the clinic segment
  with workstations. Its notes explicitly confirm this arrangement.
- R14: A shared nurse-station login, reported by Q06.
- R16: Backups are separated but have not been test-restored.
- R24: Unknown versions on software accessing patient information.

Support status for vendor firmware is unresolved.
Report uncertainty without inventing vulnerability matches.

### Score expectation

Initial target band: At risk, 50 to 69, pending calibration.
Open Critical findings prevent a score above 69.

After the Critical findings are fixed, the target band is
Needs attention, 70 to 84, pending calibration.

### Lab scan fixture

The services CSV is synthetic.
An authentic Nmap XML fixture from an authorized personal lab
has not been added yet.

Do not describe this CSV as evidence of a completed network scan.

## Q17 Remote access scenario assumptions

These are fictional scenario definitions, not verified settings
from real organizations.

### Lakeview Family Dental

Q17 = No.
The server's internal Remote Desktop connection is enabled without MFA.
The separate Remote Support product has MFA, but this does not
protect the server's Remote Desktop connection.
R07 should identify the server issue.

### Southside Counseling Collective

Q17 = Yes.
Remote connections into the clinic's laptops are disabled.
Staff use cloud applications rather than remotely controlling laptops.
Cloud account MFA is assessed separately by Q01 and Q07.

### Westside Community Health

Q17 = Yes.
The campus VPN connection is needed and requires MFA for every user.
Unnecessary remote-access connections are disabled.
The services inventory alone does not prove these settings;
the checklist answer supplies this scenario evidence.

### Rule implementation requirement

R07 must not treat a VPN alone as sufficient protection.
Combine inventory evidence with the corrected Q17 interpretation.
Unknown answers require follow-up and must not establish safety.