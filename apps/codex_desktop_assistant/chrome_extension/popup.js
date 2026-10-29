const $=id=>document.getElementById(id);
async function send(operation,extra={}){
  const result=await chrome.runtime.sendMessage({popup:true,operation,...extra});
  if(!result?.ok)throw Error(result?.error||'Extension unavailable');return result.result;
}
async function refresh(){
  const state=await send('status');$('status').textContent=state.connected?'Connected to Desktop Assistant':'Disconnected — open Desktop Assistant, then Connect';
  const [tab]=await chrome.tabs.query({active:true,currentWindow:true});const grant=state.tabs.find(x=>x.tab===tab?.id);
  $('target').textContent=grant?`Authorized tab ${grant.tab} · ${grant.origin}`:'This tab is not authorized';
  $('manual').checked=Boolean(grant?.manual);
  $('authorized_count').textContent=`Authorized tabs in this session: ${state.tabs.length}`;
  if(state.error&&!state.connected)$('error').textContent=state.error;
  if(state.authorization_error)$('error').textContent=state.authorization_error;
}
async function guarded(action){try{$('error').textContent='';await action();await refresh();}catch(error){$('error').textContent=error.message;}}
for(const name of ['connect','disconnect','authorize','stop','open'])$(name).onclick=()=>guarded(()=>send(name));
$('manual').onchange=()=>guarded(()=>send('manual',{enabled:$('manual').checked}));
$('site').onclick=()=>guarded(async()=>{
  const [tab]=await chrome.tabs.query({active:true,currentWindow:true});const url=new URL(tab.url);
  if(!['http:','https:'].includes(url.protocol))throw Error('Choose an ordinary HTTP or HTTPS website.');
  const granted=await chrome.permissions.request({origins:[`${url.protocol}//${url.hostname}/*`]});
  if(!granted)throw Error('Chrome site permission was denied.');await send('authorize');
});
$('downloads').onclick=()=>guarded(async()=>{if(!await chrome.permissions.request({permissions:['downloads']}))throw Error('Download permission was denied.');});
$('frames').onclick=()=>guarded(async()=>{
  const result=await send('frame_choices');$('frame').replaceChildren();
  for(const frame of result.frames){const option=document.createElement('option');option.value=JSON.stringify(frame);option.textContent=`Frame ${frame.frame} · ${frame.origin}`;$('frame').appendChild(option);}
});
$('frame_allow').onclick=()=>guarded(async()=>{
  if(!$('frame').value)throw Error('List embedded frames and choose one first.');
  const frame=JSON.parse($('frame').value),url=new URL(frame.url);
  if(!await chrome.permissions.request({origins:[`${url.protocol}//${url.hostname}/*`]}))throw Error('Chrome frame permission was denied.');
  await send('authorize_frame',{frame:frame.frame,origin:frame.origin});
});
refresh().catch(error=>$('error').textContent=error.message);
setInterval(()=>refresh().catch(()=>{}),1000);
