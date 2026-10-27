from dataclasses import dataclass
from typing import Literal

from clinicshield.schemas import Asset, Service
from clinicshield.checklist_input import ANSWERS, Checklist
from clinicshield.input_limits import InputError

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