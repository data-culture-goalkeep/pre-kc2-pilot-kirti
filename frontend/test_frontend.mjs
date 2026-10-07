import assert from 'node:assert/strict';
import fs from 'node:fs';
import { calculateAssessmentAverage, parseAssessmentScore, buildStudentRows, isUnauthorizedError } from './app-core.mjs';

assert.deepEqual(parseAssessmentScore('0'), { raw:'0', numericScore:0, scoreCode:null, effectiveValue:0 });
assert.deepEqual(parseAssessmentScore('10'), { raw:'10', numericScore:10, scoreCode:null, effectiveValue:10 });
assert.deepEqual(parseAssessmentScore('A'), { raw:'A', numericScore:null, scoreCode:'A', effectiveValue:0 });
for (const value of ['77','87','89','N','-1','11']) assert.equal(parseAssessmentScore(value), null);
assert.equal(calculateAssessmentAverage(['8','A','7']), 5);
assert.equal(calculateAssessmentAverage(['0','5','10']), 5);
assert.equal(calculateAssessmentAverage(['A','A']), 0);

const rows = buildStudentRows({
  students:[{student_id:'S1',student_name:'One'}],
  enrollments:[{student_id:'S1',academic_year_id:1,grade_id:2,source_grade_label:'Class 3'}],
  academicYears:[{academic_year_id:1,year_label:'2025-26'}],
  grades:[{grade_id:2,grade_code:'3'}],
  attendanceMonths:[{attendance_month_id:9,student_id:'S1',academic_year_id:1,grade_id:2,month_number:9,source_month_label:'Sep',reported_attendance_percentage:82}],
});
assert.equal(rows[0].grade,'3');
assert.equal(rows[0].attendancePercent,82);
assert.equal(isUnauthorizedError({status:401,message:'Unauthorized'}),true);
assert.equal(isUnauthorizedError({status:500,message:'Oops'}),false);

const source = fs.readFileSync(new URL('./app.mjs', import.meta.url), 'utf8');
const html = fs.readFileSync(new URL('./index.html', import.meta.url), 'utf8');
assert.match(source, /sb_publishable_/);
assert.doesNotMatch(source + html, /service[_-]?role|sb_secret_|SUPABASE_SERVICE_ROLE_KEY/i);
assert.match(source, /signInWithPassword/);
assert.match(source, /getSession\(\)/);
assert.match(source, /onAuthStateChange/);
assert.match(source, /from\('attendance_days'\)/);
assert.match(html, /0–10 or <b>A<\/b> \(Absent\)/);
assert.doesNotMatch(html, /integers 1[–-]10 only/i);

console.log('frontend tests: PASS');
