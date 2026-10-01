# KC2 Phase 1 Data Model — Overview

This Mermaid ERD is a simplified relationship view generated strictly from the approved Phase 1 schema in:

`supabase/migrations/20261001074553_create_phase1_schema.sql`

It shows all 17 approved tables while intentionally omitting columns so reviewers can see the main entity relationships clearly.

```mermaid
erDiagram
    SOURCE_FILES ||--o{ ACADEMIC_YEARS : "source_file_id"
    SOURCE_FILES ||--o{ GRADES : "source_file_id"
    SOURCE_FILES ||--o{ SUBJECTS : "source_file_id"
    SOURCE_FILES ||--o{ ASSESSMENT_PERIODS : "source_file_id"
    SOURCE_FILES ||--o{ ASSESSMENT_SCORE_CODES : "source_file_id"
    SOURCE_FILES ||--o{ ATTENDANCE_STATUS_CODES : "source_file_id"
    SOURCE_FILES ||--o{ STUDENTS : "source_file_id"
    SOURCE_FILES ||--o{ STUDENT_GRADE_ENROLLMENTS : "source_file_id"
    SOURCE_FILES ||--o{ GRADE_SUBJECTS : "source_file_id"
    SOURCE_FILES ||--o{ ASSESSMENT_COMPETENCIES : "source_file_id"
    SOURCE_FILES ||--o{ ASSESSMENT_ACTIVITIES : "source_file_id"
    SOURCE_FILES ||--o{ STUDENT_ASSESSMENTS : "source_file_id"
    SOURCE_FILES ||--o{ ASSESSMENT_SCORES : "source_file_id"
    SOURCE_FILES ||--o{ ATTENDANCE_MONTHS : "source_file_id"
    SOURCE_FILES ||--o{ ATTENDANCE_DAYS : "source_file_id"
    SOURCE_FILES ||--o{ STUDENT_MEASUREMENTS : "source_file_id"

    STUDENTS ||--o{ STUDENT_GRADE_ENROLLMENTS : "student_id"
    ACADEMIC_YEARS ||--o{ STUDENT_GRADE_ENROLLMENTS : "academic_year_id"
    GRADES o|--o{ STUDENT_GRADE_ENROLLMENTS : "grade_id"

    GRADES ||--o{ GRADE_SUBJECTS : "grade_id"
    SUBJECTS ||--o{ GRADE_SUBJECTS : "subject_id"
    GRADE_SUBJECTS ||--o{ ASSESSMENT_COMPETENCIES : "grade_subject_id"
    ASSESSMENT_COMPETENCIES ||--o{ ASSESSMENT_ACTIVITIES : "competency_id"

    STUDENTS ||--o{ STUDENT_ASSESSMENTS : "student_id"
    ACADEMIC_YEARS ||--o{ STUDENT_ASSESSMENTS : "academic_year_id"
    GRADE_SUBJECTS ||--o{ STUDENT_ASSESSMENTS : "grade_subject_id"
    ASSESSMENT_PERIODS ||--o{ STUDENT_ASSESSMENTS : "assessment_period_id"
    STUDENT_ASSESSMENTS ||--o{ ASSESSMENT_SCORES : "student_assessment_id"
    ASSESSMENT_ACTIVITIES ||--o{ ASSESSMENT_SCORES : "activity_id"
    ASSESSMENT_SCORE_CODES o|--o{ ASSESSMENT_SCORES : "score_code"

    STUDENTS ||--o{ ATTENDANCE_MONTHS : "student_id"
    ACADEMIC_YEARS ||--o{ ATTENDANCE_MONTHS : "academic_year_id"
    GRADES ||--o{ ATTENDANCE_MONTHS : "grade_id"
    ATTENDANCE_MONTHS ||--o{ ATTENDANCE_DAYS : "attendance_month_id"
    ATTENDANCE_STATUS_CODES o|--o{ ATTENDANCE_DAYS : "normalized_status_code"
    ATTENDANCE_MONTHS ||--o| STUDENT_MEASUREMENTS : "attendance_month_id"
```

## Notes

- `student_grade_enrollments.grade_id` is nullable in the approved schema.
- `assessment_scores.score_code` is nullable; valid rows contain either a numeric score or a score code according to the approved check constraint.
- `attendance_days.normalized_status_code` is nullable.
- The model intentionally does not enforce natural-key uniqueness for `student_assessments` or `attendance_months`; legitimate source duplicates are retained and flagged using `duplicate_candidate`.
