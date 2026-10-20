# Import exception decisions — verified source inspection

Status: analysis / review. No production database writes.

## VI STD grade tab
The VI STD grade tab has header rows 1-4 (Term, Subject, Skill or Concept, Activity), and 18 populated score rows 5-22. Column A is blank for these student rows in the inspected range. There is no defensible ID mapping from this tab alone: do not assign scores by row number, assumed roster order or names. Keep these assessment rows on an unmatched-student exception list pending an authoritative roster.

## UKG grade IDs
The grade tab includes mixed SCH and SHC prefixes and inconsistent spaces. Preserve original text; propose candidate canonical IDs only when an existing student ID matches after documented typo normalization and an independent grade/roster check. Do not silently rewrite.

## BMI 2026 duplicate ID occurrences
- SCH-25-0007: rows 18 and 55. One row has early-month measurements; the other has no values in the first three monthly pairs. Inspect all twelve months before choosing precedence.
- SCH-22-0001: rows 46 and 59; both contain early-month measurement values.
- SCH-21-0009: rows 40 and 71; both contain early-month measurement values.

Three repeated ID occurrences across 98 identified rows (95 distinct IDs). This is not proof that measurements duplicate; require monthly cell-level comparison and conflict resolution.

## Source cohort
148 unique student IDs, all matching current database. Forty existing IDs not in final profile are SCH-26-0001 through SCH-26-0040. Preserve full historical records in restorable backup before any production cutover.

## Attendance rules for proposed importer
- Consolidated workbook and standalone monthly workbooks can contain the same student-month; define an approved priority rule or cell-level reconciliation, with source references retained.
- Blank student ID does not authorize a guessed match based on a similarly spelled name.
- Keep raw P / A / H / long holiday text / blank distinct until business mapping is signed off.
- Validate reported total, present and absent counts, without overwriting source values or assuming every calendar day is a school day.

## Stop conditions before import
Unresolved student ID on assessment row; conflicting BMI measurements for same student/month; overlapping attendance with differing statuses; unverifiable student identity; missing recoverable backup; inadequate authenticated RLS.

No live tables, policies or student records have been altered.
