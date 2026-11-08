# PDF assessment report

The results screen now offers Download assessment (PDF), alongside CSV, JSON and
TXT. It uses the existing pinned fpdf2 dependency and licensed bundled Bitstream
Vera fonts; no new runtime package or external font download is required.

The first page is a bounded owner summary: score and components, status, coverage
and review counts, up to three limitations, the top three globally ranked Fix First
actions, owners/effort/cost and a next step. Long summary labels are shortened;
full text remains in the appendix. Missing evidence and synthetic remediation
warnings remain visible. The report does not predict score improvement, actual
risk reduction, compliance or clinical security effectiveness.

Page two begins a complete appendix rendered from the same readable report as
TXT, preserving score arithmetic, draft practice views, coverage issues, conflicts,
all Fix First actions/provider requests, findings, evidence and framework-reference
status/rationale/sources. Footers include developer credit and page numbers.
Unsupported font characters are shown explicitly as [U+code], rather than silently
removed. The appendix can be long because review findings and repeated source
references are retained: the initial samples are 37, 34 and 72 total pages.

All rendering returns bytes in memory. User assessment data is not written to disk
or sent over the network. Only deliberate fictional sample generation writes
samples/reports/*.pdf. Font files are read from the packaged repository directory.

Validation covers PDF structure, exactly one summary page before the appendix,
full readable-text inclusion, unchanged report inputs, all three fictional clinics,
long/unicode evidence, empty actions and UI download wiring. All three sample PDFs
were rendered with Poppler and every page reviewed in contact sheets; summary and
representative appendix pages were also inspected individually. On November 8,
the user confirmed the PDF download with page-one owner summary and page-two
appendix in the app verification sequence. This covers the exercised sample path.
Fresh GitHub CI remains pending for this increment.

Local suite: 2,532 passed excluding the known stalled AppTest file. Changed-file
medium/high Bandit and git diff --check passed. No fresh CI claimed.


November 8 plain-language update: owner guidance and recommended actions use
shorter sentences. The appendix includes a word guide before technical details.
Scoring/evidence/source content remains intact. See readability-review.md for
screening method and limitations; it is not a universal grade-8 certification.
