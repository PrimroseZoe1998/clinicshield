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

Dataset and expected findings pending.

## Westside Community Health

Dataset and expected findings pending.
Initial Critical findings must keep its score at or below 69.