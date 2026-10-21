# March attendance import checkpoint

Source: final consolidated School Attendance 2025-2026 workbook.
Sheet section: March-2026 (first worksheet-like section returned by Drive).
Inspection only.

120 rows contain syntactically valid SCH-style IDs and 31 day-status columns.
Raw statuses across those rows: P=1841, A=799, H=1080.
Total inspected daily status cells: 3720.

The attempted bulk staging import was blocked by tool safety controls, so it was not executed.
A fresh database SELECT verified:
- staging attendance_entries = 0
- staging students = 148
- staging measurement_entries = 502
- staging import_batches = 2

Do not treat the 120 IDs as confirmed in the final cohort until rechecked.
The 3720 daily cells are source observations only; overlap with monthly attendance workbooks is unresolved.
Preserve holidays explicitly; do not represent H as absence.
Next steps: approved, auditable importer; cohort inclusion check; source provenance per cell; reconciliation of overlapping month records; read-only checks before cutover.
