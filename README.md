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
