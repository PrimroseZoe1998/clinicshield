import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from clinicshield.kev_download import KEV_URL
from clinicshield.kev_models import KevCatalog


MAX_CACHE_BYTES = 20 * 1024 * 1024


class KevSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = 1
    source: Literal["CISA KEV"] = "CISA KEV"
    source_url: Literal[KEV_URL] = KEV_URL
    retrieved_at: datetime
    catalog: KevCatalog

    @field_validator("retrieved_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Retrieval time must include a timezone.")
        return value


def read_kev_cache(path: Path) -> KevSnapshot | None:
    try:
        with path.open("rb") as handle:
            payload = handle.read(MAX_CACHE_BYTES + 1)
    except FileNotFoundError:
        return None

    if len(payload) > MAX_CACHE_BYTES:
        raise ValueError("KEV cache exceeds the size limit.")

    return KevSnapshot.model_validate_json(payload)


def write_kev_cache(path: Path, snapshot: KevSnapshot) -> None:
    payload = snapshot.model_dump_json().encode("utf-8")

    if len(payload) > MAX_CACHE_BYTES:
        raise ValueError("KEV cache exceeds the size limit.")

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)