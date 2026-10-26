from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

from clinicshield.feed_models import VulnerabilityRecord


class FeedSnapshot(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    schema_version: Literal[1] = 1
    source: str = Field(min_length=1, strict=True)
    source_url: HttpUrl
    retrieved_at: datetime
    records: tuple[VulnerabilityRecord, ...]

    @field_validator("retrieved_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Feed retrieval time must include a timezone.")
        return value

    @model_validator(mode="after")
    def validate_record_provenance(self):
        for record in self.records:
            if (
                record.source != self.source
                or record.source_url != self.source_url
                or record.retrieved_at != self.retrieved_at
            ):
                raise ValueError(
                    "Record provenance must match the feed snapshot."
                )
        return self


def serialize_snapshot(snapshot: FeedSnapshot) -> str:
    return snapshot.model_dump_json()


def deserialize_snapshot(payload: str) -> FeedSnapshot:
    return FeedSnapshot.model_validate_json(payload)