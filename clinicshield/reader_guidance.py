"""Shared plain-language guidance for the app and human-readable reports."""
PRIVACY_NOTICE = (
    "Do not upload patient data, passwords or recovery codes. "
    "Your inputs stay in this session. They are not saved to disk. "
    "ClinicShield does not scan your network."
)
SCORE_GUIDE = (
    "Safeguards shows how your answers scored. Exposure starts at 100 and "
    "drops for confirmed technical findings. A higher score does not prove "
    "that your systems are safe. Provisional means there are gaps or checks still open."
)
SCOPE_NOTICE = (
    "Missing evidence is not proof of safety. Scores use only the data supplied. "
    "Draft mappings may still need review. This prototype does not prove that a "
    "clinic is safe, meets health care law or is ready for live use."
)
PRIORITY_GUIDE = (
    "Priority is finding points divided by effort. It does not predict a score "
    "gain or a drop in real risk. Check costs and the work needed before you start."
)
TABLE_GUIDE = (
    "Confirmed findings come first. Items that need review come next. "
    "Each group is sorted by severity, then Exposure points before caps. "
    "This is not a measure of real risk reduction. Match the Ref code to full details below."
)
GLOSSARY = (
    ("IT / NA / VPN / SMB / BAA", "Information technology / not applicable / virtual private network / Server Message Block file sharing / Business Associate Agreement. A VPN alone does not prove that access is safe."),
    ("Finding", "A gap or a check raised by the supplied data. Confirmed means supported by that data, not an on-site check."),
    ("Coverage", "What the tool could check. Unassessed means it could not check; it does not mean safe."),
    ("Entity", "A device, cloud service or other item used to group scores. A cap sets the most points one item can lose."),
    ("Effort", "1: under an hour and free. 2: a day or a small cost. 3: vendor help, budget or several weeks."),
    ("CSV / JSON / XLSX / XML / TXT / PDF", "Comma-separated values / JavaScript Object Notation / Excel workbook / Extensible Markup Language / plain text / Portable Document Format. These are file types."),
    ("OS / MFA / EHR / PHI", "Operating system / multifactor authentication / electronic health record / protected health information. Do not upload patient data."),
    ("CVE / NVD / CVSS", "Common Vulnerabilities and Exposures: weakness IDs. National Vulnerability Database: public weakness records. Common Vulnerability Scoring System: a source severity score."),
    ("CISA / KEV / EPSS", "Cybersecurity and Infrastructure Security Agency / Known Exploited Vulnerabilities catalog / Exploit Prediction Scoring System. KEV lists flaws used in attacks. EPSS estimates a flaw's chance of use in attacks over 30 days; it does not prove your systems are affected."),
    ("HHS / HICP / CPG", "US Department of Health and Human Services / Health Industry Cybersecurity Practices / Cybersecurity Performance Goals. Project links to these sources may be partial or still need review."),
    ("NIST / CSF / CIS / HIPAA", "National Institute of Standards and Technology / Cybersecurity Framework / Center for Internet Security / Health Insurance Portability and Accountability Act. References do not prove compliance."),
    ("TCP / UDP / TLS / SSH / RDP / HTTP / HTTPS", "Transmission Control Protocol / User Datagram Protocol / Transport Layer Security / Secure Shell / Remote Desktop Protocol / Hypertext Transfer Protocol / HTTP over TLS. These name network methods or services."),
)


def glossary_lines():
    return [f"{term}: {meaning}" for term, meaning in GLOSSARY]
