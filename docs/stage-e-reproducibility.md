# Stage E data migration reproducibility

Stage E loads the sanitized KC2 Phase 1 source workbooks into the schema created by `supabase/migrations/20261001074553_create_phase1_schema.sql`.

The migration source files are **not committed to GitHub**. They remain in the sanitized Google Drive source folder:

- Folder: https://drive.google.com/drive/folders/1YrUTXKw2Gk1LQ37lz6Xg-N8BDE-P2fAD?usp=drive_link
- Exact workbook file IDs, canonical Drive titles, and expected exported `.xlsx` filenames are pinned in `scripts/stage_e/source_manifest.json`.

This avoids committing large source files and keeps the repository free of source-data copies. Export/download the eleven pinned sanitized workbooks to a local directory before running Stage E.

## Files

- `scripts/stage_e/source_manifest.json` — authoritative Stage E source inventory.
- `scripts/stage_e/stage_e_common.py` — source parsing, normalization, duplicate detection, failure capture, and failure-log generation.
- `scripts/stage_e/import_stage_e.py` — dry-run/import reconciliation process.
- `scripts/stage_e/generate_failure_log.py` — failure-log-only command; never writes to Supabase.
- `scripts/stage_e/validate_stage_e.py` — read-only database validation/reconciliation.
- `scripts/stage_e/test_stage_e_parser.py` — regression test for the accepted sanitized-source snapshot.
- `requirements-stage-e.txt` — Python dependencies.

The accepted Stage E failure artifact is retained externally in the same Drive folder as `KC2_Stage_E_Migration_Failure_Log.xlsx`: https://docs.google.com/spreadsheets/d/1V3RY6DtG90uZeZI5FSJ2IRNjsFSp4dgl/edit?usp=drivesdk

## Environment

Use Python 3.11+:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-stage-e.txt
```

Environment variables:

- `KC2_SOURCE_DIR` — local directory containing the eleven exported `.xlsx` files named exactly as specified by the manifest.
- `SUPABASE_DB_URL` — PostgreSQL connection string for the target Supabase database. Required only for `--apply` and database validation. Never commit it.

## Dry-run and failure log

Dry-run is the default. It parses all sources, validates required relationships and score/status domains, computes duplicate candidates, and writes the failure log, but performs **no database writes**.

```bash
python scripts/stage_e/import_stage_e.py \
  --source-dir "$KC2_SOURCE_DIR" \
  --failure-log artifacts/KC2_Stage_E_Migration_Failure_Log.xlsx
```

Failure-log-only mode:

```bash
python scripts/stage_e/generate_failure_log.py \
  --source-dir "$KC2_SOURCE_DIR" \
  --output artifacts/KC2_Stage_E_Migration_Failure_Log.xlsx \
  --audit-json artifacts/KC2_Stage_E_Source_Audit.json
```

Failed records are never silently discarded. The workbook contains a Summary tab plus one tab per source workbook. Each failure row records source sheet, row, column where applicable, failure scope, reason, and raw value; the workbook-specific tab identifies the source workbook.

## Apply/reconcile

Only run after the Stage C schema exists:

```bash
SUPABASE_DB_URL='...' python scripts/stage_e/import_stage_e.py \
  --source-dir "$KC2_SOURCE_DIR" \
  --failure-log artifacts/KC2_Stage_E_Migration_Failure_Log.xlsx \
  --apply
```

The apply path is designed for interrupted-run recovery and reruns:

- source/reference tables use their approved unique keys;
- students and annual enrollments use their approved keys;
- `student_assessments` and `attendance_months` deliberately do **not** use the prohibited logical natural uniqueness; rerun matching uses workbook/sheet/row provenance so legitimate source duplicates remain separate records without creating a second copy of the same source row;
- cell-level tables reconcile through their approved parent/key relationships and preserve `source_column_name`;
- no source-derived rows are deleted merely because an import is rerun;
- all writes run inside one database transaction.

After reconciliation, duplicate flags are recomputed for every member of duplicate groups:

- assessment: `(student_id, academic_year_id, grade_subject_id, assessment_period_id)`
- attendance: `(student_id, academic_year_id, grade_id, month_number)`

Therefore the four accepted attendance duplicate groups/eight records are produced correctly by committed logic and no manual correction is required on a reproducible run.

## Intentional source handling

Only approved/mechanically safe transformations are performed:

- integer assessment scores `1-10` → `numeric_score`;
- assessment `A`, `0`, `77`, `87`, `89`, and any other non-integer/out-of-range score are logged and not inserted as valid scores;
- attendance retains the exact value in `raw_status_code` and trims surrounding whitespace only for `normalized_status_code`;
- attendance meanings are `P = Present`, `A = Absent`, `H = Holiday`, and `NA = Not Applicable`;
- raw attendance code `N` remains semantically unresolved pending an explicit normalization decision;
- template activity headers beginning with `<activity_name>` (including numbered source variants) are represented as the approved placeholder `<activity_name>` with `is_placeholder=true`;
- `A. LKG` maps to `LKG` and `B. UKG` maps to `UKG`, while preserving the original source label;
- EVS, Science, and Social Science remain distinct subjects.

## Validation

`validate_stage_e.py` is read-only:

```bash
SUPABASE_DB_URL='...' python scripts/stage_e/validate_stage_e.py \
  --source-dir "$KC2_SOURCE_DIR"
```

It validates:

- manifest source-file IDs and source-to-database table counts;
- provenance completeness;
- orphan enrollments/assessments/scores/attendance/days/measurements;
- assessment score representation under the integer `1-10` rule and exclusion of invalid score/code rows;
- attendance day range, raw-code presence, trim-only normalization, and approved code meanings;
- duplicate source-location detection;
- assessment/attendance duplicate group and member counts;
- removal of assessment code `A`, mapping of `A. LKG` / `B. UKG`, and preservation of raw `N` as unresolved.

## Regression test

```bash
KC2_SOURCE_DIR="$KC2_SOURCE_DIR" PYTHONPATH=scripts/stage_e \
  python -m unittest scripts/stage_e/test_stage_e_parser.py
```

The previous handover snapshot contained 47,387 valid assessment scores and 9,346 failure entries under the old `0-10/A` rule. Those two counts are no longer acceptance constants because `A` and `0` are now invalid. Before the correction migration is applied or the branch is merged as an accepted backend baseline, rerun the parser against all 11 sanitized workbooks and record the corrected valid-score and failure-entry counts. Stable expectations remain: 11 source files, 188 students, 317 enrollments, 3,453 assessment instances, 1,882 attendance months, 46,763 attendance days, 1,786 measurements, 50/100 assessment duplicate groups/members, 4/8 attendance duplicate groups/members, and 44 placeholder activities.

## Testing status

The original Phase 1 snapshot was previously validated against all eleven sanitized workbook exports. The PM-approved corrections in this branch change the valid-score domain and therefore require a new source regression/failure-log regeneration before acceptance. The existing production dataset has not been modified by this branch. Run the regression and dry-run first, capture the corrected counts, then apply the forward correction migration only to an explicitly approved target and rerun read-only validation.

A destructive clean-database rebuild has **not** been executed against the production Supabase project. This repository therefore demonstrates code-level reproducibility plus validated live reconciliation, not a fresh production reset/reload test.
