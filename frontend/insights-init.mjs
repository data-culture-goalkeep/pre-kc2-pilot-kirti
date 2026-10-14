import {createClient} from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.2/+esm';
const supabase=createClient('https://tyhwkudogenugnnfgxav.supabase.co','sb_publishable_UvoJmNRNQXBuQVO1w7qCAA_Aqy47QYo');
const $=id=>document.getElementById(id);
const node=(tag,value)=>{const e=document.createElement(tag);e.textContent=String(value??'—');return e;};
let session=null,data=null;
async function fetchAll(table,columns){const rows=[];for(let offset=0;;offset+=1000){const {data:page,error}=await supabase.from(table).select(columns).range(offset,offset+999);if(error)throw error;rows.push(...(page||[]));if(!page||page.length<1000)break;}return rows;}
function metric(label,value){const card=node('div','');card.className='card';card.append(node('span',label),node('b',value));return card;}
function line(label,value){const d=node('div','');d.className='row';d.append(node('span',label),node('strong',value));return d;}
function fill(id,rows){$(id).replaceChildren(...(rows.length?rows:[node('p','No source records for this selection.')]));}
function render(){
const year=$('insightsYear').value;
const enrolments=data.enrolments.filter(r=>!year||String(r.academic_year_id)===year);
const attendance=data.attendance.filter(r=>!year||String(r.academic_year_id)===year);
const assessments=data.assessments.filter(r=>!year||String(r.academic_year_id)===year);
const uniqueStudents=new Set(enrolments.map(r=>r.student_id));
const assessedStudents=new Set(assessments.map(r=>r.student_id));
const attendedStudents=new Set(attendance.map(r=>r.student_id));
const cards=$('insightsCards');cards.replaceChildren(metric('Students enrolled',uniqueStudents.size),metric('Students with attendance',attendedStudents.size),metric('Students with assessments',assessedStudents.size),metric('Assessment records',assessments.length));
const grades=new Map(data.grades.map(g=>[g.grade_id,g.grade_name]));
const byGrade=new Map();for(const r of enrolments){const label=grades.get(r.grade_id)||r.source_grade_label||'Unmapped';byGrade.set(label,(byGrade.get(label)||0)+1);}
fill('insightsGrades',[...byGrade].sort((a,b)=>a[0].localeCompare(b[0])).map(([label,count])=>line(label,count)));
const percentages=attendance.filter(r=>r.reported_attendance_percentage!=null).map(r=>Number(r.reported_attendance_percentage));
const avg=percentages.length? (percentages.reduce((x,y)=>x+y,0)/percentages.length).toFixed(1)+'%':'Not available';
fill('insightsAttendance',[line('Attendance month records',attendance.length),line('Students represented',attendedStudents.size),line('Records with reported percentage',percentages.length),line('Mean of source-reported monthly percentages',avg)]);
const per=new Map(data.periods.map(p=>[p.assessment_period_id,p.source_label||p.period_code]));const perCount=new Map();for(const r of assessments){const name=per.get(r.assessment_period_id)||'Unmapped period';perCount.set(name,(perCount.get(name)||0)+1);}
fill('insightsPeriods',[...perCount].sort((a,b)=>a[0].localeCompare(b[0])).map(([name,n])=>line(name,n)));
fill('insightsReview',[line('Assessment duplicate candidates',assessments.filter(r=>r.duplicate_candidate).length),line('Attendance duplicate candidates',attendance.filter(r=>r.duplicate_candidate).length),line('Assessment records with reported average',assessments.filter(r=>r.reported_average_score!=null).length),line('Records containing unresolved attendance code N','Not evaluated in this summary')]);
$('insightsState').textContent='Live source data loaded. Counts update with the academic year filter.';
}
async function open(force=false){
if(!session){$('insightsAuth').hidden=false;$('insightsWorkspace').hidden=true;return;}
$('insightsAuth').hidden=true;$('insightsWorkspace').hidden=false;
if(data&&!force){render();return;}
$('insightsState').textContent='Loading programme records from Supabase…';
try{const [enrolments,attendance,assessments,grades,years,periods]=await Promise.all([
fetchAll('student_grade_enrollments','student_id,academic_year_id,grade_id,source_grade_label'),
fetchAll('attendance_months','student_id,academic_year_id,reported_attendance_percentage,duplicate_candidate'),
fetchAll('student_assessments','student_id,academic_year_id,assessment_period_id,reported_average_score,duplicate_candidate'),
fetchAll('grades','grade_id,grade_name'),
fetchAll('academic_years','academic_year_id,year_label'),
fetchAll('assessment_periods','assessment_period_id,source_label,period_code')]);
if(!session)return;
data={enrolments,attendance,assessments,grades,years,periods};
const select=$('insightsYear'),previous=select.value;select.replaceChildren();let opt=node('option','All academic years');opt.value='';select.append(opt);
for(const y of years.sort((a,b)=>String(b.year_label).localeCompare(String(a.year_label)))){opt=node('option',y.year_label);opt.value=String(y.academic_year_id);select.append(opt);}select.value=previous&&[...select.options].some(x=>x.value===previous)?previous:'';
render();
}catch(error){$('insightsState').textContent='Unable to load programme data: '+(error.message||'Unknown error');}}
const nav=document.querySelector('[data-page="insights"]');
nav.addEventListener('click',()=>open());
$('insightsYear').addEventListener('change',()=>{if(data)render();});
$('insightsRefresh').addEventListener('click',()=>open(true));
session=(await supabase.auth.getSession()).data.session;
supabase.auth.onAuthStateChange((_event,next)=>{session=next;if(!session){data=null;open();}else if(nav.classList.contains('active'))open();});
if(nav.classList.contains('active'))open();
