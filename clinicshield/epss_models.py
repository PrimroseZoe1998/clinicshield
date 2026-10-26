from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EpssRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    cve: str = Field(
        strict=True,
        pattern=r"^CVE-[0-9]{4}-[0-9]{4,19}$",
    )
    epss: Decimal = Field(ge=0, le=1, allow_inf_nan=False)
    percentile: Decimal = Field(ge=0, le=1, allow_inf_nan=False)
    score_date: date

    @field_validator("epss", "percentile", mode="before")
    @classmethod
    def reject_boolean_scores(cls, value):
        if isinstance(value, bool):
            raise ValueError("EPSS values must be numeric, not boolean.")
        return value