export const SCORE_RULES = Object.freeze({
  numericMin: 0,
  numericMax: 10,
  absentCode: 'A',
  invalidExamples: Object.freeze(['77', '87', '89']),
  unresolvedCode: 'N',
});

export function parseAssessmentScore(rawValue) {
  const raw = String(rawValue ?? '').trim();
  if (raw === SCORE_RULES.absentCode) {
    return { raw: 'A', numericScore: null, scoreCode: 'A', effectiveValue: 0 };
  }
  if (!/^(?:10|[0-9])$/.test(raw)) return null;
  const numericScore = Number(raw);
  return { raw, numericScore, scoreCode: null, effectiveValue: numericScore };
}

export function calculateAssessmentAverage(values) {
  if (!values.length) return null;
  const parsed = values.map(parseAssessmentScore);
  if (parsed.some(value => value === null)) return null;
  return parsed.reduce((sum, value) => sum + value.effectiveValue, 0) / parsed.length;
}

export function latestBy(items, field) {
  return [...items].sort((a, b) => String(b[field] ?? '').localeCompare(String(a[field] ?? '')))[0] ?? null;
}

export function buildStudentRows({ students, enrollments, academicYears, grades, attendanceMonths }) {
  const yearById = new Map(academicYears.map(row => [row.academic_year_id, row]));
  const gradeById = new Map(grades.map(row => [row.grade_id, row]));
  const enrollmentsByStudent = new Map();
  const attendanceByStudent = new Map();

  for (const row of enrollments) {
    if (!enrollmentsByStudent.has(row.student_id)) enrollmentsByStudent.set(row.student_id, []);
    enrollmentsByStudent.get(row.student_id).push(row);
  }
  for (const row of attendanceMonths) {
    if (!attendanceByStudent.has(row.student_id)) attendanceByStudent.set(row.student_id, []);
    attendanceByStudent.get(row.student_id).push(row);
  }

  return students.map(student => {
    const enrollmentRows = (enrollmentsByStudent.get(student.student_id) ?? []).map(row => ({
      ...row,
      year_label: yearById.get(row.academic_year_id)?.year_label ?? '',
      grade_code: gradeById.get(row.grade_id)?.grade_code ?? row.source_grade_label ?? '',
    }));
    const latestEnrollment = latestBy(enrollmentRows, 'year_label');
    const monthRows = attendanceByStudent.get(student.student_id) ?? [];
    const latestAttendance = [...monthRows].sort((a, b) => {
      const ay = yearById.get(a.academic_year_id)?.year_label ?? '';
      const by = yearById.get(b.academic_year_id)?.year_label ?? '';
      return by.localeCompare(ay) || (b.month_number - a.month_number);
    })[0] ?? null;

    return {
      ...student,
      grade: latestEnrollment?.grade_code || '—',
      academicYear: latestEnrollment?.year_label || '—',
      attendancePercent: latestAttendance?.reported_attendance_percentage ?? null,
      attendanceMonthId: latestAttendance?.attendance_month_id ?? null,
      attendanceMonthLabel: latestAttendance?.source_month_label ?? '—',
    };
  });
}

export function isUnauthorizedError(error) {
  if (!error) return false;
  return [401, 403].includes(Number(error.status)) || /jwt|session|unauthor|permission/i.test(String(error.message ?? ''));
}
