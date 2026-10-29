import re
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

from clinicshield.epss_refresh import refresh_epss_cache
from clinicshield.kev_refresh import refresh_kev_cache
from clinicshield.eol_refresh import refresh_eol_cache
from clinicshield.refresh_status import write_refresh_status

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh public feed caches.")
    parser.add_argument(
        "--cache-dir",
        type=Path,
        required=True,
        help="Directory for public feed cache files.",
    )
    parser.add_argument(
        "--eol-product",
        action="append",
        default=[],
        help="Exact endoflife.date product slug; may be repeated.",
    )
    parser.add_argument(
        "--status-file", type=Path,
        help="Optional per-run JSON status report; contains no inventory data.",
    )
    args = parser.parse_args(argv)
    failed = False
    status = {
        "schema_version": 1,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "feeds": [],
    }

    def record(source, outcome, *, snapshot=None, error=None):
        entry = {"source": source, "outcome": outcome}
        if snapshot is not None:
            entry["retrieved_at"] = snapshot.retrieved_at.isoformat()
        if error is not None:
            entry["error_type"] = type(error).__name__
        status["feeds"].append(entry)

    try:
        snapshot = refresh_kev_cache(args.cache_dir / "kev.json")
    except (requests.RequestException, ValueError, OSError) as error:
        print(
            f"CISA KEV refresh failed: {type(error).__name__}",
            file=sys.stderr,
        )
        record("CISA KEV", "failed", error=error)
        failed = True
    else:
        record("CISA KEV", "succeeded", snapshot=snapshot)
        print(
            f"CISA KEV refreshed: "
            f"{snapshot.catalog.count} entries; "
            f"catalog {snapshot.catalog.catalogVersion}; "
            f"retrieved {snapshot.retrieved_at.isoformat()}"
        )

    try:
        epss_snapshot = refresh_epss_cache(args.cache_dir / "epss.json")
    except (requests.RequestException, ValueError, OSError) as error:
        print(
            f"FIRST EPSS refresh failed: {type(error).__name__}",
            file=sys.stderr,
        )
        record("FIRST EPSS", "failed", error=error)
        failed = True
    else:
        record("FIRST EPSS", "succeeded", snapshot=epss_snapshot)
        print(
            f"FIRST EPSS refreshed: "
            f"{len(epss_snapshot.records)} records; "
            f"model {epss_snapshot.model_version}; "
            f"score date {epss_snapshot.score_date}; "
            f"retrieved {epss_snapshot.retrieved_at.isoformat()}"
        )
    for product in dict.fromkeys(args.eol_product):
        try:
            # Validate the slug before using it in a cache filename.
            if not isinstance(product, str) or not re.fullmatch(
                r"[a-z0-9]+(?:-[a-z0-9]+)*", product
            ):
                raise ValueError("Invalid endoflife.date product slug.")

            eol_snapshot = refresh_eol_cache(
                args.cache_dir / f"eol-{product}.json",
                product=product,
            )
        except (requests.RequestException, ValueError, OSError) as error:
            print(
                f"endoflife.date refresh failed for {product!r}: "
                f"{type(error).__name__}",
                file=sys.stderr,
            )
            record(
                f"endoflife.date:{product}" if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", product)
                else "endoflife.date:invalid-product", "failed", error=error,
            )
            failed = True
        else:
            record(f"endoflife.date:{product}", "succeeded", snapshot=eol_snapshot)
            print(
                f"endoflife.date refreshed: {eol_snapshot.product}; "
                f"{len(eol_snapshot.response.result.releases)} releases; "
                f"retrieved {eol_snapshot.retrieved_at.isoformat()}"
            )
    status["finished_at"] = datetime.now(timezone.utc).isoformat()
    status["outcome"] = "failed" if failed else "succeeded"
    if args.status_file is not None:
        try:
            write_refresh_status(args.status_file, status)
        except OSError as error:
            print(f"Refresh status report failed: {type(error).__name__}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())