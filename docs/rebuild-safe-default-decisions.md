# Rebuild execution decisions: safe defaults

Date: 2026-10-20
Status: design-only. No production migration applied.

Confirmed existing project: Kirti Pilot KC (Supabase project tyhwkudogenugnnfgxav), ACTIVE_HEALTHY. No development branches currently exist. Recoverable backup or restore point has NOT been verified.

## Adopted import defaults
- Profile student IDs: use the 148 unique IDs in the final Student Profile Sheet as the target active cohort. All 148 IDs are present in the old database.
- Excluded 40 legacy IDs: SCH-26-0001 through SCH-26-0040. Do not migrate them into the *active* cohort; preserve their related historical records and source provenance in an independently verified backup/archive.
- VI STD: keep source score records unlinked in an import-exception queue until independent student identities can be confirmed. Never assign based on spreadsheet row order.
- UKG: preserve the original SHC/SCH spelling and spacing as source evidence. Suggest candidate normalized IDs for reviewer approval only.
- LKG: keep distinct source row and assessment-period keys even when student IDs repeat.
- BMI: preserve all source rows and month-specific measurements. Do not discard repeated IDs: compare same-student same-month measurements and flag conflicts.
- Attendance: consolidate overlapping workbooks using an explicit source precedence/record conflict rule that remains pending; blanks, holidays, presents and absences stay distinguishable. Student rows without confirmed IDs stay unmatched.
- Score values: preserve raw values and missing/absence notation until approved numeric/scoring semantics have been confirmed.
- Sensitive profile attributes: restricted by reviewed row- and column-level access, never published in frontend assets.

## Readiness gates
1. Finish detailed tab-specific field maps and all source-level row reconciliation counts.
2. Resolve or explicitly quarantine unmatched VI STD, UKG, BMI and attendance records.
3. Create replacement schema/migrations and deterministic import scripts on a GitHub branch; avoid any database mutation.
4. Verify an actual restorable backup including existing historical student and auth-related information, not just a spreadsheet export.
5. Test backup restore and revised import in a safely isolated environment (separate branch or database); no branch currently exists.
6. Validate foreign keys, row counts, source provenance, RLS policy restrictions, app query compatibility and rollback plan.
7. Obtain explicit approval for destructive cutover with an itemized change list.

These constraints intentionally override the earlier suggestion to delete the live 17-table database immediately. No real records have been deleted or modified.
