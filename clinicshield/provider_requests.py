"""Draft requests for human review; never send or execute remediation."""

REQUESTS = {
    "R01": "review the applicable CVE and KEV entry, and agree a vendor-supported remediation or mitigation plan",
    "R02": "review the applicable CVE and agree a vendor-supported remediation or mitigation plan",
    "R03": "verify OS support and extended-support coverage, and plan a supported replacement or documented mitigation",
    "R04": "verify application support and plan a supported release or documented mitigation",
    "R05": "review the reported encryption gap and agree a supported encryption plan with recovery arrangements",
    "R06": "review the internet-facing administration service, confirm its business need, and agree restrictions on unnecessary access",
    "R07": "review remote-access necessity and MFA separately, and agree changes for the reported gaps",
    "R08": "review SMB on the unsupported OS and agree a supported OS plan without treating SMB presence as a confirmed exploit",
    "R09": "review the Telnet listener and agree a supported secure-management alternative where appropriate",
    "R10": "review the unchanged default administrator password and agree a controlled credential change",
    "R11": "review the reported medical-device separation gap with the clinical/device vendor and agree safe network restrictions",
    "R12": "review the reported email MFA gap and agree protection for the affected accounts",
    "R13": "review the reported clinical-application MFA gap with its vendor and agree a supported authentication plan",
    "R14": "review shared-account use and agree individually attributable access with appropriate clinical continuity arrangements",
    "R15": "review the reported antivirus gap and agree supported protection and update settings",
    "R16": "review backup frequency, separation and restore testing individually, and agree a plan for the reported gaps",
    "R17": "ask the responsible privacy/security lead to assess agreement applicability and obtain or review the appropriate vendor agreement",
    "R18": "review guest-network separation and agree restrictions protecting clinic systems",
    "R19": "check the router safeguards individually and agree a plan for the settings actually found deficient",
    "R20": "review incident planning and assigned security responsibility separately, and document the reported gaps",
    "R21": "review staff reporting and breach-notification preparation separately with the responsible lead, without assuming a breach or notification obligation",
    "R22": "ask the responsible security lead to arrange and document a scoped risk analysis",
    "R23": "ask the responsible manager to arrange relevant staff security training and retain completion records",
    "R24": "verify the installed software version and patient-information scope before reassessing vulnerability applicability",
}


def provider_requests(occurrences, entity_id):
    """Use confirmed evidence only, including separate branches of combined rules."""
    requests = []
    for occurrence in occurrences:
        finding = occurrence.finding
        if finding.observation.status != "confirmed":
            continue
        rule = finding.rule.rule_id
        details = dict(finding.observation.evidence)
        target = entity_id
        identity = [details.get(key, "") for key in ("vendor", "product", "version", "vulnerability_id")]
        identity = [value for value in identity if value]
        if identity:
            target += " / " + " / ".join(identity)
        task = REQUESTS[rule]
        if rule == "R16":
            parts = []
            if details.get("Q10") == "No":
                parts.append("review backup frequency and separation individually, identifying which part failed")
            if details.get("Q11") == "No":
                parts.append("arrange a controlled restore test and record its outcome")
            if parts:
                task = "; ".join(parts)
        if rule == "R20":
            parts = []
            if details.get("Q20") == "No":
                parts.append("document an incident-response plan")
            if details.get("Q24a") == "No":
                parts.append("name the person responsible for security")
            if parts:
                task = "; ".join(parts)
        if rule == "R21":
            parts = []
            if details.get("Q21") == "No":
                parts.append("document how staff report suspected security problems")
            if details.get("Q22") == "No":
                parts.append("arrange a qualified review of breach-notification preparation without assuming a breach or notification obligation")
            if parts:
                task = "; ".join(parts)
        request = (f"For {target} ({rule}), please {task}. "
                   "Please provide dated evidence for reassessment and confirm the owner, "
                   "cost estimate and a safe timetable before changes.")
        if request not in requests:
            requests.append(request)
    return sorted(requests)
