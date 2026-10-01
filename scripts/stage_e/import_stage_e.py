#!/usr/bin/env python3
"""Idempotent KC2 Stage E importer. Dry-run by default; --apply performs writes."""
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from stage_e_common import CANONICAL_GRADES, expected_counts, parse_sources, write_failure_log

PERIOD_ORDER={"Baseline":0,"Term 1":1,"Term 2":2,"Term 3":3}

def q1(cur,sql,params=()):
    cur.execute(sql,params); return cur.fetchone()

def upsert(cur,table,values,conflict,ret):
    cols=list(values); keys={x.strip() for x in conflict.split(",")}
    sets=",".join(f"{c}=excluded.{c}" for c in cols if c not in keys)
    cur.execute(f"insert into public.{table} ({','.join(cols)}) values ({','.join(['%s']*len(cols))}) on conflict ({conflict}) do update set {sets} returning {ret}",[values[c] for c in cols])
    return cur.fetchone()[ret]

def source_row_id(cur,table,id_col,sfid,sheet,row):
    rec=q1(cur,f"select {id_col} from public.{table} where source_file_id=%s and source_sheet_name=%s and source_row_number=%s order by {id_col} limit 1",(sfid,sheet,row))
    return rec[id_col] if rec else None

def assert_schema(cur):
    expected={"source_files","academic_years","grades","subjects","assessment_periods","assessment_score_codes","attendance_status_codes","students","student_grade_enrollments","grade_subjects","assessment_competencies","assessment_activities","student_assessments","assessment_scores","attendance_months","attendance_days","student_measurements"}
    cur.execute("select table_name from information_schema.tables where table_schema='public' and table_type='BASE TABLE'")
    found={r["table_name"] for r in cur.fetchall()}
    missing=sorted(expected-found)
    if missing: raise RuntimeError(f"Approved Stage C schema is missing tables: {missing}")

def apply_data(conn,data):
    from psycopg.rows import dict_row
    with conn.cursor(row_factory=dict_row) as cur:
        assert_schema(cur); source_ids={}
        for w in data.source_files:
            source_ids[w["label"]]=upsert(cur,"source_files",{"drive_file_id":w["drive_file_id"],"file_name":w.get("source_file_name",Path(w["filename"]).stem),"file_type":"google_sheet"},"drive_file_id","source_file_id")
        def prov(r): return {"source_file_id":source_ids[r["source_label"]],"source_sheet_name":r["sheet"],"source_row_number":r["row"]}

        year_ids={}
        for year,r in sorted(data.academic_years.items()):
            year_ids[year]=upsert(cur,"academic_years",{"year_label":year,**prov(r)},"year_label","academic_year_id")
        grade_ids={}
        for grade in CANONICAL_GRADES:
            r=data.grades[grade]
            grade_ids[grade]=upsert(cur,"grades",{"grade_code":grade,"grade_name":grade,"sort_order":r["sort_order"],**prov(r)},"grade_code","grade_id")
        subject_ids={}
        for subject,r in sorted(data.subjects.items()):
            subject_ids[subject]=upsert(cur,"subjects",{"subject_name":subject,**prov(r)},"subject_name","subject_id")
        period_ids={}
        for period,r in sorted(data.periods.items(),key=lambda x:PERIOD_ORDER[x[0]]):
            period_ids[period]=upsert(cur,"assessment_periods",{"period_code":period,"source_label":period,"sort_order":PERIOD_ORDER[period],**prov(r)},"period_code","assessment_period_id")
        for code,r in data.score_codes.items():
            upsert(cur,"assessment_score_codes",{"score_code":code,"meaning":None,**prov(r)},"score_code","score_code")
        for code,r in sorted(data.attendance_codes.items()):
            upsert(cur,"attendance_status_codes",{"status_code":code,"meaning":None,**prov(r)},"status_code","status_code")

        for s in data.students:
            upsert(cur,"students",{"student_id":s["student_id"],"student_name":s["student_name"],"source_enrollment_year_label":s["source_enrollment_year_label"],"gender":s["gender"],"date_of_birth":s["date_of_birth"],"social_category":s["social_category"],"program_type":s["program_type"],**prov(s)},"student_id","student_id")
        for e in data.enrollments:
            upsert(cur,"student_grade_enrollments",{"student_id":e["student_id"],"academic_year_id":year_ids[e["academic_year"]],"grade_id":grade_ids[e["grade"]] if e["grade"] else None,"source_grade_label":e["source_grade_label"],**prov(e),"source_column_name":e["column"]},"student_id,academic_year_id","student_grade_enrollment_id")

        gs_ids={}
        for g in data.grade_subjects:
            key=(g["grade"],g["subject"])
            gs_ids[key]=upsert(cur,"grade_subjects",{"grade_id":grade_ids[g["grade"]],"subject_id":subject_ids[g["subject"]],**prov(g)},"grade_id,subject_id","grade_subject_id")
        comp_ids={}
        for c in data.competencies:
            gid=gs_ids[(c["grade"],c["subject"])]
            cid=upsert(cur,"assessment_competencies",{"grade_subject_id":gid,"competency_order":c["competency_order"],"competency_name":c["competency_name"],**prov(c)},"grade_subject_id,competency_order","competency_id")
            comp_ids[(c["grade"],c["subject"],c["competency_order"])]=cid
        activity_ids={}
        for a in data.activities:
            cid=comp_ids[(a["grade"],a["subject"],a["competency_order"])]
            aid=upsert(cur,"assessment_activities",{"competency_id":cid,"activity_order":a["activity_order"],"activity_name":a["activity_name"],"is_placeholder":a["is_placeholder"],**prov(a),"source_column_name":a["column"]},"competency_id,activity_order","activity_id")
            activity_ids[(a["grade"],a["subject"],a["competency_order"],a["activity_order"])]=aid

        assessment_ids={}
        for a in data.assessments:
            sfid=source_ids[a["source_label"]]; aid=source_row_id(cur,"student_assessments","student_assessment_id",sfid,a["sheet"],a["row"])
            vals={"student_id":a["student_id"],"academic_year_id":year_ids[a["academic_year"]],"grade_subject_id":gs_ids[(a["grade"],a["subject"])],"assessment_period_id":period_ids[a["period"]],"reported_average_score":a["reported_average_score"],"duplicate_candidate":a["duplicate_candidate"],**prov(a)}
            if aid is None:
                cols=list(vals); cur.execute(f"insert into public.student_assessments ({','.join(cols)}) values ({','.join(['%s']*len(cols))}) returning student_assessment_id",[vals[c] for c in cols]); aid=cur.fetchone()["student_assessment_id"]
            else:
                cur.execute("update public.student_assessments set student_id=%s,academic_year_id=%s,grade_subject_id=%s,assessment_period_id=%s,reported_average_score=%s,duplicate_candidate=%s where student_assessment_id=%s",(vals["student_id"],vals["academic_year_id"],vals["grade_subject_id"],vals["assessment_period_id"],vals["reported_average_score"],vals["duplicate_candidate"],aid))
            assessment_ids[(a["source_label"],a["sheet"],a["row"])]=aid
        for s in data.scores:
            ass_id=assessment_ids[(s["assessment_source_label"],s["assessment_sheet"],s["assessment_row"])]
            act_id=activity_ids[(s["grade"],s["subject"],s["competency_order"],s["activity_order"])]
            upsert(cur,"assessment_scores",{"student_assessment_id":ass_id,"activity_id":act_id,"raw_score_value":s["raw_score_value"],"numeric_score":s["numeric_score"],"score_code":s["score_code"],**prov(s),"source_column_name":s["column"]},"student_assessment_id,activity_id","assessment_score_id")

        attendance_ids={}
        for a in data.attendance_months:
            sfid=source_ids[a["source_label"]]; mid=source_row_id(cur,"attendance_months","attendance_month_id",sfid,a["sheet"],a["row"])
            vals={"student_id":a["student_id"],"academic_year_id":year_ids[a["academic_year"]],"grade_id":grade_ids[a["grade"]],"month_number":a["month_number"],"source_month_label":a["source_month_label"],"reported_days_present":a["reported_days_present"],"reported_days_absent":a["reported_days_absent"],"reported_attendance_percentage":a["reported_attendance_percentage"],"duplicate_candidate":a["duplicate_candidate"],**prov(a)}
            if mid is None:
                cols=list(vals); cur.execute(f"insert into public.attendance_months ({','.join(cols)}) values ({','.join(['%s']*len(cols))}) returning attendance_month_id",[vals[c] for c in cols]); mid=cur.fetchone()["attendance_month_id"]
            else:
                cur.execute("update public.attendance_months set student_id=%s,academic_year_id=%s,grade_id=%s,month_number=%s,source_month_label=%s,reported_days_present=%s,reported_days_absent=%s,reported_attendance_percentage=%s,duplicate_candidate=%s where attendance_month_id=%s",(vals["student_id"],vals["academic_year_id"],vals["grade_id"],vals["month_number"],vals["source_month_label"],vals["reported_days_present"],vals["reported_days_absent"],vals["reported_attendance_percentage"],vals["duplicate_candidate"],mid))
            attendance_ids[(a["source_label"],a["sheet"],a["row"])]=mid
        for d in data.attendance_days:
            mid=attendance_ids[(d["parent_source_label"],d["parent_sheet"],d["parent_row"])]
            upsert(cur,"attendance_days",{"attendance_month_id":mid,"day_of_month":d["day_of_month"],"raw_status_code":d["raw_status_code"],"normalized_status_code":d["normalized_status_code"],**prov(d),"source_column_name":d["column"]},"attendance_month_id,day_of_month","attendance_day_id")
        for m in data.measurements:
            mid=attendance_ids[(m["parent_source_label"],m["parent_sheet"],m["parent_row"])]
            upsert(cur,"student_measurements",{"attendance_month_id":mid,"age_years":m["age_years"],"height_cm":m["height_cm"],"weight_kg":m["weight_kg"],"reported_bmi_value":m["reported_bmi_value"],"reported_bmi_category":m["reported_bmi_category"],**prov(m)},"attendance_month_id","student_measurement_id")

        ids=list(source_ids.values())
        cur.execute("""update public.student_assessments sa set duplicate_candidate=exists(
          select 1 from public.student_assessments x where x.source_file_id=any(%s) and x.student_assessment_id<>sa.student_assessment_id
          and x.student_id=sa.student_id and x.academic_year_id=sa.academic_year_id and x.grade_subject_id=sa.grade_subject_id and x.assessment_period_id=sa.assessment_period_id)
          where sa.source_file_id=any(%s)""",(ids,ids))
        cur.execute("""update public.attendance_months am set duplicate_candidate=exists(
          select 1 from public.attendance_months x where x.source_file_id=any(%s) and x.attendance_month_id<>am.attendance_month_id
          and x.student_id=am.student_id and x.academic_year_id=am.academic_year_id and x.grade_id=am.grade_id and x.month_number=am.month_number)
          where am.source_file_id=any(%s)""",(ids,ids))

def main():
    p=argparse.ArgumentParser(description="Parse and optionally reconcile the sanitized KC2 Stage E workbooks.")
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--manifest",type=Path,default=Path(__file__).with_name("source_manifest.json"))
    p.add_argument("--failure-log",type=Path,default=Path("artifacts/KC2_Stage_E_Migration_Failure_Log.xlsx"))
    p.add_argument("--apply",action="store_true",help="Reconcile into the approved schema. Default is no-write dry-run.")
    a=p.parse_args(); data=parse_sources(a.source_dir,a.manifest); write_failure_log(data,a.failure_log)
    report={"mode":"apply" if a.apply else "dry-run","counts":expected_counts(data),"summary":data.summary,"failure_log":str(a.failure_log)}
    if not a.apply:
        print(json.dumps(report,indent=2,default=str)); return
    db=os.environ.get("SUPABASE_DB_URL")
    if not db: raise SystemExit("SUPABASE_DB_URL is required with --apply")
    import psycopg
    from psycopg.rows import dict_row
    with psycopg.connect(db,row_factory=dict_row) as conn:
        with conn.transaction(): apply_data(conn,data)
    print(json.dumps(report,indent=2,default=str))
if __name__=="__main__": main()
