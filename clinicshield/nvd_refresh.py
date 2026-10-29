import math
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests

from clinicshield.nvd_cache import MAX_NVD_BYTES, NVD_URL, NvdAllowlist, NvdSnapshot, cve_id, load_json, write_nvd_cache


class NvdBudgetExceeded(ValueError):
    pass


class NvdClient:
    """Sequential bounded public requests; never accepts an inventory or custom URL."""
    def __init__(self, *, budget_seconds=600, clock=time.monotonic, sleep=time.sleep, now=lambda: datetime.now(timezone.utc), get=None):
        if not math.isfinite(budget_seconds) or budget_seconds <= 0:
            raise ValueError("Provide a positive finite NVD run budget.")
        self.clock, self.sleep, self.now = clock, sleep, now
        self.get = get or requests.get
        self.deadline = clock() + budget_seconds
        self.next_request = clock()

    def wait(self, delay):
        if self.clock() + delay + 1 >= self.deadline:
            raise NvdBudgetExceeded("NVD run budget exhausted.")
        if delay > 0:
            self.sleep(delay)

    def retry_after(self, text):
        if not text:
            return 0
        try:
            value = float(text)
        except ValueError:
            try:
                value = (parsedate_to_datetime(text) - self.now()).total_seconds()
            except (ValueError, TypeError, OverflowError):
                raise ValueError("Invalid NVD Retry-After header.") from None
        if not math.isfinite(value):
            self.next_request = self.deadline
            raise ValueError("Invalid NVD Retry-After header.")
        return max(0, value)

    def download(self, identifier):
        cve_id(identifier)
        url = f"{NVD_URL}?cveId={identifier}"
        for attempt in range(3):
            self.wait(max(0, self.next_request - self.clock()))
            self.next_request = self.clock() + 10
            delay = 10 * (attempt + 1)
            try:
                remaining = self.deadline - self.clock()
                with self.get(url, timeout=(min(5, remaining), min(20, remaining)), stream=True, allow_redirects=False) as response:
                    if response.status_code == 429 or 500 <= response.status_code <= 599:
                        try:
                            delay = max(delay, self.retry_after(response.headers.get("Retry-After")))
                        except ValueError:
                            self.next_request = self.deadline
                            raise
                        response.raise_for_status()
                    response.raise_for_status()
                    if response.status_code != 200:
                        raise ValueError("Expected HTTP 200 from NVD.")
                    data = bytearray()
                    for chunk in response.iter_content(chunk_size=64 * 1024):
                        if self.clock() >= self.deadline:
                            raise NvdBudgetExceeded("NVD run budget exhausted.")
                        if not chunk:
                            continue
                        if len(data) + len(chunk) > MAX_NVD_BYTES:
                            raise ValueError("NVD download exceeds the size limit.")
                        data.extend(chunk)
                    return NvdSnapshot(cve_id=identifier, request_url=url, retrieved_at=self.now(), response=load_json(bytes(data)))
            except (requests.Timeout, requests.ConnectionError, requests.exceptions.ChunkedEncodingError):
                if attempt == 2:
                    raise
            except requests.HTTPError as error:
                code = error.response.status_code if error.response is not None else 0
                if code == 429 or 500 <= code <= 599:
                    self.next_request = max(self.next_request, self.clock() + delay)
                if attempt == 2 or (code != 429 and not 500 <= code <= 599):
                    raise
            self.wait(delay)
        raise ValueError("NVD retry attempts exhausted.")


def refresh_nvd_allowlist(allowlist: NvdAllowlist, directory: Path, *, client=None):
    client = client or NvdClient()
    outcomes = []
    exhausted = False
    for identifier in allowlist.cve_ids:
        if exhausted:
            outcomes.append({"source": f"NVD:{identifier}", "outcome": "failed", "error_type": "NvdBudgetExceeded"})
            continue
        try:
            snapshot = client.download(identifier)
            write_nvd_cache(directory / f"{identifier}.json", snapshot)
        except (requests.RequestException, ValueError, OSError) as error:
            outcomes.append({"source": f"NVD:{identifier}", "outcome": "failed", "error_type": type(error).__name__})
            exhausted = isinstance(error, NvdBudgetExceeded)
        else:
            outcomes.append({"source": f"NVD:{identifier}", "outcome": "succeeded", "retrieved_at": snapshot.retrieved_at.isoformat()})
    return outcomes
