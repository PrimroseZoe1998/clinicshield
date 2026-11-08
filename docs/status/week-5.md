# Week 5 status

## Done

November 8: findings CSV and reusable checklist JSON downloads implemented locally.
Saved JSON retains 25 answers, Q24 follow-ups and medical-device applicability;
legacy import remains supported. CSV retains evidence and uncertainty and guards
formula-like scalar cells. Corrected Week 5 plan against the original brief.
Fixed an existing NVD integration test to use its declared fixture clock.

Validation: 2,526 tests passed with tests/test_app_preview.py excluded (known local
stall), using an explicit workspace temporary directory. Changed-file Bandit
medium/high check passed. git diff --check passed. User screenshots confirm CSV
opened in Excel, JSON downloaded with answers/follow-ups/applicability, and saved
JSON re-upload succeeded after restarting Streamlit: Lakeview inventory-only
80 overall, 72.3 Safeguards, 91.0 Exposure, with provisional/coverage warnings.
These observations cover the exercised Lakeview path, not every input path.
New CI results remain unverified.

## Next

Save/push this verified checkpoint, then implement the PDF owner summary and
detailed appendix. Continue
five-screen flow, interactive checklist, findings table, readability checks,
Docker and hosting work per ../week-5-plan.md.

## Blocked

No implementation blocker. Week 3 framework-reference review remains unresolved.
Repository ownership/transfer needs resolution before deployment per the brief.

## Ask

Week 4 LinkedIn publication remains unconfirmed.
