import csv
import io
from dataclasses import dataclass
from datetime import date, datetime, timezone

from clinicshield.epss_models import EpssRecord


MAX_CSV_CHARACTERS = 64 * 1024 * 1024
MAX_RECORDS = 1_000_000


@dataclass(frozen=True)
class EpssDataset:
    model_version: str
    score_date: date
    records: tuple[EpssRecord, ...]


def parse_epss_csv(text: str) -> EpssDataset:
    if len(text) > MAX_CSV_CHARACTERS:
        raise ValueError("EPSS CSV exceeds the size limit.")

    stream = io.StringIO(text, newline="")
    comment = stream.readline().strip()

    if not comment.startswith("#"):
        raise ValueError("EPSS metadata comment is missing.")

    metadata = {}
    for item in comment[1:].split(","):
        key, separator, value = item.partition(":")
        key, value = key.strip(), value.strip()
        if not separator or not key or not value or key in metadata:
            raise ValueError("Invalid EPSS metadata.")
        metadata[key] = value

    model_version = metadata.get("model_version", "")
    if not model_version or "score_date" not in metadata:
        raise ValueError("EPSS model version or score date is missing.")

    raw_date = metadata["score_date"]

    if "T" in raw_date:
        published_at = datetime.fromisoformat(raw_date)
        if (
            published_at.tzinfo is None
            or published_at.utcoffset() is None
        ):
            raise ValueError("EPSS score timestamp requires a timezone.")
        score_date = published_at.astimezone(timezone.utc).date()
    else:
        score_date = date.fromisoformat(raw_date)
        if score_date.isoformat() != raw_date:
            raise ValueError("EPSS score date must use YYYY-MM-DD.")

    reader = csv.reader(stream, strict=True)
    if next(reader, None) != ["cve", "epss", "percentile"]:
        raise ValueError("Unexpected EPSS CSV columns.")

    records = []
    seen = set()

    try:
        for row in reader:
            if len(row) != 3:
                raise ValueError("EPSS rows must contain three fields.")
            if len(records) >= MAX_RECORDS:
                raise ValueError("EPSS record limit exceeded.")

            record = EpssRecord(
                cve=row[0],
                epss=row[1],
                percentile=row[2],
                score_date=score_date,
            )
            if record.cve in seen:
                raise ValueError("Duplicate EPSS CVE identifier.")

            seen.add(record.cve)
            records.append(record)
    except csv.Error as error:
        raise ValueError("Malformed EPSS CSV.") from error

    if not records:
        raise ValueError("EPSS CSV contains no score records.")

    return EpssDataset(
        model_version=model_version,
        score_date=score_date,
        records=tuple(records),
    )