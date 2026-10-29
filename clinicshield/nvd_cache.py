import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from clinicshield.input_limits import MAX_JSON_BYTES, validate_upload
from clinicshield.json_input import unique_object, reject_constant

NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
MAX_NVD_BYTES = 4 * 1024 * 1024
CVE_PATTERN = r"CVE-[0-9]{4}-[0-9]{4,19}"


def cve_id(value):
    if not isinstance(value, str) or not re.fullmatch(CVE_PATTERN, value):
        raise ValueError("Provide a valid CVE ID.")
    return value


def source_time(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})?", value,
    ):
        raise ValueError("NVD source timestamp must be text.")
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    # The NVD API emits UTC timestamps without an offset, as verified in its response.
    return stamp.replace(tzinfo=timezone.utc) if stamp.tzinfo is None else stamp


def load_json(data):
    try:
        return json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique_object, parse_constant=reject_constant)
    except (UnicodeDecodeError, ValueError, RecursionError):
        raise ValueError("Invalid JSON input.") from None


class NvdAllowlist(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal[1] = 1
    review_status: Literal["reviewed"]
    review_basis: str = Field(strict=True, min_length=1)
    cve_ids: tuple[str, ...] = Field(max_length=50)

    @model_validator(mode="after")
    def validate_entries(self):
        if not self.review_basis.strip():
            raise ValueError("Provide an allowlist review basis.")
        for value in self.cve_ids:
            cve_id(value)
        if len(set(self.cve_ids)) != len(self.cve_ids):
            raise ValueError("Allowlist CVE IDs must be unique.")
        return self


def read_nvd_allowlist(path: Path) -> NvdAllowlist:
    with path.open("rb") as handle:
        data = handle.read(MAX_JSON_BYTES + 1)
    validate_upload(data, max_bytes=MAX_JSON_BYTES)
    return NvdAllowlist.model_validate(load_json(data))


class NvdSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal[1] = 1
    source: Literal["NVD CVE API 2.0"] = "NVD CVE API 2.0"
    cve_id: str
    request_url: str
    retrieved_at: datetime
    response: dict

    @field_validator("retrieved_at")
    @classmethod
    def aware_retrieval(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Retrieval time must include a timezone.")
        return value

    @model_validator(mode="after")
    def validate_record(self):
        identifier = cve_id(self.cve_id)
        if self.request_url != f"{NVD_URL}?cveId={identifier}":
            raise ValueError("NVD cache request URL does not match the CVE.")
        response = self.response
        if (response.get("format") != "NVD_CVE" or response.get("version") != "2.0"
                or any(type(response.get(key)) is not int for key in ("totalResults", "startIndex", "resultsPerPage"))
                or response["totalResults"] != 1 or response["startIndex"] != 0 or response["resultsPerPage"] != 1):
            raise ValueError("Expected a single-record NVD API 2.0 response.")
        rows = response.get("vulnerabilities")
        if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
            raise ValueError("Expected one NVD CVE record.")
        record = rows[0].get("cve")
        if not isinstance(record, dict) or record.get("id") != identifier:
            raise ValueError("NVD returned a missing or mismatched CVE.")
        source_time(response.get("timestamp"))
        for key in ("published", "lastModified"):
            source_time(record.get(key))
        if not isinstance(record.get("descriptions"), list) or not record["descriptions"] or not isinstance(record.get("references"), list):
            raise ValueError("NVD record lacks required source fields.")
        json.dumps(response, allow_nan=False)
        return self

    @property
    def record(self):
        return self.response["vulnerabilities"][0]["cve"]


def read_nvd_cache(path: Path, identifier: str) -> NvdSnapshot | None:
    cve_id(identifier)
    try:
        with path.open("rb") as handle:
            payload = handle.read(MAX_NVD_BYTES + 1)
    except FileNotFoundError:
        return None
    if len(payload) > MAX_NVD_BYTES:
        raise ValueError("NVD cache exceeds the size limit.")
    snapshot = NvdSnapshot.model_validate(load_json(payload))
    if snapshot.cve_id != identifier:
        raise ValueError("NVD cache identity mismatch.")
    return snapshot


def write_nvd_cache(path: Path, snapshot: NvdSnapshot) -> None:
    snapshot = NvdSnapshot.model_validate(snapshot.model_dump())
    payload = snapshot.model_dump_json().encode("utf-8")
    if len(payload) > MAX_NVD_BYTES:
        raise ValueError("NVD cache exceeds the size limit.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, prefix=".nvd-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
