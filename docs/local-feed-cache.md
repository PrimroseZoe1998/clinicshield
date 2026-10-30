# Local public-feed cache

The app defaults to `<repository>/data/cache` when Load saved public-feed caches
is checked. The directory is ignored by Git and contains public intelligence only.
Assessment uploads and patient information must never be stored here.

Expected layout:

```text
data/cache/
  kev.json
  epss.json
  eol-python.json
  eol-windows.json
  nvd/
    CVE-2021-44228.json
  refresh-status.json
  refresh.log
```

The weekly/manual workflow now writes snapshots into data/cache on the runner
and publishes that directory as a 30-day artifact. It does not commit snapshots
or automatically synchronize a user's local checkout. Download and extract a
future artifact into this directory to update the local copy. Ensure kev.json
sits directly in data/cache rather than inside another public-feeds-* directory.
Keep original retrieval timestamps; copying a file does not refresh its source.
The app still permits an explicit alternative cache folder and never downloads
feeds while evaluating an assessment. Missing/invalid/stale coverage remains visible.

For an explicit online refresh from the repository root, with network access:

```powershell
python -m clinicshield.refresh_feeds --cache-dir data/cache --status-file data/cache/refresh-status.json --nvd-allowlist config/nvd-allowlist.json --eol-product python --eol-product windows
```

October 30 setup: copied the user's extracted public-feeds-40963762712 artifact
into data/cache, retaining bytes and timestamps. KEV, EPSS, lifecycle and NVD
loading are checked locally; no fresh network retrieval or scheduled execution
is implied. This closes the default local-path usability gap. Automatic persistent
repository distribution, if required by the original brief, remains a scope difference.

October 30 update: artifact public-feeds-41084601410.zip was validated locally
(all five snapshot readers and successful per-feed status), then installed into
data/cache with the previous cache backed up in workspace scratch storage.
Offline assessment/TXT generation passed, and the user confirmed the refreshed
October 30 dates in the app. See status/week-3.md for provenance and timestamps.
