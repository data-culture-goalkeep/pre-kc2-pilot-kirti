# Phase 2 four-tab read-only frontend: QA handover

## Deployment
- Vercel team: `goalkeep2`; project: `pre-kc2-pilot-kirti`
- Preview branch: `feature/phase2-my-work-readonly`
- Preview commit: `f87dd2aca30c2a13429823f51f206ff9334b791e`
- Preview URL: https://pre-kc2-pilot-kirti-nzekrcchw-goalkeep2.vercel.app
- Do not merge into production until QA acceptance.

## Implemented
- Students & Attendance: Supabase Auth; read-only student, enrolment, attendance month/day retrieval.
- Assessments & Follow-up: assessment records and activity-score detail are read-only; shows duplicate candidates. Follow-up action entry is not implemented.
- Programme Insights: enrolment, attendance and assessment source-data coverage by year; source-reported attendance percentage is explicitly not a derived attendance KPI.
- My Work: read-only review counts (duplicate candidates, missing reported values), period coverage and navigation; not assigned tasks or deadlines.

## Confirmed / unconfirmed
- Vercel returned READY for the preview build.
- PM reported that the previous Students & Attendance and Assessments views showed live data.
- PM reported completing the latest My Work / Programme Insights check but independent browser-level verification and numeric reconciliation against Supabase have not been performed here.
- All browser modules use a publishable Supabase key, not a service-role key; live access additionally depends on deployed Supabase RLS policies.
- There are no frontend database writes.
- **Important:** browser authentication only hides UI; RLS remains the actual data protection boundary. Independently test unauthenticated queries with a fresh session.
- No tasks/follow-up table exists in the approved 17-table schema; do not imply actual task assignments or resolved follow-ups.

## Kirti / PM QA checklist
1. Signed out, try each tab and verify **no individual-level data** can be retrieved; validate direct Supabase anon access is denied.
2. Sign in as the internal test account (do not share credentials); verify correct user identity and session handling.
3. Compare student list totals, attendance history, assessment-record counts and filtered year totals to authoritative database queries. Check pagination and duplicate candidates.
4. Open activity scores, verify raw A and numeric 0–10 handling **against current approved correction rules and database values**. Do not silently normalize unresolved codes.
5. Test year filters/search, sign-out, expired session and refresh; ensure no historical student data is cached/displayed after logout.
6. Verify Vercel preview protection and Supabase RLS grants for Teacher, PM, Leadership and Admin.
7. Confirm scope, role permissions, schema and audit needs before adding assessment edits, teacher assignments or follow-up actions.
8. Verify mobile layout and keyboard accessibility.

## Acceptance decision
This PR is **draft / review only**. It does not change live Supabase data or schema. No production deployment or automatic merge is authorized.
