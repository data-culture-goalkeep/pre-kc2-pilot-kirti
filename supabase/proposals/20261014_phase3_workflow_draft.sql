-- PROPOSAL ONLY: Phase 3 additive schema, apply to an isolated test database first.
-- Do not apply to Kirti Pilot KC production without PM/Kirti sign-off.
-- No modifications to the 17 imported Phase 1 tables or their source values.
begin;

create table public.pilot_staff_roles (
  user_id uuid primary key references auth.users(id),
  pilot_role text not null check (pilot_role in ('teacher','pm','leadership','admin')),
  assigned_at timestamptz not null default now()
);

create table public.followup_actions (
  followup_action_id bigint generated always as identity primary key,
  student_id text not null references public.students(student_id),
  originating_assessment_id bigint references public.student_assessments(student_assessment_id),
  originating_attendance_month_id bigint references public.attendance_months(attendance_month_id),
  need_category text not null check (btrim(need_category) <> ''),
  action_notes text not null check (btrim(action_notes) <> ''),
  assigned_to uuid references auth.users(id),
  action_status text not null check (action_status in ('open','in_progress','completed','cancelled')),
  due_date date,
  completed_at timestamptz,
  created_by uuid not null references auth.users(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint followup_completion_check check (
    (action_status = 'completed' and completed_at is not null)
    or (action_status <> 'completed' and completed_at is null)
  )
);

-- Separate new entries from imported assessment_scores. Do not overwrite source lineage.
create table public.assessment_entry_drafts (
  assessment_entry_draft_id bigint generated always as identity primary key,
  student_id text not null references public.students(student_id),
  academic_year_id bigint not null references public.academic_years(academic_year_id),
  grade_subject_id bigint not null references public.grade_subjects(grade_subject_id),
  assessment_period_id bigint not null references public.assessment_periods(assessment_period_id),
  activity_id bigint not null references public.assessment_activities(activity_id),
  raw_score_value text not null,
  entry_notes text,
  created_by uuid not null references auth.users(id),
  created_at timestamptz not null default now(),
  -- Drafts are intentionally not published into imported assessment tables.
  workflow_status text not null default 'draft' check (workflow_status = 'draft'),
  constraint draft_score_preliminary_check check (raw_score_value ~ '^(10|[0-9]|A)$')
);

-- Append-only event log; changes will require a reviewed server-side write path.
create table public.pilot_action_events (
  event_id bigint generated always as identity primary key,
  entity_type text not null check (entity_type in ('followup_action','assessment_draft')),
  entity_id bigint not null,
  event_type text not null,
  event_payload jsonb not null default '{}'::jsonb,
  actor_id uuid not null references auth.users(id),
  created_at timestamptz not null default now()
);

create index followup_actions_student_idx on public.followup_actions(student_id);
create index followup_actions_assignee_idx on public.followup_actions(assigned_to);
create index assessment_entry_drafts_student_idx on public.assessment_entry_drafts(student_id);
create index pilot_action_events_entity_idx on public.pilot_action_events(entity_type,entity_id);

alter table public.pilot_staff_roles enable row level security;
alter table public.followup_actions enable row level security;
alter table public.assessment_entry_drafts enable row level security;
alter table public.pilot_action_events enable row level security;

-- Deliberately no browser-accessible policies yet. Even signed-in users are denied.
-- Follow-on approval must define per-student teacher scope, reviewer access,
-- database-enforced audit events, and source score semantics before write policies.
commit;
