# Stage E data migration reproducibility

Stage E loads the sanitized KC2 Phase 1 source workbooks into the schema created by `supabase/migrations/20261001074553_create_phase1_schema.sql`.

The migration source files are **not committed to GitHub**. They remain in the sanitized Google Drive source folder:

- Folder: https://drive.google.com/drive/folders/1YrUTXKw2Gk1LQ37lz6Xg-N8BDE-P2fAD?usp=drive_link
- Exact workbook file IDs and expected exported `.xlsx` filenames are pinned in `scripts/stage_e/source_manifest.json`.

This avoids committing large source files and keeps the repository free of source-data copies. Export/download the eleven pinned sanitized workbooks to a local directory before running Stage E.

## Files

- `scripts/stage_e/source_manifest.json` — authoritative Stage E source inventory.
- `scripts/stage_e/stage_e_common.py` — source parsing, normalization, duplicate detection, failure capture, and failure-log generation.
- `scripts/stage_e/import_stage_e.py` — dry-run/import reconciliation process.
- `scripts/stage_e/generate_failure_log.py` — failure-log-only command; never writes to Supabase.
- `scripts/stage_e/validate_stage_e.py` — read-only database validation/reconciliation.
- `scripts/stage_e/test_stage_e_parser.py` — regression test for the accepted sanitized-source snapshot.
- `requirements-stage-e.txt` — Python dependencies.

The accepted Stage E failure artifact is retained externally in the same Drive folder as `KC2_Stage_E_Migration_Failure_Log.xlsx`.

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

- numeric assessment scores 0–10 → `numeric_score`;
- literal assessment `A` → `score_code='A'`, with `meaning=NULL`;
- invalid scores including `77`, `87`, `89` are logged and not inserted as valid scores;
- attendance retains the exact value in `raw_status_code` and trims surrounding whitespace only for `normalized_status_code`;
- `H`, `N`, `NA` remain semantically unresolved;
- template activity headers beginning with `<activity_name>` (including numbered source variants) are represented as the approved placeholder `<activity_name>` with `is_placeholder=true`;
- `A. LKG` and `B. UKG` remain in `source_grade_label` with `grade_id=NULL`;
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
- assessment score representation and exclusion of `77`, `87`, `89`;
- attendance day range, raw-code presence, and trim-only normalization;
- duplicate source-location detection;
- assessment/attendance duplicate group and member counts;
- unresolved `A`, `H`, `N`, `NA`, and unresolved enrollment grades.

## Regression test

```bash
KC2_SOURCE_DIR="$KC2_SOURCE_DIR" PYTHONPATH=scripts/stage_e \
  python -m unittest scripts/stage_e/test_stage_e_parser.py
```

For the accepted sanitized snapshot the parser must produce: 11 source files, 188 students, 317 enrollments, 3,453 assessment instances, 47,387 valid assessment scores, 1,882 attendance months, 46,763 attendance days, 1,786 measurements, 50/100 assessment duplicate groups/members, 4/8 attendance duplicate groups/members, 44 placeholder activities, and 9,346 failure entries.

## Testing status

The parser/failure generator has been run against all eleven sanitized workbook exports and reproduces the accepted Stage E source counts, duplicate counts, placeholder count, invalid score set, and 9,346 failure entries. The existing completed live dataset has also been reconciled read-only against these expected counts and integrity checks.

A destructive clean-database rebuild has **not** been executed against the production Supabase project. This repository therefore demonstrates code-level reproducibility plus validated live reconciliation, not a fresh production reset/reload test.
