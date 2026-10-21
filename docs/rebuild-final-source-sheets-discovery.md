# Vanavil KC-2 rebuild from final source sheets — design discovery

**Status: analysis only. No live database or app changes approved or performed.**

## Final source folder
https://drive.google.com/drive/folders/1b8s3F3X79PHYSXWmZ7-TTb4JGQYHw9EH

Seven files found:
1. Student Profile Sheet (Google Sheet; Student wise / Sheet2)
2. School Grade sheet 2025-2026 (Google Sheet; nine tabs LKG through VII STD)
3. Copy of BMI Details-Vanavil (Google Sheet; 2024, 2025, Sheet4, 2026)
4. Copy of School Attendnace- 2025-2026.xlsx
5. Copy of January attendance 2026.xlsx
6. Copy of Feburary Attendnace.xlsx
7. Copy of March attendance 2026.xlsx

## Source observations (confirmed, not assumed)
- Student Profile Sheet contains S.NO, NAME, English Names, Remark, Date Of birth, GRADE, GENDER, Student id, COMMUNITY and CASTE. Tamil and English names both appear. Some Remarks indicate a student has left, including term-specific notes. These should be preserved as **source values**, not silently mapped to an invented enrolment status.
- Nine grade tabs use numerous, often merged/multi-line subject, activity and term headings. The layout includes Tamil, English and Montessori content; the exact competency mapping requires detailed sheet-by-sheet reconstruction, not a one-row header parser.
- The BMI 2026 tab has student identifiers and monthly pairs of weight and height columns. Its title/header includes a year-label inconsistency that needs source confirmation; do not infer nutritional/BMI classification thresholds.
- January, February, March and the consolidated school attendance workbooks have differing header layouts and representations of holiday days (e.g. blank, long-text holiday or H). Some monthly rows have missing Student IDs. The consolidated workbook includes March 2026 records; therefore source periods overlap. Re-importing all workbooks naively could double-count attendance.
- February and March files include names with spelling variations versus the profile sheet. Matching by English name alone is not safe.

## Preliminary replacement data model (not yet a final ERD)
Retain or redesign around stable entities:
- source_files / import_runs / source_row_refs: versioned provenance and reversible imports
- students: immutable student IDs, both original Tamil name and English name where available; treat sensitive profile attributes with limited access
- academic_years, grades, student_grade_enrollments: grade by academic year, with original grade labels
- subjects, grade_subjects, assessment_periods, competencies, activities: match actual nine-sheet layout
- student_assessments, assessment_scores: preserve raw score and original activity/source context; preserve duplicate candidates and unresolved codes
- attendance_months, attendance_days, attendance_status_codes: key on student/year/month/day; reconcile overlaps and holiday code variations
- student_measurements: by student + measurement month/year, preserving raw height/weight and source reference; review any link to attendance and BMI calculations
- staff roles / follow-up tables are a separate Phase 3 proposal, not part of the final source sheets.

**Exact tables, column names, constraints, and relationships remain subject to a complete field-by-field source inventory and comparative schema review.**

## Baseline (existing Kirti Pilot KC)
Supabase project `tyhwkudogenugnnfgxav`, existing approved 17-table schema:
- Students 188; enrolments 317; assessments 3,453; activity scores 47,387
- Attendance month records 1,882; attendance days 46,763
- Duplicate assessment candidates 100; duplicate attendance candidates 8
- All 17 tables have RLS enabled; only seven have authenticated read policies.

These are **old database counts**, not counts from the revised source files.

## Mandatory pre-rebuild gates
1. Full detailed inventory: tabs, column locations, student IDs, dates, assessment term/activity mapping, school-year overlaps, raw attendance/score values.
2. Produce explicit source-to-target mapping, row-count reconciliation and unmatched / duplicate review report. Do not invent missing identifiers.
3. Identify all frontend query contracts and migrations which reference existing tables; plan auth/RLS changes and cutover.
4. Verify recoverable backup/restore **including database, auth identities/policies, provenance and schema**, rather than assume a backup exists.
5. Design and test new schema and import in a safe staging schema or isolated environment; ensure sensitive student information is not copied into public assets or logs.
6. Present a dry-run diff showing new, changed, omitted and unresolved records; obtain explicit approval for any destructive deletion.
7. If approved, perform an orderly cutover with rollback criteria, data checks, authorized user-access tests and Vercel smoke tests.

## Current decision
The user's instruction is to proceed with the **design-first rebuild recommendation**, not to delete live database tables before the new schema and backup have been reviewed. Live database and deployed frontend must remain operational until cutover.
