from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class KevEntry(BaseModel):
    # Preserve additional source fields as the feed evolves.
    model_config = ConfigDict(extra="allow", frozen=True)

    cveID: str = Field(
        strict=True,
        pattern=r"^CVE-[0-9]{4}-[0-9]{4,19}$",
    )
    vendorProject: str = Field(strict=True, min_length=1)
    product: str = Field(strict=True, min_length=1)
    vulnerabilityName: str = Field(strict=True, min_length=1)
    dateAdded: date
    shortDescription: str = Field(strict=True, min_length=1)
    requiredAction: str = Field(strict=True, min_length=1)
    dueDate: date


class KevCatalog(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)

    catalogVersion: str = Field(strict=True, min_length=1)
    dateReleased: datetime
    count: int = Field(strict=True, ge=0)
    vulnerabilities: tuple[KevEntry, ...]

    @field_validator("dateReleased")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Catalog release time must include a timezone.")
        return value

    @model_validator(mode="after")
    def validate_entries(self):
        if self.count != len(self.vulnerabilities):
            raise ValueError("Catalog count does not match its entries.")

        identifiers = [entry.cveID for entry in self.vulnerabilities]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Catalog contains duplicate CVE IDs.")

        return self