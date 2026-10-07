-- KC2 PM-approved Phase 1 corrections
-- Applies confirmed semantic/normalization decisions without rewriting the original Phase 1 migration.
-- This migration is non-destructive and must be applied only to an explicitly approved target.
--
-- Assessment storage remains unchanged:
--   numeric_score 0-10 OR score_code='A'
-- A remains stored as raw_score_value='A', numeric_score=NULL, score_code='A'.
-- A means Absent; calculation-layer logic treats A as effective score 0 and includes it in averages.

begin;

-- 1. Confirm the meaning of the existing valid assessment score code.
-- No assessment_scores rows are deleted or rewritten.
update public.assessment_score_codes
set meaning = 'Absent'
where score_code = 'A';

-- 2. Approved grade label mappings.
-- Preserve source_grade_label exactly as imported; only fill the canonical grade_id.
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

-- Raw N remains intentionally unresolved pending an explicit approved meaning.

commit;
