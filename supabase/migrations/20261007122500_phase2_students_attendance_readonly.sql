-- Phase 2 milestone: Students & Attendance read-only access.
-- Approved Option A: every authenticated internal user may read all student-level records.
-- RLS stays enabled. No INSERT/UPDATE/DELETE policies are created.

begin;

grant select on table public.students to authenticated;
grant select on table public.student_grade_enrollments to authenticated;
grant select on table public.grades to authenticated;
grant select on table public.academic_years to authenticated;
grant select on table public.attendance_months to authenticated;
grant select on table public.attendance_days to authenticated;
grant select on table public.attendance_status_codes to authenticated;

create policy "students_authenticated_select"
  on public.students for select to authenticated using (true);

create policy "student_grade_enrollments_authenticated_select"
  on public.student_grade_enrollments for select to authenticated using (true);

create policy "grades_authenticated_select"
  on public.grades for select to authenticated using (true);

create policy "academic_years_authenticated_select"
  on public.academic_years for select to authenticated using (true);

create policy "attendance_months_authenticated_select"
  on public.attendance_months for select to authenticated using (true);

create policy "attendance_days_authenticated_select"
  on public.attendance_days for select to authenticated using (true);

create policy "attendance_status_codes_authenticated_select"
  on public.attendance_status_codes for select to authenticated using (true);

commit;
