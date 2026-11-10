"""Public build/runtime metadata only; never expose environment secrets or input data."""
from importlib import metadata
from pathlib import Path
import platform
import re
import subprocess

PACKAGES = ("streamlit", "pyarrow", "certifi", "pip")


def checkout_revision(root):
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"], cwd=Path(root),
            capture_output=True, text=True, timeout=2, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"
    value = result.stdout.strip()
    return value if result.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value) else "unavailable"


def runtime_details(root, *, usage_stats):
    pins = {}
    try:
        for line in (Path(root) / "requirements.txt").read_text(encoding="utf-8").splitlines():
            if "==" in line and not line.lstrip().startswith("#"):
                name, version = line.strip().split("==", 1)
                pins[name.lower()] = version
    except OSError:
        pass
    packages = {}
    for name in PACKAGES:
        try:
            actual = metadata.version(name)
        except metadata.PackageNotFoundError:
            actual = "unavailable"
        pin = pins.get(name)
        packages[name] = {"installed": actual, "repository_pin": pin,
                          "matches_pin": actual == pin if pin is not None else None}
    return {"checkout_commit": checkout_revision(root),
            "python": platform.python_version(),
            "effective_usage_statistics_setting": usage_stats,
            "packages": packages}
