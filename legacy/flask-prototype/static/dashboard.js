const $ = (selector, root=document) => root.querySelector(selector);
const $$ = (selector, root=document) => [...root.querySelectorAll(selector)];
let dashboardState = {goals:[], activities:[], study:[], history:[], summary:{}};

function localDate(date=new Date()){
  const offset = date.getTimezoneOffset();
  return new Date(date.getTime()-offset*60000).toISOString().slice(0,10);
}
function escapeHtml(value){
  return String(value ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}
async function api(path, method='GET', body){
  const response = await fetch(path,{method,headers:{'Content-Type':'application/json'},body:body ? JSON.stringify(body) : undefined});
  const data = await response.json().catch(()=>({message:'Something went wrong.'}));
  if(!response.ok) throw data;
  return data;
}
function number(value, digits=0){ return Number(value || 0).toLocaleString(undefined,{maximumFractionDigits:digits}); }
function showToast(message){
  const toast=$('#toast'); toast.textContent=message; toast.classList.add('show');
  clearTimeout(showToast.timer); showToast.timer=setTimeout(()=>toast.classList.remove('show'),2600);
}
function openModal(id){
  const modal=document.getElementById(id); if(modal && !modal.open) modal.showModal();
}
function closeModal(id){ const modal=document.getElementById(id); if(modal?.open) modal.close(); }
function categoryIcon(category){ return ({fitness:'↗',study:'▤',wellness:'♡',work:'◇',personal:'◎'})[category] || '◎'; }
function activityLabel(type){ return ({steps:'Steps',running:'Run',walking:'Walk',workout:'Workout',cycling:'Cycle',swimming:'Swim',yoga:'Yoga',sports:'Sport'})[type] || type; }

async function loadUser(){
  try{
    const result=await api('/api/user'); const user=result.user;
    const hour=new Date().getHours(); const greeting=hour<12?'Good morning':hour<18?'Good afternoon':'Good evening';
    $('#greeting').textContent=`${greeting}, ${user.name.split(' ')[0]}`;
    $('#profileName').textContent=user.name; $('#userAvatar').textContent=user.name.charAt(0).toUpperCase();
    $('#todayLabel').textContent=new Date().toLocaleDateString(undefined,{weekday:'long',month:'long',day:'numeric'}).toUpperCase();
  }catch(error){ location.href='/login'; }
}

async function loadDashboard(quiet=false){
  try{
    const result=await api('/api/dashboard-summary'); dashboardState=result;
    renderHero(); renderStats(); renderTracker(); renderGoals(); renderHistory(); renderActivities(); renderStudy();
  }catch(error){ if(!quiet) showToast(error.message || 'Could not load your dashboard.'); }
}
function renderHero(){
  const total=dashboardState.goals.length, completed=dashboardState.goals.filter(goal=>goal.completed).length;
  const percent=total ? Math.round(completed/total*100) : 0;
  $('#heroCompleted').textContent=completed; $('#heroTotal').textContent=total; $('#overallPercent').textContent=`${percent}%`;
  $('#progressOrbit').style.setProperty('--progress',percent);
  $('#heroMessage').textContent=total===0?'Add your first goal and make today count.':percent===100?'Day conquered. Enjoy that earned satisfaction.':`${total-completed} goal${total-completed===1?'':'s'} left. Keep the rhythm alive.`;
}
function renderStats(){
  const s=dashboardState.summary || {};
  $('#stepsValue').textContent=number(s.steps); $('#caloriesValue').innerHTML=`${number(s.calories)} <em>kcal</em>`;
  $('#distanceValue').innerHTML=`${number(s.distance,2)} <em>km</em>`; $('#activeValue').innerHTML=`${number(s.active_minutes)} <em>min</em>`;
  $('#stepsHint').textContent=`${Math.min(100,Math.round((s.steps||0)/10000*100))}% of 10,000 today`;
}
function renderTracker(){
  const tracker=dashboardState.tracker || {};
  const connect=$('#fitbitConnectBtn'), sync=$('#fitbitSyncBtn'), disconnect=$('#fitbitDisconnectBtn'), status=$('#trackerStatus');
  if(tracker.connected){
    connect.hidden=true; sync.hidden=false; disconnect.hidden=false;
    const last=tracker.last_synced_at ? new Date(`${tracker.last_synced_at.replace(' ','T')}Z`) : null;
    const when=last && !Number.isNaN(last.getTime()) ? last.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}) : 'recently';
    status.textContent=`Fitbit connected · automatically synced ${when}`; status.classList.add('tracker-connected');
  }else{
    connect.hidden=false; sync.hidden=true; disconnect.hidden=true;
    status.textContent='Connect a wearable for automatic tracking, or log activity manually.'; status.classList.remove('tracker-connected');
  }
}
function renderGoals(){
  const list=$('#goalList'); const goals=dashboardState.goals || [];
  if(!goals.length){ list.innerHTML='<div class="empty-state"><span>◎</span><h3>Your day is a blank canvas</h3><p>Add a measurable goal to start building momentum.</p></div>'; return; }
  list.innerHTML=goals.map(goal=>{
    const percent=Math.min(100,Math.round(Number(goal.current_value)/Number(goal.target_value)*100));
    return `<article class="goal-row ${goal.completed?'done':''}">
      <button class="goal-check" data-complete-goal="${goal.id}" aria-label="${goal.completed?'Completed':'Complete goal'}">${goal.completed?'✓':categoryIcon(goal.category)}</button>
      <div><div class="goal-name">${escapeHtml(goal.title)}</div><div class="goal-meta"><span class="category-chip">${escapeHtml(goal.category)}</span><span>${percent}% complete</span></div></div>
      <div class="goal-progress"><strong>${number(goal.current_value,2)} / ${number(goal.target_value,2)} ${escapeHtml(goal.unit)}</strong><div class="micro-progress"><i style="width:${percent}%"></i></div><div class="goal-actions">${!goal.completed?`<button class="tiny-button" data-progress-goal="${goal.id}">＋ progress</button>`:''}<button class="tiny-button danger" data-delete-goal="${goal.id}">remove</button></div></div>
    </article>`;
  }).join('');
}
function renderHistory(){
  const chart=$('#historyChart'); const history=dashboardState.history || [];
  chart.innerHTML=history.map((day,index)=>`<div class="day-bar ${index===history.length-1?'today':''}" title="${day.completed} of ${day.total} goals"><div class="bar-track"><i class="bar-fill" style="height:${day.total?Math.max(6,day.percent):4}%"></i></div><span>${escapeHtml(day.label)}</span></div>`).join('');
  const streak=dashboardState.summary?.streak || 0; $('#streakValue').textContent=streak;
  $('#historyTitle').textContent=streak?`${streak} strong day${streak===1?'':'s'} in a row`:'Your story starts today';
  $('#historyText').textContent=streak?'Consistency is becoming your advantage.':'Complete every goal to begin your streak.';
}
function renderActivities(){
  const feed=$('#activityFeed'); const activities=dashboardState.activities || [];
  if(!activities.length){ feed.innerHTML='<span class="activity-tag">Nothing logged yet—pick an activity above.</span>'; return; }
  feed.innerHTML=activities.map(item=>`<span class="activity-tag"><b>${escapeHtml(activityLabel(item.activity_type))}</b><span>${number(item.value,2)} ${escapeHtml(item.unit)}${item.duration?` · ${item.duration} min`:''}${item.calories?` · ${item.calories} kcal`:''}</span><button data-delete-activity="${item.id}" aria-label="Remove activity">×</button></span>`).join('');
}
function renderStudy(){
  const list=$('#studyList'); const goals=dashboardState.study || [];
  if(!goals.length){ list.innerHTML='<div class="empty-state"><span>▤</span><h3>No chapters planned yet</h3><p>Add a subject and chapter to create a focused study target.</p></div>'; return; }
  list.innerHTML=goals.map((goal,index)=>{
    const minutePercent=Math.round(goal.studied_minutes/goal.target_minutes*100), topicPercent=Math.round(goal.topics_completed/goal.topics_total*100), progress=Math.min(100,Math.round((minutePercent+topicPercent)/2));
    const due=new Date(`${goal.due_date}T00:00:00`).toLocaleDateString(undefined,{month:'short',day:'numeric'});
    const colors=['#4a9b75','#7c6ac2','#d5864c','#4f86bd'];
    return `<article class="study-card ${goal.completed?'done':''}" style="--subject:${colors[index%colors.length]}"><div class="study-card-head"><div><span class="subject-label">${escapeHtml(goal.subject)}</span><h3>${escapeHtml(goal.chapter)}</h3></div><span class="due-chip">Due ${due}</span></div><div class="study-metrics"><div><strong>${goal.studied_minutes}/${goal.target_minutes}m</strong><span>focus time</span></div><div><strong>${goal.topics_completed}/${goal.topics_total}</strong><span>topics covered</span></div></div><div class="study-progress"><i style="width:${progress}%"></i></div><div class="study-footer"><span>${goal.completed?'Completed ✓':`${progress}% overall`}</span><div class="study-actions">${!goal.completed?`<button class="tiny-button" data-study-time="${goal.id}">＋15m</button><button class="tiny-button" data-study-topic="${goal.id}">＋topic</button>`:''}<button class="tiny-button danger" data-delete-study="${goal.id}">×</button></div></div></article>`;
  }).join('');
}

$$('[data-open-modal]').forEach(button=>button.addEventListener('click',()=>openModal(button.dataset.openModal)));
$$('.modal').forEach(modal=>modal.addEventListener('click',event=>{ if(event.target===modal) modal.close(); }));
$('#goalDate').value=localDate(); $('#activityDate').value=localDate(); $('#studyDue').value=localDate(new Date(Date.now()+7*86400000));

$('#goalForm').addEventListener('submit',async event=>{
  event.preventDefault();
  try{ await api('/api/daily-goals','POST',{title:$('#goalTitle').value,category:$('#goalCategory').value,target_value:$('#goalTarget').value,unit:$('#goalUnit').value,goal_date:$('#goalDate').value}); event.target.reset(); $('#goalDate').value=localDate(); $('#goalTarget').value=1; $('#goalUnit').value='task'; closeModal('goalModal'); showToast('Goal added to your day.'); await loadDashboard(true); }
  catch(error){ showToast(error.message || 'Could not add goal.'); }
});
$('#activityForm').addEventListener('submit',async event=>{
  event.preventDefault();
  try{ await api('/api/activities','POST',{activity_type:$('#activityType').value,value:$('#activityValue').value,unit:$('#activityUnit').value,duration:$('#activityDuration').value,calories:$('#activityCalories').value,notes:$('#activityNotes').value,log_date:$('#activityDate').value}); event.target.reset(); $('#activityDate').value=localDate(); closeModal('activityModal'); showToast('Activity logged. Nice work.'); await loadDashboard(true); }
  catch(error){ showToast(error.message || 'Could not log activity.'); }
});
$('#studyForm').addEventListener('submit',async event=>{
  event.preventDefault();
  try{ await api('/api/study-goals','POST',{subject:$('#studySubject').value,chapter:$('#studyChapter').value,target_minutes:$('#studyMinutes').value,topics_total:$('#studyTopics').value,due_date:$('#studyDue').value}); event.target.reset(); $('#studyDue').value=localDate(new Date(Date.now()+7*86400000)); $('#studyMinutes').value=90; $('#studyTopics').value=5; closeModal('studyModal'); showToast('Chapter added to your study plan.'); await loadDashboard(true); }
  catch(error){ showToast(error.message || 'Could not add study goal.'); }
});

$('#goalList').addEventListener('click',async event=>{
  const complete=event.target.closest('[data-complete-goal]'), progress=event.target.closest('[data-progress-goal]'), remove=event.target.closest('[data-delete-goal]');
  try{
    if(complete) await api('/api/daily-goals','PUT',{id:complete.dataset.completeGoal,completed:true});
    if(progress){ const goal=dashboardState.goals.find(item=>String(item.id)===progress.dataset.progressGoal); const increment=Math.max(1,Number(goal.target_value)/4); await api('/api/daily-goals','PUT',{id:goal.id,increment}); }
    if(remove) await api('/api/daily-goals','DELETE',{id:remove.dataset.deleteGoal});
    if(complete||progress||remove) await loadDashboard(true);
  }catch(error){ showToast(error.message || 'Could not update goal.'); }
});
$('#activityFeed').addEventListener('click',async event=>{ const button=event.target.closest('[data-delete-activity]'); if(!button)return; await api('/api/activities','DELETE',{id:button.dataset.deleteActivity}); await loadDashboard(true); });
$('#studyList').addEventListener('click',async event=>{
  const time=event.target.closest('[data-study-time]'), topic=event.target.closest('[data-study-topic]'), remove=event.target.closest('[data-delete-study]');
  try{ if(time)await api('/api/study-goals','PUT',{id:time.dataset.studyTime,minutes:15}); if(topic)await api('/api/study-goals','PUT',{id:topic.dataset.studyTopic,topics:1}); if(remove)await api('/api/study-goals','DELETE',{id:remove.dataset.deleteStudy}); if(time||topic||remove)await loadDashboard(true); }catch(error){ showToast(error.message || 'Could not update study goal.'); }
});
$$('[data-quick-activity]').forEach(button=>button.addEventListener('click',()=>{
  const type=button.dataset.quickActivity; $('#activityType').value=type;
  const unit=type==='steps'?'steps':type==='workout'?'sets':'km'; $('#activityUnit').value=unit; openModal('activityModal');
}));
$('#activityType').addEventListener('change',event=>{ const type=event.target.value; $('#activityUnit').value=type==='steps'?'steps':['running','walking','cycling','swimming'].includes(type)?'km':'minutes'; });
$('#fitbitSyncBtn').addEventListener('click',async()=>{
  const button=$('#fitbitSyncBtn'); button.disabled=true; button.textContent='Syncing…';
  try{ await api('/api/fitbit/sync','POST'); showToast('Fitbit data synced.'); await loadDashboard(true); }
  catch(error){ showToast(error.message || 'Fitbit sync failed.'); }
  finally{ button.disabled=false; button.textContent='↻ Sync Fitbit'; }
});
$('#fitbitDisconnectBtn').addEventListener('click',async()=>{
  if(!confirm('Disconnect Fitbit and remove its synced data from DayFlow?')) return;
  try{ await api('/api/fitbit/disconnect','DELETE'); showToast('Fitbit disconnected.'); await loadDashboard(true); }
  catch(error){ showToast(error.message || 'Could not disconnect Fitbit.'); }
});
$('#logoutBtn').addEventListener('click',async()=>{ await api('/api/logout','POST'); location.href='/login'; });
$('#menuBtn').addEventListener('click',()=>$('#sidebar').classList.toggle('open'));
$$('.nav-item').forEach(item=>item.addEventListener('click',()=>{ $$('.nav-item').forEach(link=>link.classList.remove('active')); item.classList.add('active'); $('#sidebar').classList.remove('open'); }));

const trackerParams=new URLSearchParams(location.search);
if(trackerParams.get('tracker')==='connected') showToast('Fitbit connected and syncing automatically.');
if(trackerParams.get('tracker_error')) showToast(trackerParams.get('tracker_error'));
if(trackerParams.has('tracker') || trackerParams.has('tracker_error')) history.replaceState({},'',location.pathname);
loadUser(); loadDashboard();