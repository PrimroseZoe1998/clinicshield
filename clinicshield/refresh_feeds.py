import argparse
import sys
from pathlib import Path

import requests

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

    try:
        snapshot = refresh_kev_cache(args.cache_dir / "kev.json")
    except (requests.RequestException, ValueError, OSError) as error:
        print(
            f"CISA KEV refresh failed: {type(error).__name__}",
            file=sys.stderr,
        )
        return 1

    print(
        f"CISA KEV refreshed: "
        f"{snapshot.catalog.count} entries; "
        f"catalog {snapshot.catalog.catalogVersion}; "
        f"retrieved {snapshot.retrieved_at.isoformat()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())