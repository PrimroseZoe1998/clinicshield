# Inventory upload assessments

Choose **Upload inventory** under **Assessment source**. Supply either separate
assets/software CSV or JSON files, or an XLSX inventory workbook using the existing
template sheets. Separate services inventory is optional. Checklist and follow-up
JSON answers are required for every format. Select whether medical devices are
present (default Unknown), then choose **Generate assessment**.

The existing inventory parsers enforce required columns, input sizes, privacy
headers and asset links. Inventory uploads have the existing 10 MiB file limit;
checklist, follow-up and reviewed-evidence JSON files retain their 64 KiB limits.
Combined inventory, answers and optional evidence are limited to 20 MiB.
Workbook archive and row limits remain enforced by the workbook parser.

Saved public feeds, reviewed lifecycle mappings and reviewed CVE evidence can be
used with uploaded inventories. Evidence must refer to those inventory entries;
evidence upload widgets use separate identities for example and upload modes.
Synthetic scenario evidence is available only in the fictional example mode.

Evaluation runs in memory without writing uploaded inventories to disk or making
network requests. Inputs remain in the current Streamlit session while in use.
Changing inputs, mode or policy clears the displayed result until regeneration.
Failed generation clears the previous report and shows an error without uploaded
values or internal diagnostics.

Downloads identify **uploaded inventory** and explain that supplied information
has not been independently verified. Scores remain provisional, and missing
coverage and unresolved evidence remain visible. Uploading fictional files through
this mode still tests fictional data; the mode does not establish their authenticity.

This UI supports CSV, JSON and XLSX inventory inputs. Existing backend Nmap parsing
is not exposed in this upload interface. Administrator-observation evidence and
full framework validation remain separate work.

Validation includes format-to-report integration, missing/invalid input rejection,
mode-specific rendering using a mocked Streamlit boundary, changed-input report
invalidation, evidence asset links, missing services and offline/no-write checks.
Native Streamlit AppTest remains affected by the previously documented socket-pair
stall in this environment. Manual browser checks are recorded below.

October 29, 2026: 2,350 tests passed with `tests/test_app_preview.py` excluded,
including 20 new upload integration/UI-boundary tests. `git diff --check` passed.
The fictional Lakeview CSV upload baseline is 80 overall, 72.3 Safeguards and
91.0 Exposure without scenario evidence or public caches. The original synthetic
scenario still scores 65. These are test results, not real clinic assessments.

## Manual browser checks completed October 29, 2026

- Fictional Lakeview CSV and equivalent JSON uploads display 80 overall,
  72.3 Safeguards and 91.0 Exposure.
- The existing fictional Excel template, with Lakeview checklist/follow-up answers,
  displays 83 overall, 72.3 Safeguards and 100.0 Exposure. This template contains
  different inventory from Lakeview. Missing coverage remains relevant to the score.
- The readable CSV assessment includes the uploaded-inventory notice, the statement
  that inputs have not been independently verified, provisional status and coverage
  warnings. The notice appeared after restarting the running Streamlit process.
- Removing the services upload clears the previous scores and download. Regenerating
  without services displays the unassessed-network-services warning.
- Removing the required assets upload and regenerating displays an input error
  without scores or a download.

These checks used fictional test files only. They do not establish validation of
real clinic records or complete every possible browser path. JSON/Excel download
notices are covered by automated integration checks; their manual download check
was not separately reported. Test files remain outside the repository.
