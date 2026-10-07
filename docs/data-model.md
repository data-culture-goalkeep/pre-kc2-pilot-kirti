# KC2 Phase 1 Database Schema

This document describes the Stage C schema implemented for the KC2 pilot. It is based on the approved Stage B source-grounded model. No source data is migrated by this stage.

## Mermaid data model views

- [Overview ERD](data-model-overview.md) — simplified relationship view covering all 17 approved Phase 1 tables.
- [Detailed schema ERD](data-model-detailed.md) — all 17 approved tables with columns, keys, and migration-defined relationships.

Both diagrams are generated strictly from `supabase/migrations/20261001074553_create_phase1_schema.sql`.

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

## PM-approved source handling

Reviewer decisions now applied by the Stage E parser/import path and forward correction migration:

- numeric assessment scores `0-10` are valid;
- assessment code `A` is valid and means **Absent**;
- `A` remains stored as `raw_score_value='A'`, `numeric_score=NULL`, `score_code='A'`; it is never rewritten to numeric zero in source storage;
- for derived calculations, numeric scores use their numeric value and `A` uses effective value `0`; `A` remains included in the denominator;
- source values `77`, `87`, `89`, and unrecognized non-numeric score values are failure evidence rather than valid `assessment_scores`;
- `student_assessments.reported_average_score` remains source-reported data and is not overwritten by derived calculations;
- `A. LKG` maps to canonical grade `LKG`, while the original source label remains in `source_grade_label`;
- `B. UKG` maps to canonical grade `UKG`, while the original source label remains in `source_grade_label`;
- attendance meanings are `P = Present`, `A = Absent`, `H = Holiday`, and `NA = Not Applicable`;
- raw attendance code `N` remains unresolved pending a separate explicit normalization decision;
- literal assessment placeholder `<activity_name>` remains an intentional configurable placeholder.

Whitespace-only normalization is allowed for attendance codes, e.g. `" P"` -> `"P"` and `"H "` -> `"H"`, while the original value remains in `raw_status_code`.

## Duplicate handling

The schema intentionally does **not** enforce natural-key uniqueness for:

- `student_assessments(student_id, academic_year_id, grade_subject_id, assessment_period_id)`
- `attendance_months(student_id, academic_year_id, grade_id, month_number)`

These combinations are indexed non-uniquely. Valid source duplicates remain separate rows and are marked with `duplicate_candidate = true` during data migration.

## RLS

All Phase 1 tables are created in `public`, which is an exposed Supabase schema, so RLS is enabled on every table. No client-facing RLS policies are created in Stage C because the application authorization model is not yet defined. Service-role/server-side migration workflows can still operate as appropriate.

## Migration

Schema migrations:

- `supabase/migrations/20261001074553_create_phase1_schema.sql` — original Phase 1 schema.
- `supabase/migrations/20261005150500_apply_pm_phase1_corrections.sql` — non-destructive forward correction migration implementing the PM-approved score-code meaning, grade-label, and attendance-meaning decisions without rewriting the original migration.

Stage C remains the original schema baseline. The correction migration must be applied only to an explicitly approved target after source regression and dry-run review.
