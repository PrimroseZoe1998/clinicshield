from datetime import datetime, timezone
from pathlib import Path

from clinicshield.epss_cache import EpssSnapshot
from clinicshield.epss_cache_io import write_epss_cache
from clinicshield.epss_download import download_epss


def refresh_epss_cache(path: Path) -> EpssSnapshot:
    """Download, validate, and save EPSS; propagate refresh failures."""
    dataset = download_epss()

    snapshot = EpssSnapshot(
        retrieved_at=datetime.now(timezone.utc),
        model_version=dataset.model_version,
        score_date=dataset.score_date,
        records=dataset.records,
    )

    write_epss_cache(path, snapshot)
    return snapshot