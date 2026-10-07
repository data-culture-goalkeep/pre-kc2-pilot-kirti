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

Key confirmed rules:
- assessment storage: numeric `0-10` or score code `A`;
- assessment `A` means **Absent**, remains stored as `A`, and contributes effective score `0` while remaining in the denominator for derived averages;
- `77`, `87`, `89`, and unrecognized non-numeric assessment values remain invalid/failure evidence;
- grade labels: `A. LKG -> LKG`, `B. UKG -> UKG`, preserving `source_grade_label`;
- attendance meanings: `P=Present`, `A=Absent`, `H=Holiday`, `NA=Not Applicable`; raw `N` remains unresolved;
- placeholder activities and duplicate-candidate preservation remain unchanged;
- source-reported `student_assessments.reported_average_score` remains untouched.

Forward database correction migration:
`supabase/migrations/20261005150500_apply_pm_phase1_corrections.sql`

The migration is non-destructive to assessment observations and must not be applied to production without explicit approval.

### Phase 2 frontend follow-up

The PM frontend lives on a separate branch and is outside PR #5. Its current assessment text/input still reflects the superseded `1-10 only` assumption. Phase 2 integration must update that UI to accept/display numeric `0-10` plus `A = Absent`, keeping actual zero distinct from absence while using `A -> 0` only in calculation logic.

