-- READ-ONLY QA QUERIES for the proposed kc2_rebuild staging schema.
-- Execute only after schema proposal has been reviewed, deployed to an approved
-- isolated environment, and populated from source workbooks.
-- These checks are not proof of source completeness without per-file source counts.
select 'staged_students' as metric, count(*)::bigint as value from kc2_rebuild.students
union all select 'staged_batches',count(*) from kc2_rebuild.import_batches
union all select 'assessment_rows',count(*) from kc2_rebuild.assessment_entries
union all select 'attendance_rows',count(*) from kc2_rebuild.attendance_entries
union all select 'measurement_rows',count(*) from kc2_rebuild.measurement_entries
union all select 'open_exceptions',count(*) from kc2_rebuild.import_exceptions where review_status='open';

select 'assessment' record_type,resolution_status,count(*) as rows
from kc2_rebuild.assessment_entries group by resolution_status
union all select 'attendance',resolution_status,count(*)
from kc2_rebuild.attendance_entries group by resolution_status
union all select 'measurement',resolution_status,count(*)
from kc2_rebuild.measurement_entries group by resolution_status
order by 1,2;

-- Distinct conflicting source claims for the same date and student.
select student_id,calendar_date,count(*) records,
       count(distinct nullif(btrim(status_raw),'')) distinct_nonblank_statuses
from kc2_rebuild.attendance_entries
where student_id is not null and calendar_date is not null
group by student_id,calendar_date
having count(*)>1
order by student_id,calendar_date;

-- Multiple measurement source rows for same student and reported month.
select student_id,source_year,source_month,count(*) records,
       count(distinct coalesce(weight_raw,'') || ' / ' || coalesce(height_raw,'')) variants
from kc2_rebuild.measurement_entries
where student_id is not null and source_year is not null and source_month is not null
group by student_id,source_year,source_month
having count(*)>1
order by student_id,source_year,source_month;

-- Unmatched source entries are not eligible for published scoring.
select sheet_name,count(*) assessment_rows_pending
from kc2_rebuild.assessment_entries where student_id is null
group by sheet_name order by sheet_name;

-- Confirm staging RLS and absence of policies (supplement with a real anon client test).
select c.relname,c.relrowsecurity,
       count(p.policyname) as policy_count
from pg_class c
join pg_namespace n on n.oid=c.relnamespace
left join pg_policies p on p.schemaname=n.nspname and p.tablename=c.relname
where n.nspname='kc2_rebuild' and c.relkind='r'
group by c.relname,c.relrowsecurity order by c.relname;
