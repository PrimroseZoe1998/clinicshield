# ClinicShield Security Practices Checklist

Answer each question with Yes, No, or Unknown.
Choose Unknown when you have not checked.

Every question is worded so Yes represents a safer practice.
Unknown does not earn safeguards points and prompts a follow-up action.

Do not enter patient information, passwords, or recovery codes.

## Email protection

### Q01 Multifactor authentication for email

Is multifactor authentication required for every work email account?

Multifactor authentication means using another proof of identity,
such as an authenticator app, in addition to a password.

Why we ask: It helps protect email accounts when passwords are stolen.

### Q02 Email filtering and forwarding

Does your email service filter spam and malware and block automatic
forwarding to outside addresses?

Malware is software designed to damage systems or steal information.

Why we ask: These settings help block harmful messages and prevent
mail from being automatically copied outside the organization.

## Endpoint protection

### Q03 Antivirus protection

Do all computers run an antivirus or endpoint protection product
that updates itself?

Endpoint protection is security software that helps detect and block
harmful activity on a computer.

Why we ask: Updated protection helps detect threats on work computers.

### Q04 Automatic updates

Are operating systems and browsers set to install updates automatically?

Why we ask: Updates fix security weaknesses that attackers can exploit.

### Q05 Portable device encryption

Is every laptop, tablet, and phone that can access patient information
encrypted?

Encryption helps keep stored information unreadable without the
correct key or credentials.

Why we ask: It helps protect information if a device is lost or stolen.

## Access management

### Q06 Individual accounts

Does every staff member have their own login, with no shared accounts?

Why we ask: Individual accounts make it easier to control access
and identify who performed an action.

### Q07 Multifactor authentication for clinical systems

Is multifactor authentication required for your electronic health
record system, billing, telehealth, and any remote access?

An electronic health record system stores and manages patient records.
Telehealth provides care through phone or video services.
Remote access lets someone connect to a work system from another location.

Why we ask: A stolen password should not be enough to access
systems that handle patient information.

### Q08 Removing access when staff leave

When someone leaves, are all their work accounts disabled the same day?

Why we ask: Former staff should no longer be able to access work
systems or patient information.

### Q09 Limiting administrator rights

Are administrator rights limited to people who need them for their role?

Administrator rights allow someone to change important settings
and install software.

Why we ask: Limiting these rights reduces the damage an attacker
or an accidental change can cause.

## Data protection

### Q10 Daily separated backups

Are backups taken at least daily and kept offline or in a separate
account that an attack on your work systems could not access?

A backup is a copy used to recover information if the original is lost.

Why we ask: Protected backups help the practice recover after
ransomware, equipment failure, or accidental deletion.

### Q11 Testing backup recovery

In the last six months, has someone restored a file from backup
to confirm it works?

Why we ask: A backup is useful only if you can recover information
from it when needed.

### Q12 Vendor agreements

Do you have a signed Business Associate Agreement with every vendor
that requires one because it handles patient information for you?

A Business Associate Agreement sets out a vendor's responsibilities
for protecting patient information.

Why we ask: These agreements help clarify how vendors protect
information and respond to problems.

### Q13 Secure disposal

Are old computers, phones, and drives securely wiped or destroyed
before they leave the practice?

Why we ask: Information can remain recoverable on discarded devices,
even after files are deleted.

## Asset management

### Q14 Updated inventory

Do you have a written list of devices and software that access patient
information, reviewed and updated in the last year?

The inventory you prepare for ClinicShield can contribute to this list.

Why we ask: You need to know what you own before you can protect it
or identify missing equipment.

## Network management

### Q15 Separate guest Wi-Fi

Is guest or patient Wi-Fi separate from the network used by your
work computers?

Why we ask: Separating the networks helps limit access from visitor
devices to work systems.

### Q16 Router security

Has the router or firewall's default administrator password been
changed, and has its firmware been updated in the last year?

Firmware is the software built into a device.

Why we ask: Default passwords and outdated firmware can leave
your network open to attackers.

### Q17 Protected remote access

Is remote access to clinic computers turned off unless needed,
and does every enabled remote-access connection require
multifactor authentication?

A virtual private network provides an encrypted connection.
It should also require multifactor authentication; using a VPN
alone does not answer this question.

If remote access is completely disabled, answer Yes.
If any enabled connection lacks multifactor authentication, answer No.
If you have not checked, answer Unknown.

Why we ask: Remote access can give attackers a way into work systems
if it is left open or poorly protected.

## Vulnerability management

### Q18 Supported operating systems

Are all devices running operating systems that still receive
security updates, including any valid extended support coverage?

An operating system is the main software that runs a device,
such as Windows or macOS.

Why we ask: Unsupported systems can retain security weaknesses
that the vendor no longer fixes.

### Q19 Checking installed updates

Does someone check at least monthly that updates were successfully
installed on every machine?

Why we ask: Automatic updates can fail. Checking confirms that
devices received the fixes they need.

## Incident response

### Q20 Written incident plan

Do you have a short written plan explaining who to call and what
to do if ransomware hits or a laptop goes missing?

Ransomware is an attack that locks or steals information and
demands payment.

Why we ask: A prepared plan helps staff respond quickly and
coordinate recovery.

### Q21 Reporting security problems

Does everyone know how to report a suspicious email or a lost device,
and whom to contact?

Why we ask: Early reporting gives the practice more time to limit
damage and protect information.

### Q22 Breach notification preparation

Do you know whom to contact to determine who must be notified,
and by when, if patient information is breached?

Why we ask: A prepared contact and notification process helps the
practice respond promptly and avoid missing required steps.

## Network-connected medical devices

### Q23 Medical device inventory and separation

Are network-connected medical devices listed in your inventory with
their vendor support status, and kept on a separate network where possible?

Examples include imaging equipment, monitors, and dental sensors.

Why we ask: Medical devices can be difficult to update. Knowing their
support status and limiting network access helps manage their risks.

## Security oversight and governance

### Q24 Security responsibility and risk analysis

Is one named person responsible for security, even part time, and has
a security risk analysis been completed and documented in the last
12 months?

A security risk analysis examines how patient information could be
exposed or disrupted and what safeguards are needed.

Answer these two follow-up questions separately:

- Q24a: Is one named person responsible for security?
- Q24b: Has a security risk analysis been completed and documented
  in the last 12 months?

Use Yes, No, or Unknown for each follow-up.

The app derives Q24:
- Yes when both follow-ups are Yes.
- No when either follow-up is No.
- Unknown otherwise.

Score Q24 once. Do not score the follow-ups separately.

Use Q24a to assess missing security responsibility.
Use Q24b to assess a missing recent documented risk analysis.
Do not infer both problems from the combined answer alone.

Why we ask: Clear responsibility and a documented assessment help
the practice identify risks and follow through on fixes.

### Q25 Staff security training

Does every staff member complete security awareness training when
hired and at least once a year?

Why we ask: Training helps staff recognize threats and follow the
practice's security procedures.