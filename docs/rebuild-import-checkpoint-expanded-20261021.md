# Verified staging import checkpoint — 2026-10-21

The isolated kc2_rebuild schema now contains 148 students, 502 raw BMI month entries, 3720 March 2026 attendance day cells, and 1410 assessment score cells. Original public.students remains at 188.

New in this checkpoint:
- Completed all 3720 candidate March day cells from first section of consolidated school attendance workbook.
- Appended 1248 score cells to the prior 162 in staging from eight grade tabs (LKG, UKG, II, III, IV, V, VI and VII).
- VI STD scores: 195 raw cells staged with null student IDs. These must not be published as identified student scores.
- 11 UKG grade rows had unmatched or mistyped raw ID strings; they were not silently linked.
- Only numeric cells in initial columns B:L (per grade tab) were staged in this pass. Remaining columns and other attendance periods need a separate complete import.
- Assessment term/subject/activity columns on new rows are intentionally null pending proper merged-header mapping; do not treat staging as clean analytical data.
- Original 17-table public schema remains unmodified. No deletion, frontend change, or production cutover.

Staging data is partial. The request to delete old tables has not been executed because that would permanently discard data not yet imported. Do not characterize this as the final replacement database.
