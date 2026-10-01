# KC2 Phase 1 Database Schema

This document describes the Stage C schema implemented for the KC2 pilot. It is based on the approved Stage B source-grounded model. No source data is migrated by this stage.

## Source tracking

Every source-derived record is traceable to its source workbook, sheet, and row using:

- `source_file_id` -> `source_files.source_file_id`
- `source_sheet_name`
- `source_row_number`

Cell-level records also include `source_column_name`.

## Core grains

| Table | Grain |
| --- | --- |
| source_files | one source workbook |
| academic_years | one source-supported academic year label |
| grades | one canonical grade |
| subjects | one source-supported subject |
| assessment_periods | one assessment period |
| assessment_score_codes | one valid non-numeric assessment score code |
| attendance_status_codes | one mechanically normalized attendance status code |
| students | one student |
| student_grade_enrollments | one student / academic-year placement cell |
| grade_subjects | one grade / subject pairing |
| assessment_competencies | one competency in one grade-subject definition |
| assessment_activities | one activity column in one competency |
| student_assessments | one valid source assessment row |
| assessment_scores | one valid populated activity score cell |
| attendance_months | one valid source student-month attendance row |
| attendance_days | one populated daily attendance cell |
| student_measurements | one set of measurements attached to one attendance-month source row |

## Important unresolved source values

The schema preserves these without inferring business meanings:

- assessment code `A`
- attendance codes `H`, `N`, `NA`
- literal assessment placeholder `<activity_name>`
- roster labels `A. LKG` / `B. UKG`

Whitespace-only normalization is allowed for attendance codes, e.g. `" P"` -> `"P"` and `"H "` -> `"H"`, while the original value remains in `raw_status_code`.

Source scores outside the supported `0-10` / `A` domain (including the observed `77`, `87`, and `89`) are not representable as valid `assessment_scores`; they are intended for the migration failure log in Stage F.

## Duplicate handling

The schema intentionally does **not** enforce natural-key uniqueness for:

- `student_assessments(student_id, academic_year_id, grade_subject_id, assessment_period_id)`
- `attendance_months(student_id, academic_year_id, grade_id, month_number)`

These combinations are indexed non-uniquely. Valid source duplicates remain separate rows and are marked with `duplicate_candidate = true` during data migration.

## RLS

All Phase 1 tables are created in `public`, which is an exposed Supabase schema, so RLS is enabled on every table. No client-facing RLS policies are created in Stage C because the application authorization model is not yet defined. Service-role/server-side migration workflows can still operate as appropriate.

## Migration

Schema migration:

- `supabase/migrations/20261001074553_create_phase1_schema.sql`

Stage C is schema-only. Source-data migration is intentionally deferred.
