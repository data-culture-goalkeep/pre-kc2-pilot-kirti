-- KC2 PM-approved Phase 1 corrections
-- Applies reviewer decisions without rewriting the original Phase 1 migration.
-- This migration is forward-only and must be applied only to an explicitly approved target.

begin;

-- 1. Assessment scores are valid only as integer 1-10.
-- Remove rows previously admitted through the old 0-10/A rule.
delete from public.assessment_scores
where score_code is not null
   or numeric_score is null
   or numeric_score < 1
   or numeric_score > 10;

-- Remove the now-invalid non-numeric score code after dependent rows are gone.
delete from public.assessment_score_codes
where score_code = 'A';

alter table public.assessment_scores
  drop constraint if exists assessment_scores_value_check;

alter table public.assessment_scores
  add constraint assessment_scores_value_check check (
    numeric_score is not null
    and score_code is null
    and numeric_score between 1 and 10
  );

-- 2. Approved grade label mappings.
update public.student_grade_enrollments e
set grade_id = g.grade_id
from public.grades g
where e.source_grade_label = 'A. LKG'
  and g.grade_code = 'LKG';

update public.student_grade_enrollments e
set grade_id = g.grade_id
from public.grades g
where e.source_grade_label = 'B. UKG'
  and g.grade_code = 'UKG';

-- 3. Approved attendance meanings.
update public.attendance_status_codes
set meaning = case status_code
  when 'P' then 'Present'
  when 'A' then 'Absent'
  when 'H' then 'Holiday'
  when 'NA' then 'Not Applicable'
  else meaning
end
where status_code in ('P','A','H','NA');

-- Raw N remains intentionally unresolved pending explicit normalization decision.

commit;
