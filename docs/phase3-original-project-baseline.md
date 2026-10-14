# Production baseline and controlled test gates — 2026-10-14

Scope: **read-only inspection** of the existing `Kirti Pilot KC` Supabase project (`tyhwkudogenugnnfgxav`). These findings were obtained using SELECT queries. No records, roles, tables or policies were modified.

## Actual counts
| Metric | Live count |
| --- | ---: |
| Students | 188 |
| Student grade enrolments | 317 |
| Student assessment records | 3,453 |
| Individual assessment scores | 47,387 |
| Attendance month records | 1,882 |
| Attendance day records | 46,763 |
| Assessment duplicate candidates | 100 |
| Attendance duplicate candidates | 8 |
| Missing reported assessment averages | 54 |
| Missing reported attendance percentages | 185 |

## RLS inspection
All 17 Phase 1 public tables have RLS enabled.

Exactly seven currently expose a `SELECT` policy to the broad `authenticated` role:
`academic_years`, `grades`, `students`, `student_grade_enrollments`, `attendance_months`, `attendance_days`, `attendance_status_codes`.

The other ten tables have **no policies**. In particular `student_assessments`, `assessment_scores`, `grade_subjects`, `subjects`, `assessment_periods`, `assessment_activities`, and `assessment_competencies` have no authenticated SELECT policy. No write policy exists.

**Impact:** The authenticated Assessment page may render while returning no accessible assessment records. Claims that the assessment frontend shows real records must be revalidated after an approved, role-scoped read policy is implemented. The broader `authenticated` policy on student PII must also be reviewed for least-privilege access.

## Testing original project safely
Permitted now:
- Metadata and non-identifying aggregate SELECT checks
- Query-based reconciliation of displayed summary totals
- Role and policy inspection without altering policies
- Non-mutating review of the proposed migration source

Blocked pending explicit change approval:
- Running the Phase 3 draft migration against production
- Writing synthetic test data into imported source tables
- Opening access to assessment tables through broad RLS policies
- Adding test Auth users with elevated privileges
- Disabling RLS or bypassing RLS using an exposed service key

## Proposed deployment sequence after authorization
1. Agree on staff-to-student access scope, teacher/PM/leadership/admin permissions, retention, scoring rules and follow-up fields.
2. Create and document a recoverable database backup / point-in-time restore option suitable for the project's plan. An SQL transaction rollback protects only the migration transaction; it is not a substitute for backups or a way to undo subsequent user writes.
3. Review additive DDL in `supabase/proposals/20261014_phase3_workflow_draft.sql`. Fix any agreed semantics before moving it into the applied migrations folder.
4. Apply the minimal isolated schema change during an approved maintenance window, verify that imported record totals are unchanged, that new RLS tables deny access by default, and that no frontend write path is enabled.
5. Implement server-enforced role-scoped permissions and transactional audit trail in a **separate** reviewed change. Test with isolated synthetic test accounts and rows; clean up using documented identifiers.
6. Reconcile programme dashboards, assessment details, sign-out access and all role/negative tests before any production rollout.

## Acceptance blocker
Permission design, audit implementation and explicit production migration approval have not yet been established. This document is the baseline, **not proof of complete browser E2E or authorization tests**.
