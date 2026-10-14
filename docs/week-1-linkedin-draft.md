# Week 1 LinkedIn Draft

I’m building ClinicShield with Chicago Education Advocacy Cooperative
(ChiEAC): a free, open-source cyber safety checkup for small healthcare
providers.

The goal is to turn equipment inventories and a plain-language security
checklist into an explained score and a practical Fix First plan.

This week, I built the foundation:
- CSV and Excel inventory templates.
- Three fictional clinic datasets for testing.
- A 25-question checklist with draft framework mappings.
- Patient-information header checks and automated tests.
- An isolated Linux lab and an authentic Nmap test fixture.

All 17 current tests pass. I also reviewed HICP, the HHS Cybersecurity
Performance Goals, and the assigned NIST guidance.

One lesson: a security question needs precise wording. A VPN alone
doesn’t establish multifactor authentication, and one combined answer
can hide two different missing safeguards.

Next is building and testing the input-validation pipeline.
The assessment engine and user interface are still ahead.

ClinicShield will support risk analysis; it will not certify HIPAA
compliance or initiate network scans.

Thank you to @Chicago Education Advocacy Cooperative and
@Benjamin Drury for their guidance.

Repository:
https://github.com/PrimroseZoe1998/clinicshield

#Cybersecurity #HealthcareCybersecurity #OpenSource