# Copyable provider and responsible-lead requests

Added November 1, 2026. Confirmed Fix First actions now include `provider_requests`
for human review. These are drafts: no message is sent and no system change is
executed. The app displays them in copyable text blocks; TXT reports include the
same drafts under Copyable provider/lead request.

Each request identifies the scoring entity and rule. Available vendor, product,
version and CVE evidence is included for software findings. Drafts ask for dated
evidence for reassessment, an owner, a cost estimate and a safe timetable before
changes. Governance actions are addressed to the responsible lead rather than
assuming a technology vendor can resolve them.

Only confirmed occurrences produce requests. Review-only occurrences remain in
the verification section. R16, R20 and R21 inspect their separate answer branches
so a confirmed failure in one answer does not assert failure of another. Combined
Q10 and Q17/router conditions still require component-by-component review rather
than guessing which component failed. Requests do not establish a breach,
notification duty, completed remediation, guaranteed safety or a score gain.

Exact repeated-action consolidation preserves the distinct request drafts and
keeps the existing max-points/max-effort ranking. Priorities, grouping, finding
statuses, scoring formulas and provisional warnings are unchanged.

Tests cover branch-specific backup/governance/reporting drafts, unresolved-only
and mixed evidence, software/CVE identity, consolidation without summed priority,
TXT propagation and unchanged 65/82/80 fictional scenario scores. The initial
focused run passed 64 tests. Browser/TXT manual confirmation is the next step.

Latest validation: 2,486 tests passed, excluding the known locally stalled
Streamlit AppTest file. High-severity Bandit check passed (zero medium/high;
five existing low findings). New UI/TXT manual checks and CI are not yet claimed.
