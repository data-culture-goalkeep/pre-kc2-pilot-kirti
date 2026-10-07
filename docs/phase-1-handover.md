# KC2 Pilot - Phase 1 Final Handover

## 1. Objective and scope
Phase 1 delivers a source-grounded, auditable Supabase model for the sanitized KC2 pilot workbooks plus a reproducible Stage E migration, failure-log, and validation workflow. It does not define application authorization, resolve ambiguous source semantics, reset production, demonstrate a clean isolated rebuild, or start Phase 2.

## 2. Source inventory
Authoritative inventory: scripts/stage_e/source_manifest.json. Sanitized sources remain external to Git in the pinned Drive folder:
https://drive.google.com/drive/folders/1YrUTXKw2Gk1LQ37lz6Xg-N8BDE-P2fAD?usp=drive_link

Expected local location is KC2_SOURCE_DIR, with filenames exactly as the manifest specifies.

| Source | Type |
| --- | --- |
| UKG | assessment |
| LKG | assessment |
| Class 8 | assessment |
| Class 7 | assessment |
| Class 6 | assessment |
| Class 5 | assessment |
| Class 4 | assessment |
| Class 3 | assessment |
| Class 2 | assessment |
| Class 1 | assessment |
| Students & Attendance | students/attendance |

The manifest pins each of the 11 Drive file IDs, canonical Drive titles, expected exported XLSX filenames, and source types. It is the authoritative source-location contract. Source workbooks are intentionally not committed to Git.

## 3. Approved data model
Detailed model: docs/data-model.md. Mermaid views: docs/data-model-overview.md (overview) and docs/data-model-detailed.md (detailed schema). The 17 tables are source_files, academic_years, grades, subjects, assessment_periods, assessment_score_codes, attendance_status_codes, students, student_grade_enrollments, grade_subjects, assessment_competencies, assessment_activities, student_assessments, assessment_scores, attendance_months, attendance_days, and student_measurements.

Students link to annual enrollments, assessments, and attendance months. Grade/subject pairs own competencies; competencies own activities; assessments own scores; attendance months own daily attendance and at most one measurement row. Foreign keys enforce these relationships.

Every source-derived row records source_file_id, source_sheet_name, and source_row_number; cell-grain rows also record source_column_name. source_files.drive_file_id anchors provenance to the exact Drive workbook.

Assessment and attendance logical duplicates are intentionally preserved. Their natural duplicate keys are non-unique and duplicate members are marked duplicate_candidate=true.

## 4. Supabase implementation
Migration: supabase/migrations/20261001074553_create_phase1_schema.sql. It creates all 17 tables.

Important controls include primary/foreign keys, approved dimension/grain uniqueness, assessment numeric-score versus score-code exclusivity, attendance month/day ranges, measurement checks, nonblank cell provenance, lookup/FK indexes, and non-unique assessment/attendance natural-key indexes.

RLS is enabled on all 17 public tables. No client-facing RLS policies are defined because the application authorization model is not approved. Client authorization is therefore a known limitation/future concern, not a completed Phase 1 capability.

## 5. Stage E migration
Importer: scripts/stage_e/import_stage_e.py.

Dry-run is the default and performs no DB writes:

    python scripts/stage_e/import_stage_e.py --source-dir "$KC2_SOURCE_DIR" --failure-log artifacts/KC2_Stage_E_Migration_Failure_Log.xlsx

Writes require both --apply and SUPABASE_DB_URL:

    SUPABASE_DB_URL='...' python scripts/stage_e/import_stage_e.py --source-dir "$KC2_SOURCE_DIR" --failure-log artifacts/KC2_Stage_E_Migration_Failure_Log.xlsx --apply

The apply path verifies the approved schema and runs writes in one transaction. Reference entities/students/enrollments reconcile through approved keys. Assessment and attendance parents reconcile by source workbook + sheet + row provenance, preserving legitimate logical duplicates. Score/day cells reconcile through their parent and activity/day keys. Duplicate flags are recomputed after reconciliation.

## 6. Data-quality handling
PM-confirmed rules:
- Numeric assessment scores 0-10 are valid.
- Assessment `A` is valid and means Absent. It remains stored as a score code with its raw source value preserved.
- For derived calculations only, `A` contributes effective value 0 and remains included in the denominator.
- Scores 77, 87, 89, and unrecognized non-numeric values are failure evidence, not valid score rows.
- `student_assessments.reported_average_score` remains source-reported historical data and is not overwritten by derived calculations.
- Attendance meanings are P=Present, A=Absent, H=Holiday, and NA=Not Applicable.
- Raw attendance code N remains unresolved pending an explicit normalization decision.
- A. LKG maps to LKG and B. UKG maps to UKG while preserving source_grade_label.
- Placeholder activity headers remain normalized to literal <activity_name> with is_placeholder=true; the previous snapshot contained 44.
- Attendance whitespace: exact raw value preserved; surrounding whitespace only is trimmed for normalized status.
- Incomplete/failed records: recorded in the failure log, never silently discarded.
- EVS, Science, and Social Science remain distinct subjects.

## 7. Duplicate handling
Assessment duplicate key: student + academic year + grade-subject + assessment period. Accepted snapshot: **50 groups / 100 members**.

Attendance duplicate key: student + academic year + grade + month. Accepted snapshot: **4 groups / 8 members**.

Every group member receives duplicate_candidate=true; duplicates are not collapsed/deleted.

## 8. Failure log
Generation:

    python scripts/stage_e/generate_failure_log.py --source-dir "$KC2_SOURCE_DIR" --output artifacts/KC2_Stage_E_Migration_Failure_Log.xlsx --audit-json artifacts/KC2_Stage_E_Source_Audit.json

Accepted artifact: KC2_Stage_E_Migration_Failure_Log.xlsx in the sanitized-source Drive folder. Generated artifacts under artifacts/ are not committed.

Structure: Summary sheet plus one sheet per source workbook. Failure rows contain source sheet, row, column where applicable, failure scope, reason, and raw value. Accepted snapshot: **9,346 failure entries**. The confirmed `0-10/A` storage rule preserves the accepted score-failure classification.

## 9. Validation
Read-only validation:

    SUPABASE_DB_URL='...' python scripts/stage_e/validate_stage_e.py --source-dir "$KC2_SOURCE_DIR"

Regression:

    KC2_SOURCE_DIR="$KC2_SOURCE_DIR" PYTHONPATH=scripts/stage_e python -m unittest scripts/stage_e/test_stage_e_parser.py

Checks cover source registry/counts, provenance, orphans, `0-10/A` assessment representation, `A = Absent`, exclusion of 77/87/89 and unknown score codes, approved attendance meanings, trim-only normalization, duplicate source locations, duplicate groups/member flags, mapped LKG/UKG labels, and raw N remaining unresolved.

| Metric | Validated count |
| --- | ---: |
| source files | 11 |
| students | 188 |
| enrollments | 317 |
| assessments | 3,453 |
| valid assessment scores | 47,387 |
| attendance months | 1,882 |
| attendance days | 46,763 |
| measurements | 1,786 |
| assessment duplicates | 50 groups / 100 members |
| attendance duplicates | 4 groups / 8 members |
| placeholder activities | 44 |
| failure entries | 9,346 |

The accepted live dataset was reconciled read-only. **No clean isolated Stage C-to-Stage E end-to-end database rebuild has been performed. Production was not reset/rebuilt.**

## 10. Repository structure, environment, and run order
- supabase/migrations/20261001074553_create_phase1_schema.sql - Stage C schema.
- docs/data-model.md - model decisions.
- docs/data-model-overview.md - simplified Mermaid ERD covering all 17 Phase 1 tables.
- docs/data-model-detailed.md - detailed Mermaid ERD covering all 17 tables, columns, keys, and relationships.
- docs/stage-e-reproducibility.md - detailed Stage E runbook.
- docs/phase-1-handover.md - final handover/acceptance map.
- scripts/stage_e/source_manifest.json - authoritative source inventory.
- scripts/stage_e/stage_e_common.py - parser/normalization/duplicates/failure writer.
- scripts/stage_e/import_stage_e.py - importer.
- scripts/stage_e/generate_failure_log.py - failure-log generator.
- scripts/stage_e/validate_stage_e.py - read-only validator.
- scripts/stage_e/test_stage_e_parser.py - regression test.
- requirements-stage-e.txt - pinned dependencies.

Requires Python 3.11+, openpyxl==3.1.5, psycopg[binary]==3.2.10, all 11 workbook exports, and SUPABASE_DB_URL only for apply/DB validation.

    python -m venv .venv
    . .venv/bin/activate
    pip install -r requirements-stage-e.txt
    export KC2_SOURCE_DIR=/path/to/sanitized/exports

Run order: verify manifest/sources; run regression; run importer dry-run and inspect failure log; validate an accepted DB read-only; use --apply only for an explicitly approved target with Stage C schema/credentials. Routine validation never authorizes a production reset.

## 11. Known limitations / decisions
- Source workbooks remain external to Git by design.
- Clean isolated rebuild is not demonstrated; reproducibility evidence is source regression/failure-log regeneration plus read-only live reconciliation.
- Assessment storage domain is numeric 0-10 or score code A.
- Assessment A means Absent; for derived calculations A contributes 0 and remains in the denominator.
- Source-reported assessment averages remain historical source values and are not overwritten.
- P/A/H/NA attendance meanings are approved; raw N remains unresolved.
- A. LKG / B. UKG are mapped to LKG / UKG while source labels are preserved.
- Placeholder activities remain intentional configurable placeholders.
- 77/87/89 and other unrecognized non-numeric assessment values remain failure evidence.
- Assessment/attendance duplicates are preserved and flagged.
- RLS is enabled but client-facing authorization policies are not defined.
- Phase 2 has not started.

## 12. Phase 1 acceptance checklist
| Requirement | Status | Evidence/location | Limitation |
| --- | --- | --- | --- |
| 11 sanitized sources inventoried | Completed | source_manifest.json; pinned Drive | External to Git |
| Approved source-grounded model | Completed | docs/data-model.md | Ambiguous semantics unresolved |
| Approved 17-table schema | Completed | Stage C migration | No handover schema changes |
| Relationships/constraints/indexes | Completed | Stage C migration | Within approved model |
| Source provenance | Completed | schema + Stage E code | Column provenance on cell-grain rows |
| RLS enabled | Completed | Stage C migration | No client policies |
| Stage E importer | Completed | import_stage_e.py | Clean rebuild not demonstrated |
| Dry-run/no-write mode | Completed | importer default | None |
| Rerun/reconciliation | Completed | provenance/upsert logic | Clean rebuild not demonstrated |
| Transactional apply | Completed | importer transaction | Approved targets only |
| Data-quality handling | Completed | parser + failure log | Intentional unresolved values remain |
| Assessment duplicate handling | Completed | parser/importer/test | 50/100 snapshot |
| Attendance duplicate handling | Completed | parser/importer/test | 4/8 snapshot |
| Failure-log regeneration | Completed | generator + external artifact | Artifact not committed |
| 9,346 failures reproducible | Completed | regression/generated log | Accepted snapshot |
| Read-only DB validation | Completed | validate_stage_e.py | DB connection required |
| Accepted live reconciliation | **Pending correction apply + validation** | Stage E evidence | Live DB not modified by this branch |
| Clean isolated rebuild | **Not completed** | documented limitation | Not run |
| PM correction package | Completed in PR | parser/importer/validator/migration/docs | Requires source rerun before merge/apply |
| Phase 2 | Not started by design | phase boundary | Outside Phase 1 |

## Handover boundary
The PM correction package in this branch clarifies score semantics/calculation behavior, attendance meanings, and grade-label mappings while preserving the accepted Phase 1 score observations and counts. Merge/apply decisions remain human-controlled. The branch does not modify validated live data. Review the PR and rerun the workbook-backed regression when the local sanitized exports are available before any explicitly approved database migration.
