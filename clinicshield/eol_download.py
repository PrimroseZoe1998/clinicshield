import re

import requests

from clinicshield.eol_models import EolResponse


EOL_BASE_URL = "https://endoflife.date/api/v1/products/"
MAX_DOWNLOAD_BYTES = 10 * 1024 * 1024


def download_eol(product: str) -> EolResponse:
    """Download one product using its exact endoflife.date slug."""
    if not isinstance(product, str) or not re.fullmatch(
        r"[a-z0-9]+(?:-[a-z0-9]+)*", product
    ):
        raise ValueError("Provide a valid endoflife.date product slug.")

    url = f"{EOL_BASE_URL}{product}/"

    with requests.get(
        url,
        timeout=(10, 30),
        stream=True,
        allow_redirects=False,
    ) as response:
        response.raise_for_status()

        if response.status_code != 200:
            raise ValueError("Expected HTTP 200 from endoflife.date.")

        payload = bytearray()

        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue

            if len(payload) + len(chunk) > MAX_DOWNLOAD_BYTES:
                raise ValueError(
                    "endoflife.date download exceeds the size limit."
                )

            payload.extend(chunk)

    result = EolResponse.model_validate_json(bytes(payload))

    if result.result.name != product:
        raise ValueError("endoflife.date returned a different product.")

    return result