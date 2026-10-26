from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    field_validator,
    model_validator,
)


class EolRelease(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)

    name: str = Field(strict=True, min_length=1)
    isEol: StrictBool | None
    eolFrom: date | None
    isMaintained: StrictBool | None


class EolProduct(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)

    name: str = Field(strict=True, min_length=1)
    label: str = Field(strict=True, min_length=1)
    releases: tuple[EolRelease, ...]

    @model_validator(mode="after")
    def reject_duplicate_releases(self):
        names = [release.name for release in self.releases]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate endoflife.date release names.")
        return self


class EolResponse(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)

    schema_version: str = Field(
        strict=True,
        pattern=r"^1\.[0-9]+\.[0-9]+$",
    )
    generated_at: datetime
    last_modified: datetime
    result: EolProduct

    @field_validator("generated_at", "last_modified")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Source timestamps must include a timezone.")
        return value