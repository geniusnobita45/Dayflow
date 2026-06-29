// shared frontend logic for all templates (calls Flask API endpoints)

// --- small helper ---
async function apiFetch(path, method='GET', body=null){
  const opts = {method, headers:{'Content-Type':'application/json'}};
  if(body) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  if(res.status === 204) return null;
  const json = await res.json();
  if(!res.ok) throw json;
  return json;
}

// --- Signup page ---
const signupForm = document.getElementById('signupForm');
if(signupForm){
  signupForm.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    try{
      const out = await apiFetch('/api/signup','POST',{name,email,password});
      if(out.status==='ok') window.location.href = '/goal-setup';
    }catch(err){ alert(err.message || 'Signup failed'); }
  });
}

// --- Login page ---
const loginForm = document.getElementById('loginForm');
if(loginForm){
  loginForm.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    try{
      const out = await apiFetch('/api/login','POST',{email,password});
      if(out.status==='ok') window.location.href = '/goal-setup';
    }catch(err){ alert(err.message || 'Login failed'); }
  });
}

// --- Goal setup page ---
const goalForm = document.getElementById('goalForm');
if(goalForm){
  goalForm.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const type = document.getElementById('goalType').value;
    const duration = document.getElementById('goalDuration').value;
    try{
      const out = await apiFetch('/api/goal','POST',{type,duration});
      if(out.status==='ok') window.location.href = '/timetable-choice';
    }catch(err){ alert('Error saving goal'); }
  });
}

// --- Manual timetable page ---
const manualForm = document.getElementById('manualTimetableForm');
if(manualForm){
  const listEl = document.getElementById('taskList');

  // helper to refresh tasks from server
  async function refreshTasks(){
    try{
      const res = await apiFetch('/api/tasks','GET');
      const tasks = res.tasks || [];
      listEl.innerHTML = tasks.map(t=>`<div><b>${t.name}</b> (${t.start_time||t.start} - ${t.end_time||t.end || ''}) [${t.priority || ''}]</div>`).join('');
    }catch(err){ listEl.innerHTML = '<div class="small-muted">No tasks yet</div>'; }
  }
  refreshTasks();

  manualForm.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const name = document.getElementById('taskName').value.trim();
    const start = document.getElementById('startTime').value;
    const end = document.getElementById('endTime').value;
    const priority = document.getElementById('priority').value;
    if(!name||!start||!end){ alert('Enter all fields'); return; }
    try{
      await apiFetch('/api/tasks','POST',{tasks:[{name,start,end,priority}]});
      document.getElementById('taskName').value=''; document.getElementById('startTime').value=''; document.getElementById('endTime').value='';
      await refreshTasks();
      alert('Task added');
    }catch(err){ alert('Unable to add task'); }
  });
}

// --- Generator page ---
const genForm = document.getElementById('generateForm');
if(genForm){
  genForm.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const wake = document.getElementById('wakeTime').value;
    const sleep = document.getElementById('sleepTime').value;
    if(!wake || !sleep){ alert('Enter wake & sleep time'); return; }
    // fetch current goal to decide generator plan (simple logic)
    // We'll retrieve user goal via /api/user then /api/goal isn't exposed; we rely on server-side goal saved earlier.
    // For simplicity, just create a small plan and POST to /api/tasks
    const tasks = [
      { name: "Morning Routine", start: wake, end: addMinutesToTime(wake, 30), priority: "medium" },
      { name: "Focused Session", start: addMinutesToTime(wake, 60), end: addMinutesToTime(wake, 180), priority: "high" },
      { name: "Evening Review", start: "19:00", end: "19:30", priority: "medium" }
    ];
    try{
      await apiFetch('/api/tasks','POST',{tasks});
      document.getElementById('generatedSchedule').innerHTML = tasks.map(t=>`<p>${t.name} (${t.start} - ${t.end})</p>`).join('');
      alert('Generated and saved to your schedule');
    }catch(err){ alert('Error generating schedule'); }
  });
}

function addMinutesToTime(t, delta){
  const [hh,mm] = t.split(':').map(s=>parseInt(s,10));
  const m = hh*60 + mm + delta;
  const nh = Math.floor((m%1440)/60).toString().padStart(2,'0');
  const nm = (m%60).toString().padStart(2,'0');
  return `${nh}:${nm}`;
}

// --- Dashboard page ---
const taskList = document.getElementById('taskList');
const greetingEl = document.getElementById('greeting');
const userGoalEl = document.getElementById('userGoal');
const streakValEl = document.getElementById('streakValue');
const logoutBtn = document.getElementById('logoutBtn');

if(taskList){
  async function loadDashboard(){
    try{
      const u = await apiFetch('/api/user','GET');
      if(u.status==='ok'){
        const user = u.user;
        const hr = new Date().getHours();
        const greet = hr < 12 ? 'Good Morning' : (hr < 18 ? 'Good Afternoon' : 'Good Evening');
        greetingEl.textContent = `${greet}, ${user.name}`;
      }
    }catch(e){
      // not logged in -> redirect to login
      window.location.href = '/login';
      return;
    }

    try{
      const res = await apiFetch('/api/tasks','GET');
      const tasks = res.tasks || [];
      taskList.innerHTML = tasks.map(t=>`<div><b>${escapeHtml(t.name)}</b> (${t.start_time||t.start} - ${t.end_time||t.end||''})</div>`).join('');
    }catch(err){
      taskList.innerHTML = '<div class="small-muted">No tasks yet.</div>';
    }
    // load goal summary (we'll set simple text)
    try{
      const g = await apiFetch('/api/user','GET'); // no direct /api/goal get route, but dashboard can show known or static text
      userGoalEl.textContent = 'Your goal is set — view Settings to change.';
    }catch(e){}
    // streak (simple: saved in localStorage for frontend)
    const s = localStorage.getItem('df_streak') || '0';
    streakValEl.textContent = `${s} days`;
  }
  loadDashboard();
}

if(logoutBtn){
  logoutBtn.addEventListener('click', async ()=>{
    await apiFetch('/api/logout','POST');
    window.location.href = '/login';
  });
}

if(document.getElementById('resetBtn')){
  document.getElementById('resetBtn').addEventListener('click', async ()=>{
    if(!confirm('This will clear your tasks and goals for this account. Continue?')) return;
    try{
      await apiFetch('/api/reset_user','POST');
      alert('Data cleared for your account.');
      window.location.href = '/dashboard';
    }catch(e){ alert('Error'); }
  });
}

// small HTML escape
function escapeHtml(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

// Request notification permission once
if("Notification" in window && Notification.permission !== "granted"){
  Notification.requestPermission();
}
