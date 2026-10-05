#!/usr/bin/env python3
"""Read-only Stage E source-to-database validator."""
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from stage_e_common import expected_counts, parse_sources

CHECK_SQL={
"provenance_missing":"""with bad as (
 select 'academic_years' t,count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null) c from public.academic_years
 union all select 'grades',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null) from public.grades
 union all select 'subjects',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null) from public.subjects
 union all select 'assessment_periods',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null) from public.assessment_periods
 union all select 'assessment_score_codes',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null) from public.assessment_score_codes
 union all select 'attendance_status_codes',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null) from public.attendance_status_codes
 union all select 'students',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null) from public.students
 union all select 'student_grade_enrollments',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null or source_column_name is null) from public.student_grade_enrollments
 union all select 'grade_subjects',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null) from public.grade_subjects
 union all select 'assessment_competencies',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null) from public.assessment_competencies
 union all select 'assessment_activities',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null or source_column_name is null) from public.assessment_activities
 union all select 'student_assessments',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null) from public.student_assessments
 union all select 'assessment_scores',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null or source_column_name is null) from public.assessment_scores
 union all select 'attendance_months',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null) from public.attendance_months
 union all select 'attendance_days',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null or source_column_name is null) from public.attendance_days
 union all select 'student_measurements',count(*) filter(where source_file_id is null or source_sheet_name is null or source_row_number is null) from public.student_measurements)
 select * from bad where c<>0""",
"orphans":"""select
 (select count(*) from public.student_grade_enrollments e left join public.students s on s.student_id=e.student_id where s.student_id is null)::int orphan_enrollments,
 (select count(*) from public.student_assessments a left join public.students s on s.student_id=a.student_id where s.student_id is null)::int orphan_assessments,
 (select count(*) from public.assessment_scores sc left join public.student_assessments a on a.student_assessment_id=sc.student_assessment_id where a.student_assessment_id is null)::int orphan_scores,
 (select count(*) from public.attendance_months am left join public.students s on s.student_id=am.student_id where s.student_id is null)::int orphan_attendance,
 (select count(*) from public.attendance_days ad left join public.attendance_months am on am.attendance_month_id=ad.attendance_month_id where am.attendance_month_id is null)::int orphan_days,
 (select count(*) from public.student_measurements sm left join public.attendance_months am on am.attendance_month_id=sm.attendance_month_id where am.attendance_month_id is null)::int orphan_measurements""",
"assessment_validity":"""select
 count(*) filter(where numeric_score is not null and (numeric_score<1 or numeric_score>10))::int invalid_numeric,
 count(*) filter(where numeric_score is null and score_code is null)::int missing_representation,
 count(*) filter(where score_code is not null)::int invalid_score_code,
 count(*) filter(where raw_score_value in ('A','0','0.0','77','87','89','77.0','87.0','89.0'))::int invalid_raw_values_present
 from public.assessment_scores""",
"attendance_validity":"""select
 count(*) filter(where day_of_month<1 or day_of_month>31)::int invalid_day,
 count(*) filter(where btrim(raw_status_code)='')::int blank_raw_status,
 count(*) filter(where normalized_status_code<>btrim(raw_status_code))::int unsafe_normalization
 from public.attendance_days""",
"duplicate_candidates":"""select
 (select count(*) from public.student_assessments where duplicate_candidate)::int assessment_dup_members,
 (select count(*) from public.attendance_months where duplicate_candidate)::int attendance_dup_members,
 (select count(*) from (select student_id,academic_year_id,grade_subject_id,assessment_period_id from public.student_assessments group by 1,2,3,4 having count(*)>1)x)::int assessment_dup_groups,
 (select count(*) from (select student_id,academic_year_id,grade_id,month_number from public.attendance_months group by 1,2,3,4 having count(*)>1)x)::int attendance_dup_groups""",
"duplicate_source_locations":"""select 'students' table_name,count(*)::int duplicate_source_keys from (select source_file_id,source_sheet_name,source_row_number,count(*) from public.students group by 1,2,3 having count(*)>1)x
 union all select 'student_grade_enrollments',count(*)::int from (select source_file_id,source_sheet_name,source_row_number,source_column_name,count(*) from public.student_grade_enrollments group by 1,2,3,4 having count(*)>1)x
 union all select 'student_assessments',count(*)::int from (select source_file_id,source_sheet_name,source_row_number,count(*) from public.student_assessments group by 1,2,3 having count(*)>1)x
 union all select 'assessment_scores',count(*)::int from (select source_file_id,source_sheet_name,source_row_number,source_column_name,count(*) from public.assessment_scores group by 1,2,3,4 having count(*)>1)x
 union all select 'attendance_months',count(*)::int from (select source_file_id,source_sheet_name,source_row_number,count(*) from public.attendance_months group by 1,2,3 having count(*)>1)x
 union all select 'attendance_days',count(*)::int from (select source_file_id,source_sheet_name,source_row_number,source_column_name,count(*) from public.attendance_days group by 1,2,3,4 having count(*)>1)x
 union all select 'student_measurements',count(*)::int from (select source_file_id,source_sheet_name,source_row_number,count(*) from public.student_measurements group by 1,2,3 having count(*)>1)x""",
"business_rules":"""select
 (select count(*) from public.assessment_score_codes where score_code='A')::int score_a_codes,
 (select count(*) from public.attendance_status_codes where status_code='P' and meaning='Present')::int present_meaning_ok,
 (select count(*) from public.attendance_status_codes where status_code='A' and meaning='Absent')::int absent_meaning_ok,
 (select count(*) from public.attendance_status_codes where status_code='H' and meaning='Holiday')::int holiday_meaning_ok,
 (select count(*) from public.attendance_status_codes where status_code='NA' and meaning='Not Applicable')::int na_meaning_ok,
 (select count(*) from public.attendance_status_codes where status_code='N' and meaning is null)::int n_still_unresolved,
 (select count(*) from public.student_grade_enrollments where grade_id is null and source_grade_label in ('A. LKG','B. UKG'))::int unresolved_mapped_grade_rows,
 (select count(*) from public.student_grade_enrollments where grade_id is null)::int all_null_grade_rows"""
}

def main():
    p=argparse.ArgumentParser(description="Validate Stage E sources against an existing database without writes.")
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--manifest",type=Path,default=Path(__file__).with_name("source_manifest.json"))
    a=p.parse_args(); data=parse_sources(a.source_dir,a.manifest); expected=expected_counts(data)
    db=os.environ.get("SUPABASE_DB_URL")
    if not db: raise SystemExit("SUPABASE_DB_URL is required")
    import psycopg
    from psycopg.rows import dict_row
    out={"expected_counts":expected,"checks":{},"count_mismatches":{}}
    with psycopg.connect(db,row_factory=dict_row) as conn, conn.cursor() as cur:
        cur.execute("select drive_file_id,file_name from public.source_files")
        live_files={r["drive_file_id"]:r["file_name"] for r in cur.fetchall()}
        manifest_files={w["drive_file_id"]:w.get("source_file_name",Path(w["filename"]).stem) for w in data.manifest["workbooks"]}
        out["source_file_registry_match"]=live_files==manifest_files
        for table,n in expected.items():
            cur.execute(f"select count(*)::int n from public.{table}"); actual=cur.fetchone()["n"]
            if actual!=n: out["count_mismatches"][table]={"expected":n,"actual":actual}
        for name,sql in CHECK_SQL.items():
            cur.execute(sql); out["checks"][name]=[dict(r) for r in cur.fetchall()]
    failures=[]
    if not out["source_file_registry_match"]: failures.append("source-file registry mismatch")
    if out["count_mismatches"]: failures.append("source/database count mismatch")
    if out["checks"]["provenance_missing"]: failures.append("missing provenance")
    if any(out["checks"]["orphans"][0].values()): failures.append("orphan foreign keys")
    if any(out["checks"]["assessment_validity"][0].values()): failures.append("invalid assessment representation")
    if any(out["checks"]["attendance_validity"][0].values()): failures.append("invalid attendance representation")
    if any(r["duplicate_source_keys"] for r in out["checks"]["duplicate_source_locations"]): failures.append("duplicate source locations")
    d=out["checks"]["duplicate_candidates"][0]; totals=data.summary["_totals"]
    if d["assessment_dup_members"]!=totals["assessment_duplicate_members"] or d["assessment_dup_groups"]!=totals["assessment_duplicate_groups"]:
        failures.append("assessment duplicate_candidate mismatch")
    if d["attendance_dup_members"]!=totals["attendance_duplicate_members"] or d["attendance_dup_groups"]!=totals["attendance_duplicate_groups"]:
        failures.append("attendance duplicate_candidate mismatch")
    b=out["checks"]["business_rules"][0]
    if (
        b["score_a_codes"]!=0
        or b["present_meaning_ok"]!=1
        or b["absent_meaning_ok"]!=1
        or b["holiday_meaning_ok"]!=1
        or b["na_meaning_ok"]!=1
        or b["n_still_unresolved"]!=1
        or b["unresolved_mapped_grade_rows"]!=0
        or b["all_null_grade_rows"]!=0
    ):
        failures.append("PM-approved business-rule contract mismatch")
    out["status"]="PASS" if not failures else "FAIL"; out["failures"]=failures
    print(json.dumps(out,indent=2,default=str)); raise SystemExit(0 if not failures else 1)
if __name__=="__main__": main()
