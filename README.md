# KC-2 Pilot Project

## Phase 1 handover

The authoritative Phase 1 operator/reviewer entry point is:

- `docs/phase-1-handover.md` — final Phase 1 scope, source inventory, schema/migration overview, validated counts, known limitations, and acceptance checklist.
- `docs/data-model.md` — approved Stage C data model.
- `docs/data-model-overview.md` — simplified Mermaid ERD for all 17 Phase 1 tables.
- `docs/data-model-detailed.md` — detailed Mermaid ERD with all 17 tables, columns, keys, and relationships.
- `docs/stage-e-reproducibility.md` — detailed Stage E import, failure-log, rerun, and validation workflow.

Stage E code lives under `scripts/stage_e/`. The sanitized source workbooks remain in the manifest-pinned Google Drive folder and are intentionally not committed to this repository.

Before operating on data, read the Phase 1 handover and Stage E runbook. Do not treat routine validation as permission to reset/rebuild production, change the approved schema, resolve ambiguous source semantics, or begin Phase 2.


## PM correction branch

The PM-approved Phase 1 corrections are implemented on the review branch `feature/pm-backend-frontend-integration`.

Key corrections:
- assessment scores: numeric 0-10 or code `A`; `A` means Absent and is preserved as a code; `77`, `87`, `89`, and unknown non-numeric values remain invalid;
- grade labels: `A. LKG -> LKG`, `B. UKG -> UKG`;
- attendance meanings: `P=Present`, `A=Absent`, `H=Holiday`, `NA=Not Applicable`; raw `N` remains unresolved;
- placeholder activities and duplicate-candidate preservation remain unchanged.

Forward database correction migration:
`supabase/migrations/20261005150500_apply_pm_phase1_corrections.sql`

Do not apply it to production until the sanitized-source regression/failure log has been rerun and the PR has been reviewed.
