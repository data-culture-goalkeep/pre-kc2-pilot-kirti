# Database schema — verified current state (2026-10-21)

**Important:** This is the current schema inventory, not a completed replacement. The existing 17-table `public` schema is still used by the frontend; the eight `kc2_rebuild` staging tables are private and incomplete. No production cutover has been made.

## Existing public application schema (17 tables)
`source_files`, `academic_years`, `grades`, `subjects`, `assessment_periods`, `assessment_score_codes`, `attendance_status_codes`, `students`, `student_grade_enrollments`, `grade_subjects`, `assessment_competencies`, `assessment_activities`, `student_assessments`, `assessment_scores`, `attendance_months`, `attendance_days`, `student_measurements`.

Authoritative creation SQL:
`supabase/migrations/20261001074553_create_phase1_schema.sql`.

## Replacement staging schema (8 tables)

Schema namespace: `kc2_rebuild`. All eight tables have RLS enabled and no client-access policies. The schema itself is not exposed to `anon` or `authenticated`.

| Table | Purpose | Columns |
|---|---|---|
| `import_batches` | Import provenance | batch_id, source_drive_file_id, source_file_name, imported_at, file_digest, import_status |
| `import_cells` | Original spreadsheet cell trace | cell_id, batch_id, sheet_name, source_row, source_column, raw_value |
| `students` | Target cohort | student_id, original_name, english_name, birth_date, gender_raw, grade_label_raw, profile_remark_raw, batch_id, source_sheet, source_row |
| `student_private_attributes` | Sensitive profile metadata | student_id, community_raw, caste_raw |
| `assessment_entries` | Raw assessments, unmatched allowed | entry_id, batch_id, sheet_name, source_row, source_column, student_id, grade_label_raw, term_raw, subject_raw, competency_raw, activity_raw, score_raw, resolution_status |
| `attendance_entries` | Daily raw attendance | entry_id, batch_id, sheet_name, source_row, source_column, student_id, calendar_date, grade_label_raw, status_raw, resolution_status |
| `measurement_entries` | Monthly raw weight/height | entry_id, batch_id, sheet_name, source_row, source_month, source_year, student_id, weight_raw, height_raw, resolution_status |
| `import_exceptions` | Unresolved source matching | exception_id, batch_id, sheet_name, source_row, source_column, issue_code, review_status, reviewer_note, created_at |

Applied staging DDL source (committed proposal):
`supabase/proposals/20261021_rebuild_staging_schema.sql`.

## Live counts checked 2026-10-21
- Original students: 188.
- Staged students: 148.
- Staged raw monthly measurements: 502.
- Staged daily attendance: 0.
- Staged assessments: 0.
- Staging import batches: 2.
- Names in staging were intentionally left null when the Drive connector presented redacted placeholders.
- Six staged student birth dates were not successfully parsed.

## Cutover blockers
1. Trusted, unmasked source names and invalid DOB review.
2. Auditable complete attendance and assessment import with original cell trace and conflict queue.
3. Resolve unlinked VI STD assessment rows without inventing student identity.
4. Reconcile repeated BMI records and workbook overlap.
5. Verify recoverable backup and restore capability.
6. Test application queries and restricted RLS before moving the frontend.

No old data should be dropped or replaced until all gates pass.
