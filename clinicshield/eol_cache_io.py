import os
import tempfile
from pathlib import Path

from clinicshield.eol_cache import EolSnapshot


MAX_CACHE_BYTES = 20 * 1024 * 1024


def read_eol_cache(path: Path) -> EolSnapshot | None:
    """Return None for a missing cache; raise for invalid data."""
    try:
        with path.open("rb") as handle:
            payload = handle.read(MAX_CACHE_BYTES + 1)
    except FileNotFoundError:
        return None

    if len(payload) > MAX_CACHE_BYTES:
        raise ValueError("endoflife.date cache exceeds the size limit.")

    return EolSnapshot.model_validate_json(payload)


def write_eol_cache(path: Path, snapshot: EolSnapshot) -> None:
    """Replace the cache only after the new file is fully written."""
    payload = snapshot.model_dump_json().encode("utf-8")

    if len(payload) > MAX_CACHE_BYTES:
        raise ValueError("endoflife.date cache exceeds the size limit.")

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