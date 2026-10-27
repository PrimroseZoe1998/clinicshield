from dataclasses import dataclass
from typing import Literal

from clinicshield.schemas import Asset, Service


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