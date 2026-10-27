'use strict';
const $ = id => document.getElementById(id);
let token = location.hash.slice(1) || sessionStorage.getItem('relay-token') || '';
history.replaceState(null, '', '/');
sessionStorage.setItem('relay-token', token);
let state, selected, currentVersion = '', busy = false;
const el = (tag, text, cls) => { const node = document.createElement(tag); node.textContent = text ?? ''; if(cls)node.className=cls; return node; };
function duration(t) { return t.status+' · '+Math.round(t.elapsed+(t.status==='Running'?(Date.now()/1000-t.started_at):0))+' seconds of execution'; }
function notify(text) { $('notice').textContent=text; }
async function post(path, body={}) {
  const res=await fetch('/api/'+path,{method:'POST',headers:{'Content-Type':'application/json','X-Relay-Token':token},body:JSON.stringify(body)});
  const out=await res.json(); if(!res.ok)throw Error(out.error); return out;
}
async function act(fn) { if(busy)return; busy=true; try{await fn();currentVersion='';await refresh();notify('Saved.');}catch(e){notify(e.message);}finally{busy=false;} }
function button(label, action, enabled=true, danger=false) {const n=el('button',label,danger?'danger':'');n.disabled=!enabled;n.onclick=()=>act(action);return n;}
async function refresh() {
  const res=await fetch('/api/state',{cache:'no-store'}); if(!res.ok)throw Error('Reopen the Windows launcher to authenticate.'); state=await res.json();
  $('runner').textContent=state.running?'Runner on':'Runner stopped'; $('github').textContent=state.connections.github; $('codex').textContent=(state.connections.codex_authentication||'Not tested')+' · '+state.connections.codex;
  $('storage').textContent=state.data_dir; $('privacy').textContent=state.connections.public?'PUBLIC OR UNVERIFIED REPOSITORY — Approve only nonsensitive test tasks. Detailed questions, reports, logs and file paths stay local until you release a reviewed message.':'Private repository verified. Treat Issue content as untrusted; credentials and logs stay local. Only nonsensitive tasks are enabled in this first version.';
  $('identity').textContent=state.owner_id?'Verified owner account ID: '+state.owner_id:'Setup required before starting.';
  if(!state.configured)$('setup').open=true;
  if(state.error)notify(state.error);
  $('execution-block').hidden=!state.execution_block?.explanation;
  $('execution-block').textContent=state.execution_block?.explanation?state.execution_block.explanation+' '+(state.execution_block.action||'')+' After fixing setup, use Test connections to clear this execution block.':'';
  if(state.delivery.uncertain)notify(state.delivery.uncertain+' GitHub comment delivery outcome(s) uncertain. Inspect the Issue before manually reposting; automatic retries are disabled.');
  const list=$('tasks');list.replaceChildren();
  const tasks=state.tasks.filter(t=>!$('filter').value||t.status===$('filter').value);
  tasks.forEach(t=>{const b=el('button','', 'task'+(selected===t.id?' chosen':''));b.append(el('b',t.title),el('span',t.status,'badge'),el('small','  #'+t.issue+' · '+t.id));b.onclick=()=>{selected=t.id;currentVersion='';refresh().catch(e=>notify(e.message));};list.append(b);});
  if(!tasks.length)list.append(el('p','No tasks in this view. Start the runner to check GitHub.','muted'));
  const task=state.tasks.find(t=>t.id===selected);if(task){const version=JSON.stringify(task);if(currentVersion!==version){currentVersion=version;await show(task);}else if($('duration'))$('duration').textContent=duration(task);}
}
async function show(t) {
  const panel=$('selected');panel.replaceChildren();const timeLabel=el('p',duration(t),'muted');timeLabel.id='duration';panel.append(el('h2',t.title),timeLabel);
  const link=el('a','Open GitHub Issue ↗');link.href='https://github.com/'+state.repository+'/issues/'+t.issue;link.target='_blank';link.rel='noopener noreferrer';panel.append(link);
  panel.append(el('h3','Instructions and exact file scope'),el('pre',JSON.stringify(t.payload,null,2)));
  if(t.blocked)panel.append(el('p',t.blocked,'warning'));
  const ack=el('label');const check=el('input');check.type='checkbox';ack.append(check,document.createTextNode('I reviewed this exact scope. It is a harmless, nonsensitive task safe for public Issues.'));
  if(t.status==='Proposed')panel.append(ack);
  const controls=el('div','','actions');
  controls.append(button('Approve',()=>post('approve',{task_id:t.id,public_test:check.checked}),t.status==='Proposed'),
    button('Reject',()=>post('control',{task_id:t.id,action:'reject'}),t.status==='Proposed'),
    button('Pause',()=>post('control',{task_id:t.id,action:'pause'}),t.approved&& !['Completed','Cancelled'].includes(t.status)),
    button('Resume',()=>post('control',{task_id:t.id,action:'resume'}),t.approved&&['Needs Owner','Needs ChatGPT','Awaiting Review','Failed'].includes(t.status)),
    button('Cancel',()=>post('control',{task_id:t.id,action:'cancel'}),t.approved&&!['Completed','Cancelled'].includes(t.status),true),
    button('Reset failed session',()=>post('control',{task_id:t.id,action:'reset-session'}),t.approved&&t.status==='Failed'),
    button('Mark reviewed / Completed',()=>post('control',{task_id:t.id,action:'complete'}),t.status==='Awaiting Review'));
  panel.append(controls);
  if(t.thread_id)panel.append(el('p','Codex thread (local): '+t.thread_id,'muted'));
  if(t.pending_reply)panel.append(el('h3','Reply awaiting local review'),el('pre',t.pending_reply));
  if(t.latest_message)panel.append(el('h3','Codex latest message (local)'),el('pre',t.latest_message));
  if(t.question)panel.append(el('h3','Question (local until released)'),el('pre',t.question));
  if(t.report)panel.append(el('h3','Completion report (local)'),el('pre',t.report));
  panel.append(el('h3','Files changed'),el('pre',t.files_changed.join('\n')||'None recorded'),el('h3','Verified relay checks'),el('pre',t.test_results.join('\n')||'No checks recorded'));
  if(t.model_test_claims)panel.append(el('h3','Model-reported tests (verify before accepting)'),el('pre',t.model_test_claims.join('\n')||'None'));
  if(t.approved&&['Needs Owner','Needs ChatGPT','Awaiting Review','Failed'].includes(t.status)){
    const local=el('details');local.append(el('summary','Answer or correct this task locally'));
    local.append(el('p','This stays local and resumes the saved thread within its existing approved file scope. External actions and expanded permissions remain unavailable.'));
    const answer=el('textarea');answer.maxLength=8000;answer.placeholder='Technical answer or correction within the approved scope';answer.setAttribute('aria-label','Local owner reply');local.append(answer);
    const label=el('label'),review=el('input');review.type='checkbox';label.append(review,document.createTextNode('I reviewed this reply and it stays within the approved scope.'));local.append(label);
    local.append(button('Send local reply / resume',()=>post('reply',{task_id:t.id,text:answer.value,scope_reviewed:review.checked})));panel.append(local);
  }
  if(t.approved){
    const details=el('details');details.append(el('summary','Release a reviewed question or report to GitHub'));
    details.append(el('p','This text will be posted as an Issue comment. Write a concise, nonsensitive message. Remove code, logs, local paths, credentials and business details. Publication requires this separate local review.'));
    const area=el('textarea');area.placeholder='Type the exact message safe to publish';area.maxLength=4000;area.setAttribute('aria-label','Exact public message');details.append(area);
    const label=el('label'), reviewed=el('input');reviewed.type='checkbox';label.append(reviewed,document.createTextNode('I reviewed this exact text and approve publishing it to the repository.'));details.append(label);
    details.append(button('Queue this reviewed comment',()=>post('publish',{task_id:t.id,text:area.value,reviewed:reviewed.checked})));panel.append(details);
  }
  panel.append(el('h3','Communication and approval history'));
  const history=await (await fetch('/api/history/'+encodeURIComponent(t.id))).json();
  history.forEach(h=>{const row=el('div','','history');row.append(el('b',h.kind+' '),el('time',new Date(h.at*1000).toLocaleString()),el('pre',h.text));panel.append(row);});
}
$('filter').onchange=()=>refresh().catch(e=>notify(e.message));
$('load-diagnostics').onclick=()=>act(async()=>{const response=await fetch('/api/diagnostics',{cache:'no-store'});if(!response.ok)throw Error('Authentication required');$('diagnostics').textContent=JSON.stringify(await response.json(),null,2);});
$('test').onclick=()=>act(async()=>{notify('Testing GitHub sign-in and Codex OS sandbox; no AI turn will be launched.');await post('test');});
$('start').onclick=()=>act(()=>post('start'));$('stop').onclick=()=>act(()=>post('stop'));
$('save').onclick=()=>act(async()=>{const ids=$('trusted').value.trim();const trusted=ids?ids.split(',').map(x=>Number(x.trim())):[];if(trusted.some(n=>!Number.isSafeInteger(n)||n<=0))throw Error('Enter numeric GitHub account IDs.');await post('setup',{token:$('token').value,trusted_ids:trusted});$('token').value='';});
(async()=>{try{await post('session');await refresh();$('trusted').value=state.trusted_ids.join(', ');notify('Ready. New tasks always require local approval.');setInterval(()=>{if(!busy)refresh().catch(e=>notify(e.message));},4000);}catch(e){notify(e.message);}})();
