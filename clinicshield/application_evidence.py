from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    HttpUrl,
    StringConstraints,
    field_validator,
)


EvidenceText = Annotated[
    str,
    StringConstraints(strict=True, strip_whitespace=True, min_length=1),
]


class ApplicationSupportEvidence(BaseModel):
    """Support evidence tied to one identified software entry."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    software_entry_id: EvidenceText
    vendor: EvidenceText
    product: EvidenceText
    version: EvidenceText
    deployment: Literal["local", "cloud"]
    support_status: Literal["supported", "unsupported", "unknown"]
    support_basis: EvidenceText
    extended_support: Literal[
        "not_applicable",
        "confirmed_absent",
        "active",
        "unknown",
    ]
    source_url: HttpUrl | None
    retrieved_at: datetime | None
    source_generated_at: datetime | None

    @field_validator("retrieved_at", "source_generated_at")
    @classmethod
    def require_timezone(
        cls, value: datetime | None
    ) -> datetime | None:
        if value is not None:
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(
                    "Application support timestamps must include a timezone."
                )
        return value