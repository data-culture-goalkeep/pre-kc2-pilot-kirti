# Frontend rebuild cohort integration (2026-10-21)

Branch: feature/148-cohort-frontend-readiness

Students & Attendance now uses authenticated RPC calls `public.kc2_rebuild_students()` and `public.kc2_rebuild_attendance(student_id, month)` instead of the old public.student tables.

Both database functions are installed in project tyhwkudogenugnnfgxav. Verified: authenticated EXECUTE = true, anon EXECUTE = false, and SECURITY DEFINER = true. Functions also verify auth.uid() before returning rows. Browser roles still cannot directly read staging tables.

The list surfaces the final cohort of 148 staged student IDs; student ID is used as visible label where names remain missing. Grade is the raw profile label. Attendance percent is computed only from staged P/A days of the latest staged month, excludes H, and is provisional. Empty months are labelled as unavailable. Assessment-count is a raw staged-cell count, not a verified learning metric.

The My Work, Assessments and Programme Insights static example metrics remain prototypes and are labelled as illustrative, not calculated from staging.

Not yet done: browser sign-in E2E, deployment, complete source import, reconciliation of unlinked VI STD rows, frontend production promotion. The original 17 public application tables were NOT deleted, and the old frontend deployment was NOT modified.
