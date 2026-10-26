import requests

from clinicshield.kev_models import KevCatalog


KEV_URL = (
    "https://www.cisa.gov/sites/default/files/feeds/"
    "known_exploited_vulnerabilities.json"
)
MAX_DOWNLOAD_BYTES = 10 * 1024 * 1024


def download_kev() -> KevCatalog:
    """Download and validate KEV without writing files."""
    with requests.get(
        KEV_URL,
        timeout=(10, 30),
        stream=True,
        allow_redirects=False,
    ) as response:
        response.raise_for_status()

        if response.status_code != 200:
            raise ValueError("Expected HTTP 200 from the KEV feed.")

        payload = bytearray()

        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue

            if len(payload) + len(chunk) > MAX_DOWNLOAD_BYTES:
                raise ValueError("KEV download exceeds the size limit.")

            payload.extend(chunk)

    return KevCatalog.model_validate_json(bytes(payload))