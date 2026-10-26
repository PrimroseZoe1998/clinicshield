from datetime import datetime, timezone
from pathlib import Path

from clinicshield.eol_cache import EolSnapshot
from clinicshield.eol_cache_io import write_eol_cache
from clinicshield.eol_download import EOL_BASE_URL, download_eol


def refresh_eol_cache(path: Path, *, product: str) -> EolSnapshot:
    """Download, validate, and save one product's lifecycle data."""
    response = download_eol(product)

    snapshot = EolSnapshot(
        source_url=f"{EOL_BASE_URL}{product}/",
        retrieved_at=datetime.now(timezone.utc),
        product=product,
        response=response,
    )

    write_eol_cache(path, snapshot)
    return snapshot