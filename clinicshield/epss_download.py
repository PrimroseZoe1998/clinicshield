import gzip
import io

import requests

from clinicshield.epss_parse import EpssDataset, parse_epss_csv


EPSS_URL = (
    "https://epss.empiricalsecurity.com/"
    "epss_scores-current.csv.gz"
)
MAX_DOWNLOAD_BYTES = 20 * 1024 * 1024
MAX_DECOMPRESSED_BYTES = 64 * 1024 * 1024


def download_epss() -> EpssDataset:
    """Download, decompress, and validate the EPSS bulk feed."""
    with requests.get(
        EPSS_URL,
        timeout=(10, 60),
        stream=True,
        allow_redirects=True,
    ) as response:
        response.raise_for_status()

        if response.status_code != 200:
            raise ValueError("Expected HTTP 200 from the EPSS feed.")

        compressed = bytearray()

        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue

            if len(compressed) + len(chunk) > MAX_DOWNLOAD_BYTES:
                raise ValueError("EPSS download exceeds the size limit.")

            compressed.extend(chunk)

    try:
        with gzip.GzipFile(
            fileobj=io.BytesIO(compressed),
            mode="rb",
        ) as handle:
            payload = handle.read(MAX_DECOMPRESSED_BYTES + 1)
    except (OSError, EOFError) as error:
        raise ValueError("Invalid EPSS gzip data.") from error

    if len(payload) > MAX_DECOMPRESSED_BYTES:
        raise ValueError("Decompressed EPSS data exceeds the size limit.")

    return parse_epss_csv(payload.decode("utf-8"))