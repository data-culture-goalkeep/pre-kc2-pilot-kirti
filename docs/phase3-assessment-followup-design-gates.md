# Phase 3 proposal: assessment entry and follow-up actions

## Decision status
PROPOSED ONLY. No schema migration or RLS change is authorized by this document.

## Verified live database on 2026-10-14
Supabase project: `Kirti Pilot KC` (`tyhwkudogenugnnfgxav`).
The public schema currently contains the 17 approved Phase 1 tables.
`pg_policies` shows SELECT-only policies for `academic_years`, `grades`, `students`, `student_grade_enrollments`, `attendance_months`, `attendance_days`, `attendance_status_codes`, applying to the broad `authenticated` role.
There are **no authenticated SELECT policies for the assessment tables** and no INSERT/UPDATE policies for these records. No follow-up action table exists in the approved schema.

## Security gate
Before enabling assessment view/editing:
- Review access for `student_assessments`, `assessment_scores`, `grade_subjects`, `subjects`, `assessment_periods`, `assessment_competencies`, `assessment_activities`.
- Define role mapping Teacher, PM, Leadership, separate Admin, including row scope, permitted operations, and audit trail.
- Require server-enforced authorization/RLS: button hiding in the browser is not sufficient.
- Authorize the specific forward migration in a reviewed PR; do not change live policies as part of initial frontend development.
- Test anonymous and unauthorized users against the API, in addition to browser E2E.
- Resolve score semantics from the **current approved correction rules and live schema**. Avoid silently reinterpreting A, 0 or N. Define immutable source scores versus editable entered scores and how to avoid corrupting imports.

## Assessment entry proposal
- Select student, academic year, grade/subject, period, competency and activity from existing approved relations.
- Show the source record and prior scores before any edit.
- Validate input in browser and database according to approved policy.
- Prevent duplicate assessment candidate overwrite. Duplicate candidates require explicit manual review.
- Record who entered/changed the score and when; preserve prior values and import lineage.
- Separate drafts from submitted entries, and enforce role-specific update permissions.

## Follow-up action proposal (not yet in schema)
Proposed new audited entity, SUBJECT TO PM APPROVAL:
- student reference; originating attendance/assessment record when available
- issue/need category and notes
- assigned user/role, action status, due date, completed date
- created_by/updated_by and timestamps
- audit history and explicit RLS

Approval needed for exact fields, relationships, workflow status vocabulary, responsibility assignment rules, retention and role access.

## QA/release plan
1. Approve data model and permission matrix.
2. Write forward migrations in a review branch, test against a non-production Supabase environment.
3. Implement authenticated UI and server-enforced data writes.
4. Verify audit, duplicate protections, 1..N role coverage, validation and race conditions.
5. Reconcile test records, check anonymous denial, obtain PM sign-off.
6. Only then deploy to production.

## Current blocker
The integrated four-tab preview cannot be considered fully validated until assessment SELECT and role security are reviewed. Earlier browser-level positive reports and successful Vercel builds are insufficient evidence of assessment permissions.
