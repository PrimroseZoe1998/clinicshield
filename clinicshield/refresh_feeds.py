import argparse
import sys
from pathlib import Path

import requests

from clinicshield.epss_refresh import refresh_epss_cache
from clinicshield.kev_refresh import refresh_kev_cache


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh public feed caches.")
    parser.add_argument(
        "--cache-dir",
        type=Path,
        required=True,
        help="Directory for public feed cache files.",
    )
    args = parser.parse_args(argv)
    failed = False

    try:
        snapshot = refresh_kev_cache(args.cache_dir / "kev.json")
    except (requests.RequestException, ValueError, OSError) as error:
        print(
            f"CISA KEV refresh failed: {type(error).__name__}",
            file=sys.stderr,
        )
        failed = True
    else:
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
        failed = True
    else:
        print(
            f"FIRST EPSS refreshed: "
            f"{len(epss_snapshot.records)} records; "
            f"model {epss_snapshot.model_version}; "
            f"score date {epss_snapshot.score_date}; "
            f"retrieved {epss_snapshot.retrieved_at.isoformat()}"
        )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())