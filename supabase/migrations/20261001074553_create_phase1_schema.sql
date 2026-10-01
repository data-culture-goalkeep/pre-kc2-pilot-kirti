-- KC2 Phase 1 schema
-- Approved Stage B model. Schema only; no source data migration.

create table public.source_files (
  source_file_id bigint generated always as identity primary key,
  drive_file_id text not null,
  file_name text not null,
  file_type text not null default 'google_sheet',
  created_at timestamptz not null default now(),
  constraint source_files_drive_file_id_key unique (drive_file_id),
  constraint source_files_file_type_check check (file_type in ('google_sheet'))
);

create table public.academic_years (
  academic_year_id bigint generated always as identity primary key,
  year_label text not null,
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  created_at timestamptz not null default now(),
  constraint academic_years_year_label_key unique (year_label),
  constraint academic_years_source_row_number_check check (source_row_number > 0)
);

create table public.grades (
  grade_id bigint generated always as identity primary key,
  grade_code text not null,
  grade_name text not null,
  sort_order smallint not null,
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  created_at timestamptz not null default now(),
  constraint grades_grade_code_key unique (grade_code),
  constraint grades_grade_name_key unique (grade_name),
  constraint grades_sort_order_key unique (sort_order),
  constraint grades_source_row_number_check check (source_row_number > 0)
);

create table public.subjects (
  subject_id bigint generated always as identity primary key,
  subject_name text not null,
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  created_at timestamptz not null default now(),
  constraint subjects_subject_name_key unique (subject_name),
  constraint subjects_source_row_number_check check (source_row_number > 0)
);

create table public.assessment_periods (
  assessment_period_id bigint generated always as identity primary key,
  period_code text not null,
  source_label text not null,
  sort_order smallint not null,
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  created_at timestamptz not null default now(),
  constraint assessment_periods_period_code_key unique (period_code),
  constraint assessment_periods_source_label_key unique (source_label),
  constraint assessment_periods_source_row_number_check check (source_row_number > 0)
);

create table public.assessment_score_codes (
  score_code text primary key,
  meaning text,
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  created_at timestamptz not null default now(),
  constraint assessment_score_codes_source_row_number_check check (source_row_number > 0)
);

create table public.attendance_status_codes (
  status_code text primary key,
  meaning text,
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  created_at timestamptz not null default now(),
  constraint attendance_status_codes_source_row_number_check check (source_row_number > 0)
);

create table public.students (
  student_id text primary key,
  student_name text not null,
  source_enrollment_year_label text,
  gender text,
  date_of_birth date,
  social_category text,
  program_type text,
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  created_at timestamptz not null default now(),
  constraint students_source_row_number_check check (source_row_number > 0)
);

create table public.student_grade_enrollments (
  student_grade_enrollment_id bigint generated always as identity primary key,
  student_id text not null references public.students(student_id),
  academic_year_id bigint not null references public.academic_years(academic_year_id),
  grade_id bigint references public.grades(grade_id),
  source_grade_label text not null,
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  source_column_name text not null,
  created_at timestamptz not null default now(),
  constraint student_grade_enrollments_student_year_key unique (student_id, academic_year_id),
  constraint student_grade_enrollments_source_row_number_check check (source_row_number > 0),
  constraint student_grade_enrollments_source_column_name_check check (btrim(source_column_name) <> '')
);

create table public.grade_subjects (
  grade_subject_id bigint generated always as identity primary key,
  grade_id bigint not null references public.grades(grade_id),
  subject_id bigint not null references public.subjects(subject_id),
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  created_at timestamptz not null default now(),
  constraint grade_subjects_grade_subject_key unique (grade_id, subject_id),
  constraint grade_subjects_source_row_number_check check (source_row_number > 0)
);

create table public.assessment_competencies (
  competency_id bigint generated always as identity primary key,
  grade_subject_id bigint not null references public.grade_subjects(grade_subject_id),
  competency_order smallint not null,
  competency_name text not null,
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  created_at timestamptz not null default now(),
  constraint assessment_competencies_grade_subject_order_key unique (grade_subject_id, competency_order),
  constraint assessment_competencies_source_row_number_check check (source_row_number > 0)
);

create table public.assessment_activities (
  activity_id bigint generated always as identity primary key,
  competency_id bigint not null references public.assessment_competencies(competency_id),
  activity_order smallint not null,
  activity_name text not null,
  is_placeholder boolean not null default false,
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  source_column_name text not null,
  created_at timestamptz not null default now(),
  constraint assessment_activities_competency_order_key unique (competency_id, activity_order),
  constraint assessment_activities_source_row_number_check check (source_row_number > 0),
  constraint assessment_activities_source_column_name_check check (btrim(source_column_name) <> '')
);

create table public.student_assessments (
  student_assessment_id bigint generated always as identity primary key,
  student_id text not null references public.students(student_id),
  academic_year_id bigint not null references public.academic_years(academic_year_id),
  grade_subject_id bigint not null references public.grade_subjects(grade_subject_id),
  assessment_period_id bigint not null references public.assessment_periods(assessment_period_id),
  reported_average_score numeric(5,2),
  duplicate_candidate boolean not null default false,
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  created_at timestamptz not null default now(),
  constraint student_assessments_source_row_number_check check (source_row_number > 0)
);

create table public.assessment_scores (
  assessment_score_id bigint generated always as identity primary key,
  student_assessment_id bigint not null references public.student_assessments(student_assessment_id),
  activity_id bigint not null references public.assessment_activities(activity_id),
  raw_score_value text not null,
  numeric_score smallint,
  score_code text references public.assessment_score_codes(score_code),
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  source_column_name text not null,
  created_at timestamptz not null default now(),
  constraint assessment_scores_assessment_activity_key unique (student_assessment_id, activity_id),
  constraint assessment_scores_value_check check (
    (numeric_score is not null and score_code is null and numeric_score between 0 and 10)
    or
    (numeric_score is null and score_code is not null)
  ),
  constraint assessment_scores_source_row_number_check check (source_row_number > 0),
  constraint assessment_scores_source_column_name_check check (btrim(source_column_name) <> '')
);

create table public.attendance_months (
  attendance_month_id bigint generated always as identity primary key,
  student_id text not null references public.students(student_id),
  academic_year_id bigint not null references public.academic_years(academic_year_id),
  grade_id bigint not null references public.grades(grade_id),
  month_number smallint not null,
  source_month_label text not null,
  reported_days_present smallint,
  reported_days_absent smallint,
  reported_attendance_percentage numeric(6,3),
  duplicate_candidate boolean not null default false,
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  created_at timestamptz not null default now(),
  constraint attendance_months_month_number_check check (month_number between 1 and 12),
  constraint attendance_months_days_present_check check (reported_days_present is null or reported_days_present >= 0),
  constraint attendance_months_days_absent_check check (reported_days_absent is null or reported_days_absent >= 0),
  constraint attendance_months_percentage_check check (
    reported_attendance_percentage is null
    or reported_attendance_percentage between 0 and 100
  ),
  constraint attendance_months_source_row_number_check check (source_row_number > 0)
);

create table public.attendance_days (
  attendance_day_id bigint generated always as identity primary key,
  attendance_month_id bigint not null references public.attendance_months(attendance_month_id),
  day_of_month smallint not null,
  raw_status_code text not null,
  normalized_status_code text references public.attendance_status_codes(status_code),
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  source_column_name text not null,
  created_at timestamptz not null default now(),
  constraint attendance_days_month_day_key unique (attendance_month_id, day_of_month),
  constraint attendance_days_day_of_month_check check (day_of_month between 1 and 31),
  constraint attendance_days_source_row_number_check check (source_row_number > 0),
  constraint attendance_days_source_column_name_check check (btrim(source_column_name) <> '')
);

create table public.student_measurements (
  student_measurement_id bigint generated always as identity primary key,
  attendance_month_id bigint not null references public.attendance_months(attendance_month_id),
  age_years numeric(4,1),
  height_cm numeric(6,2),
  weight_kg numeric(6,2),
  reported_bmi_value numeric(6,2),
  reported_bmi_category text,
  source_file_id bigint not null references public.source_files(source_file_id),
  source_sheet_name text not null,
  source_row_number integer not null,
  created_at timestamptz not null default now(),
  constraint student_measurements_attendance_month_key unique (attendance_month_id),
  constraint student_measurements_age_check check (age_years is null or age_years >= 0),
  constraint student_measurements_height_check check (height_cm is null or height_cm > 0),
  constraint student_measurements_weight_check check (weight_kg is null or weight_kg > 0),
  constraint student_measurements_bmi_check check (reported_bmi_value is null or reported_bmi_value > 0),
  constraint student_measurements_source_row_number_check check (source_row_number > 0)
);

-- Foreign-key and common lookup indexes.
create index academic_years_source_file_id_idx on public.academic_years(source_file_id);
create index grades_source_file_id_idx on public.grades(source_file_id);
create index subjects_source_file_id_idx on public.subjects(source_file_id);
create index assessment_periods_source_file_id_idx on public.assessment_periods(source_file_id);
create index assessment_score_codes_source_file_id_idx on public.assessment_score_codes(source_file_id);
create index attendance_status_codes_source_file_id_idx on public.attendance_status_codes(source_file_id);
create index students_source_file_id_idx on public.students(source_file_id);

create index student_grade_enrollments_student_id_idx on public.student_grade_enrollments(student_id);
create index student_grade_enrollments_academic_year_id_idx on public.student_grade_enrollments(academic_year_id);
create index student_grade_enrollments_grade_id_idx on public.student_grade_enrollments(grade_id);
create index student_grade_enrollments_source_file_id_idx on public.student_grade_enrollments(source_file_id);

create index grade_subjects_grade_id_idx on public.grade_subjects(grade_id);
create index grade_subjects_subject_id_idx on public.grade_subjects(subject_id);
create index grade_subjects_source_file_id_idx on public.grade_subjects(source_file_id);

create index assessment_competencies_grade_subject_id_idx on public.assessment_competencies(grade_subject_id);
create index assessment_competencies_source_file_id_idx on public.assessment_competencies(source_file_id);

create index assessment_activities_competency_id_idx on public.assessment_activities(competency_id);
create index assessment_activities_source_file_id_idx on public.assessment_activities(source_file_id);

create index student_assessments_student_id_idx on public.student_assessments(student_id);
create index student_assessments_academic_year_id_idx on public.student_assessments(academic_year_id);
create index student_assessments_grade_subject_id_idx on public.student_assessments(grade_subject_id);
create index student_assessments_assessment_period_id_idx on public.student_assessments(assessment_period_id);
create index student_assessments_source_file_id_idx on public.student_assessments(source_file_id);
create index student_assessments_student_year_idx on public.student_assessments(student_id, academic_year_id);
create index student_assessments_natural_key_idx
  on public.student_assessments(student_id, academic_year_id, grade_subject_id, assessment_period_id);

create index assessment_scores_student_assessment_id_idx on public.assessment_scores(student_assessment_id);
create index assessment_scores_activity_id_idx on public.assessment_scores(activity_id);
create index assessment_scores_score_code_idx on public.assessment_scores(score_code);
create index assessment_scores_source_file_id_idx on public.assessment_scores(source_file_id);

create index attendance_months_student_id_idx on public.attendance_months(student_id);
create index attendance_months_academic_year_id_idx on public.attendance_months(academic_year_id);
create index attendance_months_grade_id_idx on public.attendance_months(grade_id);
create index attendance_months_source_file_id_idx on public.attendance_months(source_file_id);
create index attendance_months_student_year_month_idx
  on public.attendance_months(student_id, academic_year_id, month_number);
create index attendance_months_natural_key_idx
  on public.attendance_months(student_id, academic_year_id, grade_id, month_number);

create index attendance_days_attendance_month_id_idx on public.attendance_days(attendance_month_id);
create index attendance_days_normalized_status_code_idx on public.attendance_days(normalized_status_code);
create index attendance_days_source_file_id_idx on public.attendance_days(source_file_id);

create index student_measurements_source_file_id_idx on public.student_measurements(source_file_id);

-- Public is an exposed Supabase schema. Enable RLS by default; no client policies
-- are created in Phase 1 because the application authorization model is not yet defined.
alter table public.source_files enable row level security;
alter table public.academic_years enable row level security;
alter table public.grades enable row level security;
alter table public.subjects enable row level security;
alter table public.assessment_periods enable row level security;
alter table public.assessment_score_codes enable row level security;
alter table public.attendance_status_codes enable row level security;
alter table public.students enable row level security;
alter table public.student_grade_enrollments enable row level security;
alter table public.grade_subjects enable row level security;
alter table public.assessment_competencies enable row level security;
alter table public.assessment_activities enable row level security;
alter table public.student_assessments enable row level security;
alter table public.assessment_scores enable row level security;
alter table public.attendance_months enable row level security;
alter table public.attendance_days enable row level security;
alter table public.student_measurements enable row level security;
