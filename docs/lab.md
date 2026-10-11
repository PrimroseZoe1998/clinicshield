# ClinicShield Authorized Lab

## Purpose

Generate an authentic Nmap XML fixture for service-parser tests.
The scanner and target are owned and controlled by the developer.

## Environment

- Windows 11 Home on ARM64.
- Ubuntu running under Windows Subsystem for Linux.
- Two Linux network namespaces connected by a virtual Ethernet pair.
- Scanner: clinicshield-scan, 192.0.2.1/30.
- Target: clinicshield-target, 192.0.2.2/30.
- Both namespaces have only the connected lab route and no default route.

This uses network namespaces instead of the brief's separate VMs.
They isolate networking but share the Linux kernel and filesystem.
This lab is for benign test services, not untrusted malware.

## Test service

Python HTTP server bound to 192.0.2.2 on TCP port 8080.
It serves an empty directory at /tmp/clinicshield-web.

## Scan command

Run manually in Ubuntu:

sudo ip netns exec clinicshield-scan nmap -sV -n --top-ports 1000 -oX /mnt/c/Users/zmang/ClinicShield/samples/lab_scan.xml 192.0.2.2

ClinicShield itself never starts a scan.

## Observed result

- One host up at 192.0.2.2.
- TCP port 8080 open.
- HTTP service identified as SimpleHTTPServer 0.6, Python 3.14.4.
- The other 999 scanned TCP ports were closed.

The scan does not establish internet exposure or prove the host is safe.

## Westside fixture mapping

For parser tests only, map lab host 192.0.2.2 to WH-SRV03.
Set exposure to internal based on the documented lab topology.

This mapping does not mean a real Westside clinic was scanned.
Keep the lab-derived service separate from the synthetic services CSV
until ingestion can combine evidence without duplication.

## Fixture

samples/lab_scan.xml contains the authentic scan output.
Review its contents before committing it.