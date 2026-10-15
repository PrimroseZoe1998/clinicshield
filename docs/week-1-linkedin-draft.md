# Week 1 LinkedIn Draft

Planned publication: October 16, 2026.
Status: Draft — not published.

## Post

What does a small clinic do when it has patient appointments to manage
but no dedicated cybersecurity team?

This week, I started building ClinicShield through my fellowship with
Chicago Education Advocacy Cooperative (ChiEAC). It will be a free,
open-source tool that turns a clinic’s technology inventory and a short
security checklist into a plain-language “Fix First” plan.

The foundation is in place: three fictional clinic datasets, inventory
templates, and readers for CSV, JSON, Excel, and existing Nmap scan
results. The code now passes 334 automated tests.

One lesson: a scan can show an open service, but that alone does not
prove it is exposed to the internet. ClinicShield preserves that
uncertainty instead of guessing.

The application does not run network scans. Its input readers check
for prohibited personal-information headers, but users must still
review every value before uploading.

Next: review the framework mappings and scoring decisions, then build
the vulnerability intelligence and rule engine.

Thank you to @Chicago Education Advocacy Cooperative and
@Benjamin Drury for supporting this work.

#HealthcareCybersecurity #VulnerabilityManagement #GRC #NIST #ChiEAC

## Before publishing

- Attach a screenshot of the passing tests or fictional sample data.
- Check the screenshot for personal details, notifications, and secrets.
- Select the actual organization and person from LinkedIn’s suggestions
  so both mentions resolve.
- Add the repository link:
  https://github.com/PrimroseZoe1998/clinicshield
- Publish on October 16 and record the post link afterward.