import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.2/+esm';
import { isUnauthorizedError, parseAssessmentScore } from './app-core.mjs';

const SUPABASE_URL = 'https://tyhwkudogenugnnfgxav.supabase.co';
const SUPABASE_PUBLISHABLE_KEY = 'sb_publishable_UvoJmNRNQXBuQVO1w7qCAA_Aqy47QYo';
const supabase = createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY);
const navs=document.querySelectorAll('.nav'),pages=document.querySelectorAll('.page');
const studentsPage=document.getElementById('students'),authPanel=document.getElementById('authPanel'),studentContent=document.getElementById('studentContent'),studentBody=document.getElementById('studentBody'),studentSearch=document.getElementById('studentSearch'),attendanceDetail=document.getElementById('attendanceDetail'),attendanceGrid=document.getElementById('attendanceGrid'),authMessage=document.getElementById('authMessage'),sessionLabel=document.getElementById('sessionLabel'),signOutButton=document.getElementById('signOutButton');
let session=null,studentRows=[],statusMeanings=new Map();
const academicYearFilter=document.getElementById('academicYearFilter');
const gradeFilter=document.getElementById('gradeFilter');
const REBUILD_YEAR='2025-26';
function isActiveYear(){return academicYearFilter.value===REBUILD_YEAR;}
function applyAcademicYear(){
  const year=academicYearFilter.value,available=isActiveYear();
  for(const page of pages){
    let note=page.querySelector(':scope > .year-unavailable-note');
    if(!note){note=document.createElement('div');note.className='year-unavailable-note';note.setAttribute('role','status');page.prepend(note);}
    note.textContent=available?'':`No verified rebuild data is available for academic year ${year} in this preview. Select 2025–26 to view its provisional student and attendance records. No previous-year values have been inferred.`;
    note.hidden=available;
    page.classList.toggle('year-unavailable',!available);
  }
  attendanceDetail.hidden=true;
  if(available&&document.getElementById('students').classList.contains('active'))refreshStudentsView();
}
academicYearFilter.addEventListener('change',applyAcademicYear);
applyAcademicYear();

navs.forEach(button=>{button.onclick=()=>{navs.forEach(item=>item.classList.remove('active'));pages.forEach(item=>item.classList.remove('active'));button.classList.add('active');document.getElementById(button.dataset.page).classList.add('active');if(button.dataset.page==='students')refreshStudentsView();};});
document.getElementById('attendanceJump').onclick=()=>document.querySelector('[data-page="students"]').click();
function setState(name,message=''){studentsPage.dataset.state=name;document.querySelectorAll('[data-student-state]').forEach(el=>{el.hidden=el.dataset.studentState!==name;});const target=document.querySelector(`[data-student-state="${name}"]`);if(target&&message)target.textContent=message;}
async function fetchAll(table,columns,orderColumn){const pageSize=1000,rows=[];for(let from=0;;from+=pageSize){let query=supabase.from(table).select(columns).range(from,from+pageSize-1);if(orderColumn)query=query.order(orderColumn,{ascending:true});const{data,error}=await query;if(error)throw error;rows.push(...(data??[]));if(!data||data.length<pageSize)break;}return rows;}
async function loadStudents(){if(!isActiveYear())return;setState('loading');try{const {data,error}=await supabase.rpc('kc2_rebuild_students');if(error)throw error;if(!isActiveYear())return;studentRows=Array.isArray(data)?data:[];populateGradeFilter();filterStudents();}catch(error){if(isUnauthorizedError(error)){await supabase.auth.signOut({scope:'local'});session=null;updateAuthUi('Your session expired. Sign in again to view student data.');setState('auth');return;}console.error(error);setState('error',`Could not load staging student data: ${error.message||'Unknown error'}`);}}
function renderStudentRows(rows){studentBody.innerHTML='';for(const row of rows){const tr=document.createElement('tr');const pct=row.attendancePercent==null?'—':`${Number(row.attendancePercent).toFixed(1)}%`;tr.innerHTML=`<td><button class="linkbutton" data-student-id="${escapeHtml(row.student_id)}">${escapeHtml(row.student_name)}</button><small>${escapeHtml(row.student_id)}</small></td><td>${escapeHtml(row.grade)}</td><td>${escapeHtml(row.academicYear)}</td><td>${escapeHtml(row.attendanceMonthLabel)}</td><td>${pct}</td>`;tr.querySelector('button').onclick=()=>loadAttendanceDetail(row);studentBody.appendChild(tr);}}
async function loadAttendanceDetail(student){if(!isActiveYear())return;attendanceDetail.hidden=false;document.getElementById('attendanceTitle').textContent=`${student.student_name} • ${student.attendanceMonthLabel} (provisional)`;attendanceGrid.innerHTML='<div class="muted">Loading staged attendance…</div>';if(!student.attendanceMonth){attendanceGrid.innerHTML='<div class="muted">No staged attendance exists for this student.</div>';return;}const {data,error}=await supabase.rpc('kc2_rebuild_attendance',{p_student_id:student.student_id,p_month:student.attendanceMonth});if(error){attendanceGrid.innerHTML=`<div class="errorText">Could not load attendance: ${escapeHtml(error.message)}</div>`;return;}attendanceGrid.innerHTML=(data||[]).map(day=>`<div class="daychip"><b>${day.day_of_month}</b><span>${escapeHtml(day.raw_status_code)}</span><small>${escapeHtml(day.meaning)}</small></div>`).join('')||'<div class="muted">No staged attendance days.</div>';}
function populateGradeFilter(){
  const current=gradeFilter.value;
  const grades=[...new Set(studentRows.map(row=>String(row.grade??'').trim()).filter(Boolean))];
  const priority=grade=>{const g=grade.toUpperCase();if(g==='LKG')return 0;if(g==='UKG')return 1;const roman=['I','II','III','IV','V','VI','VII','VIII','IX','X'];const n=roman.indexOf(g);return n<0?100:2+n;};
  grades.sort((a,b)=>priority(a)-priority(b)||a.localeCompare(b));
  gradeFilter.replaceChildren(new Option('All grades',''),...grades.map(g=>new Option(g,g)));
  gradeFilter.value=grades.includes(current)?current:'';
}
function filterStudents(){
  const query=studentSearch.value.trim().toLowerCase(),grade=gradeFilter.value;
  const filtered=studentRows.filter(row=>(!grade||String(row.grade??'').trim()===grade)&&`${row.student_name} ${row.student_id} ${row.grade}`.toLowerCase().includes(query));
  attendanceDetail.hidden=true;
  renderStudentRows(filtered);
  setState(filtered.length?'ready':'empty');
}
studentSearch.addEventListener('input',filterStudents);
gradeFilter.addEventListener('change',filterStudents);
document.getElementById('signInForm').addEventListener('submit',async event=>{event.preventDefault();authMessage.textContent='Signing in…';const form=new FormData(event.currentTarget);const{error}=await supabase.auth.signInWithPassword({email:String(form.get('email')),password:String(form.get('password'))});if(error)authMessage.textContent=error.message;});
signOutButton.onclick=async()=>{await supabase.auth.signOut();};
function updateAuthUi(message=''){authPanel.hidden=Boolean(session);studentContent.hidden=!session;signOutButton.hidden=!session;sessionLabel.textContent=session?.user?.email?`Signed in as ${session.user.email}`:'Not signed in';if(message)authMessage.textContent=message;}
async function refreshStudentsView(){if(!isActiveYear())return;if(!session){updateAuthUi();setState('auth');return;}updateAuthUi();await loadStudents();}
const{data:{session:initialSession}}=await supabase.auth.getSession();session=initialSession;updateAuthUi();if(document.querySelector('[data-page="students"]').classList.contains('active'))refreshStudentsView();
supabase.auth.onAuthStateChange((_event,nextSession)=>{session=nextSession;updateAuthUi();if(document.querySelector('[data-page="students"]').classList.contains('active'))queueMicrotask(()=>refreshStudentsView());});
document.querySelectorAll('[data-score-input]').forEach(input=>{input.addEventListener('change',()=>{const parsed=parseAssessmentScore(input.value);input.setCustomValidity(parsed?'':'Enter 0–10 or A for Absent.');if(parsed)input.value=parsed.raw;input.reportValidity();});});
function escapeHtml(value){return String(value??'').replace(/[&<>'"]/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));}