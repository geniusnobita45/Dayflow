// shared frontend logic for all templates (calls Flask API endpoints)

async function apiFetch(path, method='GET', body=null){
  const opts = {method, headers:{'Content-Type':'application/json'}};
  if(body) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  if(res.status === 204) return null;
  const json = await res.json();
  if(!res.ok) throw json;
  return json;
}

function escapeHtml(value){
  return String(value ?? '')
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;')
    .replace(/'/g,'&#039;');
}

function formatGoalType(type){
  const labels = { fitness: 'Fitness / Fat loss', study: 'Study / Exam prep', skill: 'Skill learning', routine: 'Daily discipline' };
  return labels[type] || 'Daily focus';
}

function collectValue(id){
  const el = document.getElementById(id);
  return el ? el.value.trim() : '';
}

const scheduledNotificationIds = new Set();

function minutesUntilToday(time){
  const [hours, minutes] = String(time || '').split(':').map(Number);
  if(Number.isNaN(hours) || Number.isNaN(minutes)) return null;
  const now = new Date();
  const target = new Date();
  target.setHours(hours, minutes, 0, 0);
  return target.getTime() - now.getTime();
}

async function ensureNotificationPermission(){
  if(!('Notification' in window)) return false;
  if(Notification.permission === 'granted') return true;
  if(Notification.permission === 'denied') return false;
  const permission = await Notification.requestPermission();
  return permission === 'granted';
}

async function scheduleBrowserNotifications(reminders){
  if(!Array.isArray(reminders) || !reminders.length) return;
  const allowed = await ensureNotificationPermission();
  if(!allowed) return;

  reminders.forEach((reminder)=>{
    if(!reminder.enabled) return;
    const delay = minutesUntilToday(reminder.remind_time);
    if(delay === null || delay < 0 || delay > 24 * 60 * 60 * 1000) return;
    const key = `${reminder.id}-${reminder.remind_time}`;
    if(scheduledNotificationIds.has(key)) return;
    scheduledNotificationIds.add(key);
    window.setTimeout(()=>{
      new Notification('DayFlow reminder', { body: reminder.title });
    }, delay);
  });
}

// --- Signup page ---
const signupForm = document.getElementById('signupForm');
if(signupForm){
  signupForm.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const name = collectValue('name');
    const email = collectValue('email');
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
    const email = collectValue('loginEmail');
    const password = document.getElementById('loginPassword').value;
    try{
      const out = await apiFetch('/api/login','POST',{email,password});
      if(out.status==='ok') window.location.href = '/dashboard';
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

  async function refreshTasks(){
    try{
      const res = await apiFetch('/api/tasks','GET');
      const tasks = res.tasks || [];
      listEl.innerHTML = tasks.map(t=>`<div><b>${escapeHtml(t.name)}</b> (${escapeHtml(t.start_time || t.start)} - ${escapeHtml(t.end_time || t.end || '')}) [${escapeHtml(t.priority || '')}]</div>`).join('');
    }catch(err){ listEl.innerHTML = '<div class="small-muted">No tasks yet</div>'; }
  }
  refreshTasks();

  manualForm.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const name = collectValue('taskName');
    const start = document.getElementById('startTime').value;
    const end = document.getElementById('endTime').value;
    const priority = document.getElementById('priority').value;
    if(!name||!start||!end){ alert('Enter all fields'); return; }
    try{
      await apiFetch('/api/tasks','POST',{tasks:[{name,start,end,priority,kind:'focus'}]});
      document.getElementById('taskName').value='';
      document.getElementById('startTime').value='';
      document.getElementById('endTime').value='';
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
    const constraints = collectValue('scheduleConstraints');
    const routine = {
      includeBasics: document.getElementById('includeBasics').checked,
      breakfast: collectValue('breakfastTime'),
      lunch: collectValue('lunchTime'),
      dinner: collectValue('dinnerTime'),
      movement: collectValue('movementTime')
    };
    const button = document.getElementById('generateButton');
    const status = document.getElementById('generatorStatus');
    const schedule = document.getElementById('generatedSchedule');
    const clarificationPanel = document.getElementById('clarificationPanel');
    const clarificationQuestions = document.getElementById('clarificationQuestions');
    if(!wake || !sleep){
      status.textContent = 'Enter both your wake and sleep time.';
      status.className = 'generator-status error';
      return;
    }

    button.disabled = true;
    button.textContent = 'Building your day...';
    status.textContent = 'Checking routine, commitments, reminders, and goal work.';
    status.className = 'generator-status';
    schedule.innerHTML = '';
    clarificationPanel.hidden = true;
    clarificationQuestions.innerHTML = '';
    try{
      const result = await apiFetch('/api/generate_schedule','POST',{wake,sleep,constraints,routine});
      schedule.innerHTML = result.tasks.map(t=>`
        <div class="generated-task ${escapeHtml(t.kind || 'focus')}">
          <div>
            <strong>${escapeHtml(t.name)}</strong>
            <span>${escapeHtml(t.start)} - ${escapeHtml(t.end)}</span>
          </div>
          <div class="task-badges">
            <span class="kind-pill">${escapeHtml(t.kind || 'focus')}</span>
            <span class="priority ${escapeHtml(t.priority)}">${escapeHtml(t.priority)}</span>
          </div>
        </div>
      `).join('');
      const engine = result.brain && result.brain.engine ? result.brain.engine : 'DayFlow brain';
      const reminderCount = Array.isArray(result.reminders) ? result.reminders.length : 0;
      status.textContent = `Schedule and ${reminderCount} reminders saved using ${engine}.`;
      status.className = 'generator-status success';
      scheduleBrowserNotifications(result.reminders || []);
    }catch(err){
      if(err.status === 'needs_clarification'){
        clarificationQuestions.innerHTML = (err.questions || []).map(q=>`<li>${escapeHtml(q)}</li>`).join('');
        clarificationPanel.hidden = false;
        status.textContent = err.message || 'I need more detail before generating.';
      }else{
        status.textContent = err.message || 'The brain could not generate a schedule.';
      }
      status.className = 'generator-status error';
    }finally{
      button.disabled = false;
      button.textContent = 'Generate smart schedule';
    }
  });
}

// --- Dashboard page ---
const dashboardPanel = document.querySelector('.dashboard-panel');
const taskList = document.getElementById('taskList');
const greetingEl = document.getElementById('greeting');
const userGoalEl = document.getElementById('userGoal');
const streakValEl = document.getElementById('streakValue');
const logoutBtn = document.getElementById('logoutBtn');

if(dashboardPanel){
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
      window.location.href = '/login';
      return;
    }

    try{
      const res = await apiFetch('/api/tasks','GET');
      const tasks = res.tasks || [];
      if(tasks.length){
        taskList.innerHTML = tasks.map(t=>`
          <div>
            <b>${escapeHtml(t.name)}</b>
            <span class="task-meta">${escapeHtml(t.start_time || t.start)} - ${escapeHtml(t.end_time || t.end || '')} | ${escapeHtml(t.kind || 'focus')}</span>
          </div>
        `).join('');
      }else{
        taskList.innerHTML = `<div class="empty-state"><p>No tasks yet.</p><button class="btn" onclick="location.href='/timetable-choice'">Set up schedule</button></div>`;
      }
    }catch(err){
      taskList.innerHTML = '<div class="small-muted">No tasks yet.</div>';
    }
    try{
      const g = await apiFetch('/api/goal','GET');
      if(g.goal){
        userGoalEl.textContent = `Your goal: ${formatGoalType(g.goal.goal_type)} for ${g.goal.duration} days`;
      }else{
        userGoalEl.innerHTML = `No goal set yet. <a href="/goal-setup">Set one now</a>`;
      }
    }catch(e){}
    const s = localStorage.getItem('df_streak') || '0';
    streakValEl.textContent = `${s} days`;
    loadReminders();
  }
  loadDashboard();
}

if(logoutBtn){
  logoutBtn.addEventListener('click', async ()=>{
    await apiFetch('/api/logout','POST');
    window.location.href = '/login';
  });
}

const reminderForm = document.getElementById('reminderForm');
const reminderList = document.getElementById('reminderList');

async function loadReminders(){
  if(!reminderList) return;
  try{
    const res = await apiFetch('/api/reminders','GET');
    const reminders = res.reminders || [];
    if(!reminders.length){
      reminderList.innerHTML = '<div class="small-muted">No reminders yet.</div>';
      return;
    }
    reminderList.innerHTML = reminders.map(reminder=>`
      <div class="reminder-row ${reminder.enabled ? '' : 'muted-row'}">
        <div>
          <strong>${escapeHtml(reminder.title)}</strong>
          <span>${escapeHtml(reminder.remind_time)}</span>
        </div>
        <div class="reminder-actions">
          <button type="button" data-reminder-toggle="${reminder.id}" data-enabled="${reminder.enabled ? 0 : 1}">${reminder.enabled ? 'Pause' : 'Resume'}</button>
          <button type="button" class="danger-light" data-reminder-delete="${reminder.id}">Delete</button>
        </div>
      </div>
    `).join('');
    scheduleBrowserNotifications(reminders);
  }catch(err){
    reminderList.innerHTML = '<div class="small-muted">Unable to load reminders.</div>';
  }
}

if(reminderForm){
  reminderForm.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const title = collectValue('reminderTitle');
    const remind_time = document.getElementById('reminderTime').value;
    try{
      const result = await apiFetch('/api/reminders','POST',{title,remind_time});
      document.getElementById('reminderTitle').value = '';
      document.getElementById('reminderTime').value = '';
      await loadReminders();
      scheduleBrowserNotifications([result.reminder]);
    }catch(err){ alert(err.message || 'Unable to create reminder'); }
  });
}

if(reminderList){
  reminderList.addEventListener('click', async (event)=>{
    const toggleId = event.target.dataset.reminderToggle;
    const deleteId = event.target.dataset.reminderDelete;
    try{
      if(toggleId){
        await apiFetch('/api/reminders','PUT',{id: toggleId, enabled: Number(event.target.dataset.enabled)});
        await loadReminders();
      }
      if(deleteId){
        await apiFetch('/api/reminders','DELETE',{id: deleteId});
        await loadReminders();
      }
    }catch(err){ alert(err.message || 'Unable to update reminder'); }
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

function mountChatWidget(){
  if(signupForm || loginForm || document.getElementById('dayflowChatWidget')) return;
  document.body.insertAdjacentHTML('beforeend', `
    <div class="chat-widget" id="dayflowChatWidget">
      <button class="chat-toggle" id="chatToggle" type="button" aria-expanded="false">Chat</button>
      <section class="chat-panel" id="chatPanel" hidden>
        <div class="chat-header">
          <strong>DayFlow chat</strong>
          <button type="button" id="chatClose" aria-label="Close chat">x</button>
        </div>
        <div class="chat-log" id="chatLog"></div>
        <form id="chatForm" class="chat-form">
          <input id="chatMessage" maxlength="1000" placeholder="Ask DayFlow" autocomplete="off" required>
          <button type="submit">Send</button>
        </form>
      </section>
    </div>
  `);

  const panel = document.getElementById('chatPanel');
  const toggle = document.getElementById('chatToggle');
  const close = document.getElementById('chatClose');
  const chatForm = document.getElementById('chatForm');
  const chatLog = document.getElementById('chatLog');

  function setOpen(open){
    panel.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
  }
  function appendMessage(role, text){
    const row = document.createElement('div');
    row.className = `chat-message ${role}`;
    row.textContent = text;
    chatLog.appendChild(row);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  toggle.addEventListener('click', ()=>setOpen(panel.hidden));
  close.addEventListener('click', ()=>setOpen(false));
  chatForm.addEventListener('submit', async (event)=>{
    event.preventDefault();
    const input = document.getElementById('chatMessage');
    const message = input.value.trim();
    if(!message) return;
    appendMessage('user', message);
    input.value = '';
    try{
      const result = await apiFetch('/api/chat','POST',{message});
      appendMessage('assistant', result.reply || 'I could not find a reply.');
    }catch(err){
      appendMessage('assistant', err.message || 'Chat is not available right now.');
    }
  });
}

mountChatWidget();
