-- PROPOSAL ONLY. DO NOT EXECUTE AGAINST PRODUCTION.
-- Isolated v2 staging schema; no DROP, UPDATE or ALTER of current Phase 1 data.
-- Application clients receive no privileges on this schema.
begin;
create schema if not exists kc2_rebuild;
revoke all on schema kc2_rebuild from public, anon, authenticated;
create table kc2_rebuild.import_batches (
 batch_id bigint generated always as identity primary key,
 source_drive_file_id text not null,
 source_file_name text not null,
 imported_at timestamptz not null default now(),
 file_digest text,
 import_status text not null default 'draft'
   check (import_status in ('draft','validated','rejected'))
);
create table kc2_rebuild.import_cells (
 cell_id bigint generated always as identity primary key,
 batch_id bigint not null references kc2_rebuild.import_batches(batch_id),
 sheet_name text not null,
 source_row integer not null check (source_row > 0),
 source_column text not null,
 raw_value text,
 unique(batch_id,sheet_name,source_row,source_column)
);
create table kc2_rebuild.students (
 student_id text primary key,
 original_name text,
 english_name text,
 birth_date date,
 gender_raw text,
 grade_label_raw text,
 profile_remark_raw text,
 batch_id bigint not null references kc2_rebuild.import_batches(batch_id),
 source_sheet text not null,
 source_row integer not null,
 unique(batch_id,source_sheet,source_row)
);
create table kc2_rebuild.student_private_attributes (
 student_id text primary key references kc2_rebuild.students(student_id),
 community_raw text,
 caste_raw text
);
create table kc2_rebuild.assessment_entries (
 entry_id bigint generated always as identity primary key,
 batch_id bigint not null references kc2_rebuild.import_batches(batch_id),
 sheet_name text not null,
 source_row integer not null check(source_row > 0),
 source_column text not null,
 student_id text references kc2_rebuild.students(student_id),
 grade_label_raw text,
 term_raw text,
 subject_raw text,
 competency_raw text,
 activity_raw text,
 score_raw text,
 resolution_status text not null default 'pending'
   check(resolution_status in ('pending','matched','excluded','conflict')),
 unique(batch_id,sheet_name,source_row,source_column),
 check (resolution_status <> 'matched' or student_id is not null)
);
create table kc2_rebuild.attendance_entries (
 entry_id bigint generated always as identity primary key,
 batch_id bigint not null references kc2_rebuild.import_batches(batch_id),
 sheet_name text not null,
 source_row integer not null check(source_row > 0),
 source_column text not null,
 student_id text references kc2_rebuild.students(student_id),
 calendar_date date,
 grade_label_raw text,
 status_raw text,
 resolution_status text not null default 'pending'
   check(resolution_status in ('pending','matched','excluded','conflict')),
 unique(batch_id,sheet_name,source_row,source_column),
 check(resolution_status <> 'matched' or (student_id is not null and calendar_date is not null))
);
create table kc2_rebuild.measurement_entries (
 entry_id bigint generated always as identity primary key,
 batch_id bigint not null references kc2_rebuild.import_batches(batch_id),
 sheet_name text not null,
 source_row integer not null check(source_row > 0),
 source_month smallint check(source_month between 1 and 12),
 source_year integer,
 student_id text references kc2_rebuild.students(student_id),
 weight_raw text,
 height_raw text,
 resolution_status text not null default 'pending'
   check(resolution_status in ('pending','matched','excluded','conflict')),
 unique(batch_id,sheet_name,source_row,source_month),
 check(resolution_status <> 'matched' or student_id is not null)
);
create table kc2_rebuild.import_exceptions (
 exception_id bigint generated always as identity primary key,
 batch_id bigint not null references kc2_rebuild.import_batches(batch_id),
 sheet_name text not null,
 source_row integer,
 source_column text,
 issue_code text not null,
 review_status text not null default 'open'
   check(review_status in ('open','resolved','waived')),
 reviewer_note text,
 created_at timestamptz not null default now()
);
-- Belt and suspenders: no browser roles granted, and RLS denies all by default.
alter table kc2_rebuild.import_batches enable row level security;
alter table kc2_rebuild.import_cells enable row level security;
alter table kc2_rebuild.students enable row level security;
alter table kc2_rebuild.student_private_attributes enable row level security;
alter table kc2_rebuild.assessment_entries enable row level security;
alter table kc2_rebuild.attendance_entries enable row level security;
alter table kc2_rebuild.measurement_entries enable row level security;
alter table kc2_rebuild.import_exceptions enable row level security;
revoke all on all tables in schema kc2_rebuild from public, anon, authenticated;
revoke all on all sequences in schema kc2_rebuild from public, anon, authenticated;
commit;
