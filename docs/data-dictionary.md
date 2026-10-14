# ClinicShield Data Dictionary

ClinicShield accepts inventories of devices, software, and network
services. Patient records and personal information are prohibited.

These schemas define the validation we will implement.
The current templates contain fictional examples.

## General rules

- Preserve canonical column names.
- Required fields must contain a value.
- Use Unknown only where the field permits it.
- Trim leading and trailing spaces from values.
- Normalize headers before checking for prohibited fields.
- Missing information must never be interpreted as safe.
- Reject duplicate asset IDs in the assets inventory.
- Validate links between inventories.
- Process uploaded content in memory without saving or logging it.

## Assets inventory

One row per device.

| Field | Required | Type or allowed values |
| --- | --- | --- |
| asset_id | Yes | Unique nonempty text |
| asset_name | Yes | Nonempty text |
| asset_type | Yes | workstation, laptop, server, tablet, phone, printer, network_device, medical_device, iot, other |
| location | No | Text |
| owner_role | No | Role description, not a person's name |
| os_name | Yes | Text; Unknown if not known |
| os_version | Yes | Text; Unknown if not known |
| touches_phi | Yes | Y, N, Unknown |
| internet_facing | Yes | Y, N, Unknown |
| portable | No | Y or N; infer from asset type when omitted |
| encrypted | Yes | Y, N, Unknown |
| auto_update | No | Y, N, Unknown |
| last_patched | No | Valid YYYY-MM-DD date or blank |
| network_segment | No | Text; examples: clinic, guest, medical, management, unknown |
| notes | No | Text without patient or personal information |

PHI means protected health information. touches_phi records whether
a device accesses it; the inventory must not contain that information.

When portable is omitted, laptop, tablet, and phone default to Y.
Other asset types default to N.

Proposed asset_name aliases: Device, Computer name.
Hostname is ambiguous between an asset label and a network host;
confirm its meaning before mapping it automatically.

## Software inventory

One row per application on a device or per cloud service.

| Field | Required | Type or allowed values |
| --- | --- | --- |
| asset_id | No | Existing asset ID; CLOUD or blank for a cloud service |
| vendor | Yes | Nonempty text |
| product | Yes | Nonempty text |
| version | Yes | Text or Unknown |
| purpose | Yes | ehr, practice_management, billing, email, telehealth, remote_access, browser, antivirus, backup, office, imaging, messaging, other |
| deployment | Yes | local or cloud |
| touches_phi | Yes | Y, N, Unknown |
| mfa_enabled | Yes | Y, N, NA, Unknown |
| auto_update | No | Y, N, Unknown |
| baa_signed | No | Y, N, NA, Unknown |
| notes | No | Text without patient or personal information |

EHR means electronic health record.
MFA means multifactor authentication.
BAA means Business Associate Agreement.

A supplied device asset_id must match the assets inventory.
CLOUD is reserved for cloud services.

Unknown versions produce an uncertainty finding, not a safe result.
NA means not applicable and must not be treated as Yes.

Proposed aliases
- Software vendor maps to vendor.
- Software name maps to product.
- Software version maps to version.
- Device ID maps to asset_id.

## Services inventory

One row per listening network service. This inventory is optional.

| Field | Required | Type or allowed values |
| --- | --- | --- |
| asset_id | Yes | Existing asset ID, or host address if the asset is unknown |
| host | No | Internal IP address or hostname |
| port | Yes | Integer from 1 to 65535 |
| protocol | Yes | tcp or udp |
| service | Yes | rdp, smb, ssh, http, https, ftp, telnet, vnc, dicom, other |
| product | No | Text from the service banner |
| version | No | Text or Unknown |
| exposure | Yes | internal, internet, unknown |

Use an existing asset_id when the host is in the assets inventory.
If only a host address is available, flag the unmatched asset link
for review. Do not invent its security settings.

Unknown exposure must not be interpreted as internal or safe.
A listening port alone does not prove internet exposure.

Proposed aliases
- Device ID maps to asset_id.
- IP address maps to host.
- Port number maps to port.
- Transport maps to protocol.
- Service name maps to service.

## Nmap XML input

ClinicShield may parse an existing Nmap XML file.
It must never initiate a network scan.

Before upload, require this confirmation:

"I confirm this scan was run on a network my organization owns
or has written permission to scan."

Map parsed hosts and services into the services schema.
Nmap output alone does not establish internet exposure.

## Patient information rejection

Check headers before reading inventory rows into the assessment engine.
For spreadsheets, check every sheet, including hidden sheets.

Reject headers containing any of these terms, ignoring letter case:

patient, pt_name, patient_name, first_name, last_name, dob,
date_of_birth, mrn, medical_record, ssn, social_security,
diagnosis, dx, icd, insurance_id, member_id, policy_number,
phone, email_address, address

Trim header whitespace and normalize spaces and hyphens to underscores
before matching. Apply this check before alias mapping.

Display this rejection message:

"This file looks like it contains patient or personal information.
ClinicShield only needs information about devices, software, and
settings. Please remove those columns and try again."

Reject the entire upload if any prohibited header is found.
Do not display, save, or log the rejected file's contents.

Header checks cannot guarantee that a file contains no personal
information. Keep the upload warning visible and instruct users
to check all values, including notes, before uploading.

Some aliases, such as IP address, conflict with the address blocklist.
Reject these headers under the current policy and ask users to use
the canonical host column instead. Resolve alias conflicts before
implementing automatic header mapping.

## Checklist follow-up answers

Each sample clinic has a followups.json file containing:

- Q24a: Whether a named person is responsible for security.
- Q24b: Whether a risk analysis was completed and documented
  in the last 12 months.

Allowed answers are Yes, No, and Unknown.
Both keys are required in the current sample format.

Derive the combined Q24 answer:
- Yes when both follow-ups are Yes.
- No when either follow-up is No.
- Unknown otherwise.

Score Q24 once. Do not add scoring weight for Q24a or Q24b.

Reject a supplied combined Q24 answer that conflicts with its follow-ups.
For older inputs without follow-ups, request the missing answers.
Do not infer both missing safeguards from Q24 = No.

Use Q24a as evidence for missing security responsibility.
Use Q24b as evidence for a missing recent documented risk analysis.

The future checklist export must include these follow-up answers
and a schema version so they can be restored correctly.

## Implemented input limits

- Maximum uploaded file size: 10 MiB (10,485,760 bytes).
- Maximum checklist or follow-up JSON file size: 64 KiB (65,536 bytes).
- Maximum CSV data records: 10,000, including blank records.
- Maximum columns: 50.
- Maximum header or cell value length: 10,000 characters.
- Maximum workbook sheets: 20, including hidden sheets.
- Maximum workbook rows per sheet: 10,001, including the header.
- Maximum workbook archive components: 1,000.
- Maximum total decompressed workbook size: 50 MiB (52,428,800 bytes).

Workbook row and column limits include cells retained through formatting.
Remove unused rows and columns if formatting makes a sheet exceed a limit.

Excel inventory cells must contain values, not formulas or Excel errors.
Date cells must contain a date without a time.
Encrypted workbook archives and duplicate archive components are rejected.

Assessment inputs use separate CSV or JSON inventories, or an Excel workbook.
The assets and software inventories are required; services are optional.
An Excel services sheet may contain headers only. An uploaded services
CSV must contain at least one data row.

Nmap XML requires explicit authorization confirmation. Only confirmed
open ports on active hosts are imported. Scan results retain unknown
exposure and unmatched asset links for review.

These checks do not guarantee that uploaded values contain no personal
information. Review all values, including notes, before uploading.

## Explicit scan-to-asset mapping

The assessment reader accepts an optional scan_host_to_asset dictionary
when Nmap XML is supplied.

Each key is a scanned host IP address. Each value is an existing device
asset_id. For example:

    {"192.0.2.2": "WH-SRV03"}

This example links the fictional lab host to the fictional Westside
asset. It is an explicit test mapping, not evidence about a real clinic.

Mapping validates IP addresses, normalizes IPv6 notation, and rejects
duplicate normalized hosts, hosts absent from the imported scan services,
unknown device IDs, and the reserved CLOUD marker.

All imported services for a mapped host receive the selected asset_id.
Their host address, port, service details, and exposure remain unchanged.
Mapping does not establish internet exposure.

Unmapped services remain available and are flagged for asset-link review.
Original service objects are not modified.

Mapping requires Nmap XML and does not bypass scan authorization.
The application must not guess mappings from names or service banners.

## Implemented header aliases

CSV and Excel inventory readers support these aliases:

| Inventory | Accepted alias | Canonical field |
| --- | --- | --- |
| Assets | Device, Computer name | asset_name |
| Software | Software vendor | vendor |
| Software | Software name | product |
| Software | Software version | version |
| Software | Device ID | asset_id |
| Services | Device ID | asset_id |
| Services | Port number | port |
| Services | Transport | protocol |
| Services | Service name | service |

Header matching ignores case, trims surrounding whitespace, and converts
spaces and hyphens to underscores.

Privacy checks run on original headers before alias mapping.
Columns that resolve to the same canonical field are rejected.

IP address remains prohibited under the current address blocklist;
use host instead. Hostname remains unsupported because its meaning
is ambiguous. Unsupported columns are rejected.

## JSON inventory format

Assets, software, and services may each be supplied as a UTF-8 JSON
array of objects. Object keys use the canonical fields or supported
header aliases. For example, a services inventory:

```json
[
  {
    "asset_id": "TEST-01",
    "host": "192.0.2.2",
    "port": 8080,
    "protocol": "tcp",
    "service": "http",
    "exposure": "unknown"
  }
]
```

Each inventory must contain at least one entry. Omit the services file
when no services inventory is available.

JSON inventories use the same schemas, privacy header checks, aliases,
and asset-link validation as CSV inventories.

Duplicate keys, nested field objects or arrays, invalid answers,
non-finite numbers, and duplicate asset IDs are rejected.

Each JSON inventory is limited to 10 MiB and 10,000 entries.
Header and string value limits also apply. The smaller 64 KiB JSON
limit applies only to checklist and follow-up files.

Each inventory may use CSV or JSON, allowing different formats for
different inventories. Do not supply both formats for the same inventory.
An Excel workbook cannot be combined with separate CSV or JSON
inventories. Authorized Nmap XML may accompany either input path.