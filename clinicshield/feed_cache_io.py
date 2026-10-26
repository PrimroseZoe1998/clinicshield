import os
import tempfile
from pathlib import Path

from clinicshield.feed_cache import (
    FeedSnapshot,
    deserialize_snapshot,
    serialize_snapshot,
)


MAX_CACHE_BYTES = 10 * 1024 * 1024


def read_feed_cache(path: Path) -> FeedSnapshot | None:
    """Return None for a missing cache; raise for invalid cache data."""
    try:
        with path.open("rb") as handle:
            payload = handle.read(MAX_CACHE_BYTES + 1)
    except FileNotFoundError:
        return None

    if len(payload) > MAX_CACHE_BYTES:
        raise ValueError("Feed cache exceeds the size limit.")

    return deserialize_snapshot(payload.decode("utf-8"))


def write_feed_cache(path: Path, snapshot: FeedSnapshot) -> None:
    """Replace a cache atomically using a temporary file beside it."""
    payload = serialize_snapshot(snapshot).encode("utf-8")

    if len(payload) > MAX_CACHE_BYTES:
        raise ValueError("Feed cache exceeds the size limit.")

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