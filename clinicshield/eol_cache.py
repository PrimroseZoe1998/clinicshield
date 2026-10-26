from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from clinicshield.eol_download import EOL_BASE_URL
from clinicshield.eol_models import EolResponse


class EolSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = 1
    source: Literal["endoflife.date"] = "endoflife.date"
    source_url: str = Field(strict=True)
    retrieved_at: datetime
    product: str = Field(
        strict=True,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    response: EolResponse

    @field_validator("retrieved_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Retrieval time must include a timezone.")
        return value

    @model_validator(mode="after")
    def validate_product_provenance(self):
        if self.response.result.name != self.product:
            raise ValueError("Cached response must match the product.")

        expected_url = f"{EOL_BASE_URL}{self.product}/"
        if self.source_url != expected_url:
            raise ValueError("Source URL must match the product endpoint.")

        return self