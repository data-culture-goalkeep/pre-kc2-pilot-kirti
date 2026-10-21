# Replacement database v2: proposed schema and import gates

Status: DESIGN ONLY. No execution against Supabase. Uses the seven final files in the user-approved Drive folder.

## Verified cohort
148 unique student IDs in final Student Profile Sheet. All 148 match current database students; 40 current IDs are outside the revised cohort (SCH-26-0001 to SCH-26-0040). Preserve their associated histories in a recoverable backup.

## Proposed relational groups
1. students: student_id, original_language_name, english_name, birth_date, gender, raw_profile_remark; restrict sensitive fields such as community and caste separately by role.
2. academic_years, grades, student_grade_enrollments: school-year and normalized grade with source grade label retained.
3. assessment_periods, subjects, competencies, activities, assessment_records and assessment_scores: one score per student, source workbook/tab, term, activity and recorded score; preserve raw input and cell provenance.
4. attendance_periods and attendance_days: daily attendance with raw code, standardized code when approved, source workbook, sheet/row/column and holiday handling. Retain source summary values for verification.
5. student_measurements: per student, date or month, weight, height, source cell; never infer medical classifications without agreed standard.
6. import_runs, import_source_rows and import_exceptions: filename, file ID, sheet, row, ingestion timestamp, source hashes, unmatched IDs and conflict decisions.
7. staff roles and Phase 3 follow-up workflow remain separate permission-controlled workstreams. Imported student data must not automatically become editable to any signed-in user.

Final SQL constraints, type definitions, foreign keys and exact table count require complete spreadsheet mapping, especially ambiguous grade sheets.

## Newly confirmed assessment exceptions
- LKG column A contains repeated IDs in separate rows: 24 recognizable occurrences but only 21 unique IDs. Source rows must be interpreted by term/section, not deduplicated blindly.
- UKG column A includes mistyped SHC prefixes, including IDs with inconsistent spaces/hyphens. Do not silently rewrite IDs: map to stable student IDs only with an auditable correction list.
- VI STD has populated score columns but no recognizable student IDs in inspected columns A:Z, rows 1:32. Treat as unresolved until a verified student index/reference is found; do not import scores onto guessed students.
- Assessment term, subject, competency and activity headings span multiple rows and differ by tab. Each tab requires a column-coordinate map.

## BMI validation
2026 column D: 98 populated ID occurrences, 95 unique IDs; all are included in revised 148 IDs. Three extra occurrences require row-level validation before deduplication.

## Attendance validation
January, February, March and consolidated attendance workbooks have differing headers and overlapping reporting periods. Some standalone records lack IDs; consolidated March provides IDs on many rows. Preserve raw statuses, do not convert blank to absence, and do not double-import overlapping student-days.

## Import sequence, without destructive actions
1. Complete per-sheet schema maps and student-resolution exception queue.
2. Stage a new schema and load with source provenance, without updating original tables.
3. Verify uniqueness, foreign keys, expected totals, daily attendance conflicts, raw-vs-computed score and attendance aggregates.
4. Verify authentication, least-privilege RLS and four frontend views against staged data.
5. Confirm restorable pre-cutover backup of the current database including 40 excluded students and histories.
6. Present exact records to omit, mapping exceptions, and a rollback procedure for explicit approval before deleting existing tables or switching frontend.

## Acceptance gate
No live write, import, drop, RLS policy change, or production cutover has been carried out. Source mapping is incomplete; the VI STD student-ID linkage must be resolved.
