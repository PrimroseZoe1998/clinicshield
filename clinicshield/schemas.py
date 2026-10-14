from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

YesNoUnknown = Literal["Y", "N", "Unknown"]

AssetType = Literal[
    "workstation", "laptop", "server", "tablet", "phone",
    "printer", "network_device", "medical_device", "iot", "other",
]


class Asset(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
    )

    asset_id: str = Field(min_length=1)
    asset_name: str = Field(min_length=1)
    asset_type: AssetType
    location: str = ""
    owner_role: str = ""
    os_name: str = Field(min_length=1)
    os_version: str = Field(min_length=1)
    touches_phi: YesNoUnknown
    internet_facing: YesNoUnknown
    portable: Literal["Y", "N"] | None = None
    encrypted: YesNoUnknown
    auto_update: YesNoUnknown = "Unknown"
    last_patched: date | None = None
    network_segment: str = "unknown"
    notes: str = ""

    @field_validator("last_patched", mode="before")
    @classmethod
    def validate_patch_date(cls, value):
        if value is None or value == "":
            return None
        if isinstance(value, date):
            return value
        if not isinstance(value, str):
            raise ValueError("Use a date in YYYY-MM-DD format.")
        value = value.strip()
        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            raise ValueError("Use a valid date in YYYY-MM-DD format.") from None
        if parsed.isoformat() != value:
            raise ValueError("Use a date in YYYY-MM-DD format.")
        return parsed

    @field_validator("portable", mode="before")
    @classmethod
    def blank_portable_is_unspecified(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("auto_update", mode="before")
    @classmethod
    def blank_update_is_unknown(cls, value):
        if isinstance(value, str) and not value.strip():
            return "Unknown"
        return value

    @field_validator("network_segment", mode="before")
    @classmethod
    def blank_segment_is_unknown(cls, value):
        if isinstance(value, str) and not value.strip():
            return "unknown"
        return value

    @model_validator(mode="after")
    def infer_portability(self):
        if self.portable is None:
            self.portable = (
                "Y" if self.asset_type in {"laptop", "tablet", "phone"} else "N"
            )
        return self

class Software(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
    )

    asset_id: str = ""
    vendor: str = Field(min_length=1)
    product: str = Field(min_length=1)
    version: str = Field(min_length=1)
    purpose: Literal[
        "ehr", "practice_management", "billing", "email", "telehealth",
        "remote_access", "browser", "antivirus", "backup", "office",
        "imaging", "messaging", "other",
    ]
    deployment: Literal["local", "cloud"]
    touches_phi: YesNoUnknown
    mfa_enabled: Literal["Y", "N", "NA", "Unknown"]
    auto_update: YesNoUnknown = "Unknown"
    baa_signed: Literal["Y", "N", "NA", "Unknown"] = "Unknown"
    notes: str = ""

    @field_validator("auto_update", "baa_signed", mode="before")
    @classmethod
    def blank_optional_answer_is_unknown(cls, value):
        if isinstance(value, str) and not value.strip():
            return "Unknown"
        return value

    @model_validator(mode="after")
    def validate_cloud_asset_marker(self):
        if self.asset_id == "CLOUD" and self.deployment != "cloud":
            raise ValueError("Use CLOUD only for cloud software.")
        return self

class Service(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
    )

    asset_id: str = Field(min_length=1)
    host: str = ""
    port: int = Field(ge=1, le=65535)
    protocol: Literal["tcp", "udp"]
    service: Literal[
        "rdp", "smb", "ssh", "http", "https",
        "ftp", "telnet", "vnc", "dicom", "other",
    ]
    product: str = ""
    version: str = "Unknown"
    exposure: Literal["internal", "internet", "unknown"]

    @field_validator("port", mode="before")
    @classmethod
    def validate_port_number(cls, value):
        if type(value) is int:
            return value
        if isinstance(value, str):
            value = value.strip()
            if value.isascii() and value.isdigit():
                return int(value)
        raise ValueError("Use a whole-number port from 1 to 65535.")

    @field_validator("version", mode="before")
    @classmethod
    def blank_version_is_unknown(cls, value):
        if isinstance(value, str) and not value.strip():
            return "Unknown"
        return value