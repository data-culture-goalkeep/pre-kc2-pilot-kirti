# Phase 3 database proposal: reviewer checklist

**Status:** un-applied SQL proposal; **not a production migration**.

## Existing environment checked
- Supabase project `Kirti Pilot KC`: `tyhwkudogenugnnfgxav`.
- Approved imported schema has 17 public tables.
- Live RLS has SELECT policies for only seven core student/attendance/reference tables; no assessment SELECT and no write policies were seen.
- No Supabase branch is currently available for this project.
- The other accessible Supabase project belongs to a different pilot and must not be repurposed as a testing database.

## Files
- `supabase/proposals/20261014_phase3_workflow_draft.sql`
- `frontend/phase3-prototype.html`

## Proposed additions
1. `pilot_staff_roles` for an explicit role mapping, with roles teacher, pm, leadership and admin.
2. `followup_actions`, recording originating student/assessment/attendance references, category, notes, assignee, status and key dates.
3. `assessment_entry_drafts`, storing new draft entries separate from imported score/source lineage.
4. `pilot_action_events` for future append-only audit events.

All four proposed tables have RLS enabled and **no access policies**. This is intentional: the migration by itself enables no client reads or writes.

## Reviewer decisions required before implementation
- Who assigns staff roles, and which staff may see which students? Authentication alone is insufficient.
- Whether the draft's field names, required fields and status vocabulary are correct.
- Whether entries are initially draft-only; who may submit, amend, reject or approve entries.
- Reconfirm whether a numeric 0 is accepted and how 'A' contributes to scores and averages before approving the preliminary draft-score constraint.
- Whether follow-ups may have no assigned staff, no due date and/or no originating assessment/attendance record.
- Specify an immutable audit mechanism, transaction boundaries and allowed privileged services.
- Define whether assignment, notes or health-related student fields require narrower access or retention restrictions.
- Decide if views of imported assessment tables can be granted with suitable row scopes.

## Safe test plan
1. Provision **a dedicated non-production Supabase project or sanctioned database branch**. Never point a trial migration at the existing production project.
2. Apply the proposed SQL there and check that all 17 existing tables still exist and source data remains unchanged.
3. Attempt each proposed table with anon and ordinary authenticated accounts: all client reads and writes must be denied at this stage.
4. Confirm FK integrity, required fields, empty values, completed date logic, and allowed role/status values.
5. Approve staff-to-student scoping, then write a separate RLS/transaction/audit implementation and repeat tests with teacher, PM, leadership, admin and unauthorized users.
6. Test score interpretation, audit immutability, duplicate safeguards and role changes.
7. Request explicit production migration approval **after** QA and review.

## Not yet complete
- No actual non-production migration has been executed.
- No role policies, audit triggers, server-side entry endpoint or deployed write interface is implemented.
- Phase 2 authenticated assessment access remains blocked by current RLS and requires separate review.
