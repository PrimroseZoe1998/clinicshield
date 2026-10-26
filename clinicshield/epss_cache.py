from datetime import date, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from clinicshield.epss_download import EPSS_URL
from clinicshield.epss_models import EpssRecord


class EpssSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = 1
    source: Literal["FIRST EPSS"] = "FIRST EPSS"
    source_url: Literal[EPSS_URL] = EPSS_URL
    retrieved_at: datetime
    model_version: str = Field(strict=True, min_length=1)
    score_date: date
    records: tuple[EpssRecord, ...] = Field(min_length=1)

    @field_validator("retrieved_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Retrieval time must include a timezone.")
        return value

    @field_validator("model_version")
    @classmethod
    def require_model_version(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("EPSS model version must not be blank.")
        return value

    @model_validator(mode="after")
    def validate_records(self):
        seen = set()

        for record in self.records:
            if record.score_date != self.score_date:
                raise ValueError("EPSS record score dates must match.")
            if record.cve in seen:
                raise ValueError("Duplicate EPSS CVE identifier.")
            seen.add(record.cve)

        return self