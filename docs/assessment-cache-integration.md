# Saved public feeds in example assessments

The Streamlit preview now offers **Load saved public-feed caches**.
Select the folder containing `kev.json` and `epss.json` produced by
`python -m clinicshield.refresh_feeds --cache-dir feed-output` or extracted
from the refresh workflow artifact. The default folder is `feed-output`
under the repository. Loading snapshots does not download feeds.

Both snapshots use the existing validated, size-limited readers. Each is
loaded independently so one invalid file does not discard the other feed.
Missing and invalid caches remain unavailable. Retrieval freshness and
source-date review messages appear in the preview and readable download.
Existing rule handlers retain their freshness checks before using evidence.

The preview still uses fictional inventories and optional synthetic scenario
evidence. Loading a KEV catalog does not create software-to-CVE associations.
Software without supplied applicability records remains unassessed.
Lifecycle cache mappings and reviewed applicability JSON inputs are now connected;
see `reviewed-assessment-evidence.md`. Real inventory uploads remain integration work.

Validation on October 29, 2026: six new cache tests and 52 existing assessment
and report tests passed (58 total). The full suite and Streamlit AppTest
stalled in this sandbox and were interrupted; they are not reported as passing.
