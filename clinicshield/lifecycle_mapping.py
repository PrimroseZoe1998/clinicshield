from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)

from clinicshield.normalization import normalize_version


MappingText = Annotated[
    str,
    StringConstraints(strict=True, strip_whitespace=True, min_length=1),
]


class OsReleaseMapping(BaseModel):
    """Explicit mapping; no prefix matching or version guessing."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    os_name: MappingText
    os_version: MappingText
    product: str = Field(
        strict=True,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    release_name: MappingText
    mapping_basis: MappingText

    @field_validator("os_name", "os_version", "release_name")
    @classmethod
    def require_known_identity(cls, value: str) -> str:
        if normalize_version(value) is None:
            raise ValueError("Lifecycle mapping requires known identifiers.")
        return value