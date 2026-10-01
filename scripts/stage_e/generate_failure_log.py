#!/usr/bin/env python3
from pathlib import Path
import argparse, json
from stage_e_common import parse_sources, write_failure_log, expected_counts

def main():
    p=argparse.ArgumentParser(description="Generate the KC2 Stage E migration failure log without writing to Supabase.")
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--manifest",type=Path,default=Path(__file__).with_name("source_manifest.json"))
    p.add_argument("--output",type=Path,default=Path("artifacts/KC2_Stage_E_Migration_Failure_Log.xlsx"))
    p.add_argument("--audit-json",type=Path)
    a=p.parse_args(); data=parse_sources(a.source_dir,a.manifest); write_failure_log(data,a.output)
    if a.audit_json:
        a.audit_json.parent.mkdir(parents=True,exist_ok=True)
        a.audit_json.write_text(json.dumps({"counts":expected_counts(data),"summary":data.summary},indent=2,default=str),encoding="utf-8")
    print(json.dumps({"counts":expected_counts(data),"summary":data.summary,"failure_log":str(a.output)},indent=2,default=str))
if __name__=="__main__": main()
