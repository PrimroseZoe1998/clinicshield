from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    StringConstraints,
    field_validator,
)


EvidenceText = Annotated[
    str,
    StringConstraints(strict=True, strip_whitespace=True, min_length=1),
]


class MedicalSeparationEvidence(BaseModel):
    """Explicit separation evidence for one medical-device asset."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    asset_id: EvidenceText
    separation_verified: Literal["Yes", "No", "Unknown"]
    evidence_basis: EvidenceText
    evidence_source: EvidenceText
    observed_at: datetime | None

    @field_validator("observed_at")
    @classmethod
    def require_timezone(
        cls, value: datetime | None
    ) -> datetime | None:
        if value is not None:
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(
                    "Separation observation time must include a timezone."
                )
        return value