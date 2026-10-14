import {createClient} from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.2/+esm';
const db=createClient('https://tyhwkudogenugnnfgxav.supabase.co','sb_publishable_UvoJmNRNQXBuQVO1w7qCAA_Aqy47QYo');
const $=id=>document.getElementById(id);
const txt=(tag,val)=>{const n=document.createElement(tag);n.textContent=String(val??'—');return n;};
let session=null,records=null;
async function fetchAll(table,cols){let rows=[];for(let offset=0;;offset+=1000){const {data,error}=await db.from(table).select(cols).range(offset,offset+999);if(error)throw error;rows.push(...(data||[]));if(!data||data.length<1000)break;}return rows;}
function row(key,value){const el=txt('div','');el.className='row';el.append(txt('span',key),txt('strong',value));return el;}
function card(label,value){const el=txt('div','');el.className='card';el.append(txt('span',label),txt('b',value));return el;}
function render(){const year=$('workYear').value,att=records.att.filter(r=>!year||String(r.academic_year_id)===year),ass=records.ass.filter(r=>!year||String(r.academic_year_id)===year),enr=records.enr.filter(r=>!year||String(r.academic_year_id)===year);
$('workCards').replaceChildren(card('Students with enrolment',new Set(enr.map(x=>x.student_id)).size),card('Students with attendance',new Set(att.map(x=>x.student_id)).size),card('Students assessed',new Set(ass.map(x=>x.student_id)).size),card('Assessment records',ass.length));
$('workReview').replaceChildren(row('Assessment duplicate candidates',ass.filter(r=>r.duplicate_candidate).length),row('Attendance duplicate candidates',att.filter(r=>r.duplicate_candidate).length),row('Assessment records missing reported average',ass.filter(r=>r.reported_average_score==null).length),row('Attendance month records missing reported percentage',att.filter(r=>r.reported_attendance_percentage==null).length));
const labels=new Map(records.periods.map(x=>[x.assessment_period_id,x.source_label||x.period_code])),periodCounts=new Map();for(const a of ass){const key=labels.get(a.assessment_period_id)||'Other';periodCounts.set(key,(periodCounts.get(key)||0)+1);}
$('workPeriods').replaceChildren(...([...periodCounts].length?[...periodCounts].sort((a,b)=>a[0].localeCompare(b[0])).map(([k,n])=>row(k,n)):[txt('p','No assessment records for this selection.')]));
$('workState').textContent='Live source records loaded. Counts are not task assignments.';}
async function open(force=false){
if(!session){$('workAuth').hidden=false;$('workWorkspace').hidden=true;return;}
$('workAuth').hidden=true;$('workWorkspace').hidden=false;if(records&&!force){render();return;}
$('workState').textContent='Loading records…';
try{const [enr,att,ass,years,periods]=await Promise.all([fetchAll('student_grade_enrollments','student_id,academic_year_id'),fetchAll('attendance_months','student_id,academic_year_id,duplicate_candidate,reported_attendance_percentage'),fetchAll('student_assessments','student_id,academic_year_id,assessment_period_id,duplicate_candidate,reported_average_score'),fetchAll('academic_years','academic_year_id,year_label'),fetchAll('assessment_periods','assessment_period_id,source_label,period_code')]);
if(!session)return;
records={enr,att,ass,years,periods};const select=$('workYear'),prior=select.value;select.replaceChildren();const all=txt('option','All academic years');all.value='';select.append(all);for(const y of years.sort((a,b)=>String(b.year_label).localeCompare(String(a.year_label)))){const op=txt('option',y.year_label);op.value=String(y.academic_year_id);select.append(op);}if([...select.options].some(o=>o.value===prior))select.value=prior;render();
}catch(e){$('workState').textContent='Unable to load My Work: '+(e.message||'Unknown error');}}
const nav=document.querySelector('[data-page="work"]');nav.addEventListener('click',()=>open());$('workYear').addEventListener('change',()=>{if(records)render();});$('workRefresh').addEventListener('click',()=>open(true));
document.querySelectorAll('[data-work-jump]').forEach(b=>b.addEventListener('click',()=>document.querySelector('[data-page="'+b.dataset.workJump+'"]').click()));
session=(await db.auth.getSession()).data.session;
db.auth.onAuthStateChange((_event,next)=>{session=next;if(!session){records=null;open();}else if(nav.classList.contains('active'))open();});
if(nav.classList.contains('active'))open();
