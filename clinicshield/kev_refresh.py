from datetime import datetime, timezone
from pathlib import Path

from clinicshield.kev_cache import KevSnapshot, write_kev_cache
from clinicshield.kev_download import download_kev


def refresh_kev_cache(path: Path) -> KevSnapshot:
    """Download, validate, and save KEV; propagate refresh failures."""
    catalog = download_kev()

    snapshot = KevSnapshot(
        retrieved_at=datetime.now(timezone.utc),
        catalog=catalog,
    )

    write_kev_cache(path, snapshot)
    return snapshot