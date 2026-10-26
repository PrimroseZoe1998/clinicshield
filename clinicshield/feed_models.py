from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from clinicshield.normalization import normalize_name, normalize_version


class VulnerabilityRecord(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    vulnerability_id: str = Field(min_length=1, strict=True)
    source: str = Field(min_length=1, strict=True)
    source_url: HttpUrl
    retrieved_at: datetime
    vendor: str = Field(min_length=1, strict=True)
    product: str = Field(min_length=1, strict=True)
    version_rule: Literal["exact", "unsupported"]
    affected_versions: tuple[str, ...] = ()
    version_evidence: str = Field(default="", strict=True)

    @field_validator("vendor", "product")
    @classmethod
    def validate_identity(cls, value: str) -> str:
        normalized = normalize_name(value)
        if normalize_version(normalized) is None:
            raise ValueError("Provide a known vendor and product.")
        return normalized

    @field_validator("affected_versions")
    @classmethod
    def validate_versions(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        cleaned = []
        for value in values:
            version = normalize_version(value)
            if version is None:
                raise ValueError(
                    "Affected versions must contain known version values."
                )
            cleaned.append(version)
        return tuple(cleaned)

    @field_validator("retrieved_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Feed retrieval time must include a timezone.")
        return value