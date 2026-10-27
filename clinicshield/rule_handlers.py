from dataclasses import dataclass
from typing import Literal

from clinicshield.schemas import Asset, Service, Software
from clinicshield.checklist_input import ANSWERS, Checklist
from clinicshield.input_limits import InputError
from clinicshield.normalization import normalize_version

@dataclass(frozen=True)
class RuleObservation:
    rule_id: str
    entity_id: str
    status: Literal["confirmed", "needs_review"]
    evidence: tuple[tuple[str, str], ...]


def portable_encryption(asset: Asset) -> RuleObservation | None:
    """Detect R05 gaps using a validated asset."""
    if asset.portable != "Y":
        return None

    if asset.encrypted == "Y":
        return None

    status: Literal["confirmed", "needs_review"]

    if asset.encrypted == "N":
        status = "confirmed"
    else:
        status = "needs_review"

    return RuleObservation(
        rule_id="R05",
        entity_id=asset.asset_id,
        status=status,
        evidence=(
            ("asset_id", asset.asset_id),
            ("portable", asset.portable),
            ("encrypted", asset.encrypted),
        ),
    )

def telnet_service(service: Service) -> RuleObservation | None:
    """Detect explicitly identified TCP Telnet services for R09."""
    if service.protocol != "tcp" or service.service != "telnet":
        return None

    return RuleObservation(
        rule_id="R09",
        entity_id=service.asset_id,
        status="confirmed",
        evidence=(
            ("asset_id", service.asset_id),
            ("host", service.host),
            ("port", str(service.port)),
            ("protocol", service.protocol),
            ("service", service.service),
            ("exposure", service.exposure),
        ),
    )

def individual_accounts(
    checklist: Checklist,
) -> RuleObservation | None:
    """Detect the individual-account safeguard gap reported by Q06."""
    answer = checklist.answers.get("Q06")

    if not isinstance(answer, str) or answer not in ANSWERS:
        raise InputError("R14 requires a valid Q06 answer.")

    if answer == "Yes":
        return None

    status: Literal["confirmed", "needs_review"]

    if answer == "No":
        status = "confirmed"
    else:
        status = "needs_review"

    return RuleObservation(
        rule_id="R14",
        entity_id="assessment",
        status=status,
        evidence=(("Q06", answer),),
    )

def guest_wifi_separation(
    checklist: Checklist,
) -> RuleObservation | None:
    """Detect the guest Wi-Fi separation gap reported by Q15."""
    answer = checklist.answers.get("Q15")

    if not isinstance(answer, str) or answer not in ANSWERS:
        raise InputError("R18 requires a valid Q15 answer.")

    if answer == "Yes":
        return None

    status: Literal["confirmed", "needs_review"]

    if answer == "No":
        status = "confirmed"
    else:
        status = "needs_review"

    return RuleObservation(
        rule_id="R18",
        entity_id="assessment",
        status=status,
        evidence=(("Q15", answer),),
    )

def router_security(
    checklist: Checklist,
) -> RuleObservation | None:
    """Detect the router safeguard gap reported by Q16."""
    answer = checklist.answers.get("Q16")

    if not isinstance(answer, str) or answer not in ANSWERS:
        raise InputError("R19 requires a valid Q16 answer.")

    if answer == "Yes":
        return None

    status: Literal["confirmed", "needs_review"]

    if answer == "No":
        status = "confirmed"
    else:
        status = "needs_review"

    return RuleObservation(
        rule_id="R19",
        entity_id="assessment",
        status=status,
        evidence=(("Q16", answer),),
    )

def documented_risk_analysis(
    checklist: Checklist,
) -> RuleObservation | None:
    """Detect the risk-analysis gap reported specifically by Q24b."""
    answer = checklist.followups.get("Q24b")

    if not isinstance(answer, str) or answer not in ANSWERS:
        raise InputError("R22 requires a valid Q24b follow-up answer.")

    if answer == "Yes":
        return None

    status: Literal["confirmed", "needs_review"]

    if answer == "No":
        status = "confirmed"
    else:
        status = "needs_review"

    return RuleObservation(
        rule_id="R22",
        entity_id="assessment",
        status=status,
        evidence=(("Q24b", answer),),
    )

def incident_readiness(
    checklist: Checklist,
) -> RuleObservation | None:
    """Assess Q20 and Q24a separately without inferring either."""
    plan = checklist.answers.get("Q20")
    responsibility = checklist.followups.get("Q24a")

    for question, answer in (
        ("Q20", plan),
        ("Q24a", responsibility),
    ):
        if not isinstance(answer, str) or answer not in ANSWERS:
            raise InputError(f"R20 requires a valid {question} answer.")

    if plan == "Yes" and responsibility == "Yes":
        return None

    status: Literal["confirmed", "needs_review"]

    if plan == "No" or responsibility == "No":
        status = "confirmed"
    else:
        status = "needs_review"

    return RuleObservation(
        rule_id="R20",
        entity_id="assessment",
        status=status,
        evidence=(
            ("Q20", plan),
            ("Q24a", responsibility),
        ),
    )

def backup_safeguards(
    checklist: Checklist,
) -> RuleObservation | None:
    """Assess Q10 and Q11 without inferring individual backup faults."""
    backups = checklist.answers.get("Q10")
    restore_testing = checklist.answers.get("Q11")

    for question, answer in (
        ("Q10", backups),
        ("Q11", restore_testing),
    ):
        if not isinstance(answer, str) or answer not in ANSWERS:
            raise InputError(f"R16 requires a valid {question} answer.")

    if backups == "Yes" and restore_testing == "Yes":
        return None

    status: Literal["confirmed", "needs_review"]

    if backups == "No" or restore_testing == "No":
        status = "confirmed"
    else:
        status = "needs_review"

    return RuleObservation(
        rule_id="R16",
        entity_id="assessment",
        status=status,
        evidence=(
            ("Q10", backups),
            ("Q11", restore_testing),
        ),
    )

def staff_security_training(
    checklist: Checklist,
) -> RuleObservation | None:
    """Detect the staff training gap reported by Q25."""
    answer = checklist.answers.get("Q25")

    if not isinstance(answer, str) or answer not in ANSWERS:
        raise InputError("R23 requires a valid Q25 answer.")

    if answer == "Yes":
        return None

    status: Literal["confirmed", "needs_review"]

    if answer == "No":
        status = "confirmed"
    else:
        status = "needs_review"

    return RuleObservation(
        rule_id="R23",
        entity_id="assessment",
        status=status,
        evidence=(("Q25", answer),),
    )

def antivirus_protection(
    checklist: Checklist,
) -> RuleObservation | None:
    """Detect the endpoint protection gap reported by Q03."""
    answer = checklist.answers.get("Q03")

    if not isinstance(answer, str) or answer not in ANSWERS:
        raise InputError("R15 requires a valid Q03 answer.")

    if answer == "Yes":
        return None

    status: Literal["confirmed", "needs_review"]

    if answer == "No":
        status = "confirmed"
    else:
        status = "needs_review"

    return RuleObservation(
        rule_id="R15",
        entity_id="assessment",
        status=status,
        evidence=(("Q03", answer),),
    )

def reporting_preparation(
    checklist: Checklist,
) -> RuleObservation | None:
    """Assess Q21 and Q22 without inferring that a breach occurred."""
    reporting = checklist.answers.get("Q21")
    notification = checklist.answers.get("Q22")

    for question, answer in (
        ("Q21", reporting),
        ("Q22", notification),
    ):
        if not isinstance(answer, str) or answer not in ANSWERS:
            raise InputError(f"R21 requires a valid {question} answer.")

    if reporting == "Yes" and notification == "Yes":
        return None

    status: Literal["confirmed", "needs_review"]

    if reporting == "No" or notification == "No":
        status = "confirmed"
    else:
        status = "needs_review"

    return RuleObservation(
        rule_id="R21",
        entity_id="assessment",
        status=status,
        evidence=(
            ("Q21", reporting),
            ("Q22", notification),
        ),
    )

def unknown_software_version(
    software: Software,
    *,
    entity_id: str,
) -> RuleObservation | None:
    """Flag missing version information without confirming a CVE."""
    if not isinstance(entity_id, str) or not entity_id.strip():
        raise InputError("R24 requires a software entry identifier.")

    if software.touches_phi == "N":
        return None

    if normalize_version(software.version) is not None:
        return None

    return RuleObservation(
        rule_id="R24",
        entity_id=entity_id,
        status="needs_review",
        evidence=(
            ("asset_id", software.asset_id),
            ("vendor", software.vendor),
            ("product", software.product),
            ("version", software.version),
            ("deployment", software.deployment),
            ("touches_phi", software.touches_phi),
        ),
    )

def cloud_baa_status(
    software: Software,
    *,
    entity_id: str,
) -> RuleObservation | None:
    """Assess reported agreement status without deciding applicability."""
    if not isinstance(entity_id, str) or not entity_id.strip():
        raise InputError("R17 requires a software entry identifier.")

    if software.deployment != "cloud" or software.touches_phi == "N":
        return None

    if software.touches_phi == "Y" and software.baa_signed == "Y":
        return None

    status: Literal["confirmed", "needs_review"]

    if software.touches_phi == "Y" and software.baa_signed == "N":
        status = "confirmed"
    else:
        status = "needs_review"

    return RuleObservation(
        rule_id="R17",
        entity_id=entity_id,
        status=status,
        evidence=(
            ("asset_id", software.asset_id),
            ("vendor", software.vendor),
            ("product", software.product),
            ("deployment", software.deployment),
            ("touches_phi", software.touches_phi),
            ("baa_signed", software.baa_signed),
        ),
    )

def email_mfa(
    software: Software,
    *,
    entity_id: str,
) -> RuleObservation | None:
    """Assess reported MFA status for email software."""
    if not isinstance(entity_id, str) or not entity_id.strip():
        raise InputError("R12 requires a software entry identifier.")

    if software.purpose != "email":
        return None

    if software.mfa_enabled == "Y":
        return None

    status: Literal["confirmed", "needs_review"]

    if software.mfa_enabled == "N":
        status = "confirmed"
    else:
        status = "needs_review"

    return RuleObservation(
        rule_id="R12",
        entity_id=entity_id,
        status=status,
        evidence=(
            ("asset_id", software.asset_id),
            ("vendor", software.vendor),
            ("product", software.product),
            ("purpose", software.purpose),
            ("deployment", software.deployment),
            ("mfa_enabled", software.mfa_enabled),
        ),
    )

def clinical_system_mfa(
    software: Software,
    *,
    entity_id: str,
) -> RuleObservation | None:
    """Assess reported MFA for the clinical applications in R13."""
    if not isinstance(entity_id, str) or not entity_id.strip():
        raise InputError("R13 requires a software entry identifier.")

    if software.purpose not in {
        "ehr", "practice_management", "billing", "telehealth"
    }:
        return None

    if software.mfa_enabled == "Y":
        return None

    status: Literal["confirmed", "needs_review"]

    if software.mfa_enabled == "N":
        status = "confirmed"
    else:
        status = "needs_review"

    return RuleObservation(
        rule_id="R13",
        entity_id=entity_id,
        status=status,
        evidence=(
            ("asset_id", software.asset_id),
            ("vendor", software.vendor),
            ("product", software.product),
            ("purpose", software.purpose),
            ("deployment", software.deployment),
            ("mfa_enabled", software.mfa_enabled),
        ),
    )

def remote_admin_exposure(
    service: Service,
) -> RuleObservation | None:
    """Assess reported exposure of explicitly identified remote services."""
    if service.protocol != "tcp" or service.service not in {
        "rdp", "vnc", "ssh", "telnet"
    }:
        return None

    if service.exposure == "internal":
        return None

    status: Literal["confirmed", "needs_review"]

    if service.exposure == "internet":
        status = "confirmed"
    else:
        status = "needs_review"

    return RuleObservation(
        rule_id="R06",
        entity_id=service.asset_id,
        status=status,
        evidence=(
            ("asset_id", service.asset_id),
            ("host", service.host),
            ("port", str(service.port)),
            ("protocol", service.protocol),
            ("service", service.service),
            ("exposure", service.exposure),
        ),
    )