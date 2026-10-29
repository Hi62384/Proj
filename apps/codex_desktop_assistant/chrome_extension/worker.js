// Privileged messages originate only from the native port or our own popup.
// No externally_connectable, window message listener, cookies or debugger API.
const HOST='com.codex.desktop_assistant';const VERSION=1;
let port=null,session=null,connected=false,connectionError='';const grants=new Map(),cancelled=new Set(),running=new Set();
let autoConnect=false,grantAckSupported=false,lastAuthorizationError='';const grantWaiters=new Map();
let nextRule=1;const tabRules=new Map();
const activationEpoch=new Map(),navigationEpoch=new Map();
const networkAvailable=Boolean(chrome.declarativeNetRequest?.getSessionRules);
const startupReady=networkAvailable?chrome.declarativeNetRequest.getSessionRules().then(rules=>chrome.declarativeNetRequest.updateSessionRules({removeRuleIds:rules.map(r=>r.id)})):Promise.resolve();
const consequentialNames=['publish','unpublish','purchase','pay','charge','checkout','delete','remove','send','sendMessage','transfer','refund','withdraw','changePassword','resetPassword'];
async function networkGuard(grant){
  if(!networkAvailable)throw Error('Reload this extension at chrome://extensions to activate its network protection permission, then reconnect and authorize the tab.');
  await startupReady;const previous=tabRules.get(grant.tab)||[];const rules=[];
  if(!grant.manual){
    // Literal filters avoid Chrome's 2 KB compiled-regex budget. '^' is
    // Chrome's separator anchor, so purchase-history is not purchase.
    for(const name of consequentialNames)rules.push({id:nextRule++,priority:100,action:{type:'block'},condition:{tabIds:[grant.tab],urlFilter:'*/'+name+'^'}});
    for(const key of ['action','operation','command','do'])for(const name of ['publish','purchase','delete','send','pay','charge','transfer'])for(const separator of ['?','&'])rules.push({id:nextRule++,priority:100,action:{type:'block'},condition:{tabIds:[grant.tab],urlFilter:'*'+separator+key+'='+name+'^'}});
    if(grant.uploadLocked){
      rules.push({id:nextRule++,priority:1,action:{type:'block'},condition:{tabIds:[grant.tab]}});
      const receiver=new URL(grant.origin),base=receiver.origin;
      rules.push({id:nextRule++,priority:10,action:{type:'allow'},condition:{tabIds:[grant.tab],urlFilter:'|'+base+'/'}});
    }
  }
  await chrome.declarativeNetRequest.updateSessionRules({removeRuleIds:previous,addRules:rules});tabRules.set(grant.tab,rules.map(r=>r.id));
}
function exact(url){const p=new URL(url);if(!['http:','https:'].includes(p.protocol)||p.username||p.password)throw Error('Only HTTP(S) sites without embedded credentials are supported');return `${p.protocol}//${p.hostname}:${p.port||(p.protocol==='https:'?'443':'80')}`;}
function publicUrl(url){const p=new URL(url);return p.origin+p.pathname;}
function frameOrigin(frame,frames,depth=0){
  if(!frame||depth>8)return null;
  if(/^https?:/.test(frame.url))return exact(frame.url);
  if(/^about:(?:blank|srcdoc)$/.test(frame.url))return frameOrigin(frames.find(f=>f.frameId===frame.parentFrameId),frames,depth+1);
  return null;
}
function post(value){if(!port||!session)throw Error('Assistant is disconnected');port.postMessage({...value,session});}
async function badge(tabId,text){try{await chrome.action.setBadgeText({tabId,text});await chrome.action.setBadgeBackgroundColor({tabId,color:text==='STOP'?'#b91c1c':'#0f766e'});}catch{}}
async function revoke(tab,notify=true){grants.delete(tab);const rules=tabRules.get(tab)||[];tabRules.delete(tab);try{await chrome.declarativeNetRequest.updateSessionRules({removeRuleIds:rules});}catch{}await badge(tab,'');try{await chrome.tabs.sendMessage(tab,{channel:'codex-content',operation:'revoke'});}catch{}if(notify&&connected)post({type:'event',event:'revoke',tab});}
function disconnect(){const old=port;port=null;session=null;connected=false;grantAckSupported=false;for(const waiter of grantWaiters.values())waiter.reject(Error('Assistant disconnected before confirming tab access.'));grantWaiters.clear();for(const tab of [...grants.keys()])revoke(tab,false);try{old?.disconnect();}catch{} }
async function confirmGrant(grant){
  if(!grantAckSupported)throw Error('Restart the updated Desktop Assistant, then reconnect. It must confirm tab access before automation is authorized.');
  await new Promise((resolve,reject)=>{
    const key=grant.tab+':'+grant.origin;const timer=setTimeout(()=>{grantWaiters.delete(key);reject(Error('The assistant did not confirm this tab grant. No automation access was enabled.'));},5000);
    grantWaiters.set(key,{resolve:()=>{clearTimeout(timer);resolve();},reject:error=>{clearTimeout(timer);reject(error);}});
    try{post({type:'event',event:'grant',tab:grant});}catch(error){clearTimeout(timer);grantWaiters.delete(key);reject(error);}
  });
}
function connect(){
  if(port)return;port=chrome.runtime.connectNative(HOST);
  port.onMessage.addListener(message=>{
    if(message.type==='hello'&&message.version===VERSION&&typeof message.session==='string'){
      session=message.session;connected=true;connectionError='';grantAckSupported=message.features?.includes('grant_ack')===true;grants.clear();return;
    }
    if(message.type==='error'){disconnect();return;}
    if(!connected||message.session!==session)return;
    if(message.type==='grant_ack'){const key=message.tab+':'+message.origin;grantWaiters.get(key)?.resolve();grantWaiters.delete(key);return;}
    if(message.type==='revoke_all'){for(const tab of [...grants.keys()])revoke(tab,false);return;}
    if(message.type==='cancel'){if(running.has(message.id))cancelled.add(message.id);return;}
    if(message.type==='request')handle(message);
  });
  port.onDisconnect.addListener(()=>{connectionError=chrome.runtime.lastError?.message||'Assistant connection ended. Reconnect and reauthorize tabs.';disconnect();});
  port.postMessage({type:'hello',version:VERSION});
}
async function active(){const [tab]=await chrome.tabs.query({active:true,currentWindow:true});if(!tab)throw Error('No active Chrome tab');return tab;}
async function authorize(target=null){
  if(!connected)throw Error('Connect to the open Desktop Assistant first.');
  const tab=target||await active(),origin=exact(tab.url);await chrome.scripting.executeScript({target:{tabId:tab.id},files:['content.js']});
  const grant={tab:tab.id,window:tab.windowId,origin,manual:false,frames:{'0':origin}};
  try{
    await networkGuard(grant);
    const response=await chrome.tabs.sendMessage(tab.id,{channel:'codex-content',operation:'grant',origin,session});
    if(!response?.ok)throw Error(response?.error||'The page did not confirm its content controller.');
    await confirmGrant(grant);grants.set(tab.id,grant);lastAuthorizationError='';await badge(tab.id,'ON');return grant;
  }catch(error){lastAuthorizationError=error.message;await revoke(tab.id);throw error;}
}
async function requireTab(args,allowManual=false){
  const grant=grants.get(args.tab);if(!grant)throw Error('Authorize this exact tab using the extension popup.');
  const tab=await chrome.tabs.get(args.tab);if(exact(tab.url)!==grant.origin){await revoke(tab.id);throw Error('Site changed. Authorize the new site in the extension.');}
  if(grant.manual&&!allowManual)throw Error('Manual Control is active for this tab.');
  return {tab,grant};
}
async function content(args,operation){
  const {grant}=await requireTab(args);const frame=Number.isInteger(args.frame)?args.frame:0;
  const frames=await chrome.webNavigation.getAllFrames({tabId:args.tab});const target=frames.find(x=>x.frameId===frame);
  const expected=frame===0?grant.origin:grant.frames?.[String(frame)];
  if(!target||!expected||frameOrigin(target,frames)!==expected)throw Error('Authorize this embedded frame site in the extension popup first.');
  try{return await chrome.tabs.sendMessage(args.tab,{...args,channel:'codex-content',operation,session},{frameId:frame});}
  catch(error){
    if(!['inspect','screenshot_check'].includes(operation))throw Error('Page connection changed; no action was replayed. Inspect again.');
    await chrome.scripting.executeScript({target:{tabId:args.tab,frameIds:[frame]},files:['content.js']});
    await chrome.tabs.sendMessage(args.tab,{channel:'codex-content',operation:'grant',origin:expected,session},{frameId:frame});
    return await chrome.tabs.sendMessage(args.tab,{...args,channel:'codex-content',operation,session},{frameId:frame});
  }
}
async function execute(operation,args,check){
  check();
  if(operation==='list_tabs'){
    const tabs=await chrome.tabs.query({});return {tabs:tabs.map(t=>{const g=grants.get(t.id);return g?{tab:t.id,window:t.windowId,active:t.active,authorized:true,origin:g.origin,manual:g.manual,title:'Authorized tab',url:publicUrl(t.url)}:{tab:t.id,window:t.windowId,active:t.active,authorized:false};})};
  }
  if(operation==='list_windows'){const windows=await chrome.windows.getAll();return {windows:windows.map(w=>({window:w.id,focused:w.focused,type:w.type}))};}
  if(operation==='manual'){
    const {grant}=await requireTab(args,true);grant.manual=Boolean(args.enabled);
    await networkGuard(grant);
    await chrome.tabs.sendMessage(args.tab,{channel:'codex-content',operation:'manual',enabled:grant.manual});
    await badge(args.tab,grant.manual?'HUMAN':'ON');post({type:'event',event:'manual',tab:args.tab,enabled:grant.manual});return {manual:grant.manual};
  }
  if(operation==='release'){await revoke(args.tab);return {released:true};}
  if(operation==='open_tab'){
    const site=exact(args.url),url=new URL(args.url);
    const created=await chrome.tabs.create({url:'about:blank',active:false});
    try{
      await networkGuard({tab:created.id,origin:site,manual:false});check();
      await chrome.tabs.update(created.id,{url:args.url});
      const permitted=await chrome.permissions.contains({origins:[`${url.protocol}//${url.hostname}/*`]});
      if(permitted){
        for(let n=0;n<80;n++){
          check();const current=await chrome.tabs.get(created.id);
          if(current.status==='complete'){
            if(exact(current.url)!==site)break;
            await authorize(current);return {tab:created.id,authorized:true,foreground_changed:false};
          }
          await new Promise(resolve=>setTimeout(resolve,100));
        }
      }
      // No automation controller exists on this tab. Do not leave network
      // restrictions behind when handing the newly opened page to its owner.
      await revoke(created.id,false);
      return {tab:created.id,authorized:false,authorization_required:true,foreground_changed:false};
    }catch(error){await revoke(created.id);throw error;}
  }
  const {tab,grant}=await requireTab(args,operation==='show');check();
  if(operation==='show'){await chrome.tabs.update(tab.id,{active:true});await chrome.windows.update(tab.windowId,{focused:true});return {shown:true};}
  if(operation==='frames'){
    const frames=await chrome.webNavigation.getAllFrames({tabId:tab.id});
    for(const frame of frames)if(frameOrigin(frame,frames)===grant.origin)grant.frames[String(frame.frameId)]=grant.origin;
    post({type:'event',event:'grant',tab:grant});
    return {frames:frames.map(f=>{const same=frameOrigin(f,frames)===(f.frameId===0?grant.origin:grant.frames?.[String(f.frameId)]);return {frame:f.frameId,parent:f.parentFrameId,authorized:same,url:same?(/^https?:/.test(f.url)?publicUrl(f.url):'about:blank'): 'Another site — authorization required'};})};
  }
  if(operation==='navigate'){
    if(exact(args.url)!==grant.origin)throw Error('Open and authorize the destination site in Chrome before navigating to it.');
    await chrome.tabs.update(tab.id,{url:args.url});return {navigation_started:true,tab:tab.id};
  }
  if(operation==='close_check'){
    const frames=await chrome.webNavigation.getAllFrames({tabId:tab.id});
    let may_lose_edits=frames.some(f=>f.frameId!==0);
    const response=await content(args,'close_check');
    if(!response?.ok)throw Error(response?.error||'Could not check unsaved edits');
    grant.closeToken=crypto.randomUUID();grant.closeState=JSON.stringify(response.result);
    return {may_lose_edits:may_lose_edits||response.result.may_lose_edits,close_token:grant.closeToken};
  }
  if(operation==='close_tab'){
    const response=await content(args,'close_check');
    if(!response?.ok||!args.close_token||args.close_token!==grant.closeToken||JSON.stringify(response.result)!==grant.closeState)throw Error('Tab changed before closing. Check it again.');
    delete grant.closeToken;await chrome.tabs.remove(tab.id);return {closed:true};
  }
  if(operation==='back'){await chrome.tabs.goBack(tab.id);return {navigation_started:true};}
  if(operation==='forward'){await chrome.tabs.goForward(tab.id);return {navigation_started:true};}
  if(operation==='reload'){await chrome.tabs.reload(tab.id);return {navigation_started:true};}
  if(operation==='observe'){
    if(!tab.active)throw Error('Background screenshots are unavailable. Use DOM inspection, or explicitly Show Tab first.');
    const frames=await chrome.webNavigation.getAllFrames({tabId:tab.id});
    for(const frame of frames){
      const site=frameOrigin(frame,frames);
      if(site!==grant.origin&&args.allowed_frames?.[String(frame.frameId)]!==site)throw Error('Screenshot withheld: authorize and inspect the embedded frame site first, or use DOM inspection.');
      if(site===grant.origin)grant.frames[String(frame.frameId)]=site;
      const checked=await content({...args,frame:frame.frameId},'screenshot_check');if(!checked.ok)throw Error(checked.error);
    }
    const focused=await chrome.windows.get(tab.windowId);if(!focused.focused)throw Error('Screenshot needs the explicitly shown Chrome window. DOM inspection works in the background.');
    const activeBefore=await chrome.tabs.get(tab.id);if(!activeBefore.active)throw Error('Active tab changed; screenshot discarded.');
    const activation=activationEpoch.get(tab.windowId)||0,navigation=navigationEpoch.get(tab.id)||0;
    const image=await chrome.tabs.captureVisibleTab(tab.windowId,{format:'png'});
    const after=await chrome.tabs.get(tab.id);
    if(!after.active||exact(after.url)!==grant.origin||(activationEpoch.get(tab.windowId)||0)!==activation||(navigationEpoch.get(tab.id)||0)!==navigation)throw Error('Tab or navigation changed during capture; screenshot discarded.');
    const bitmap=await createImageBitmap(await(await fetch(image)).blob());let scale=Math.min(1,1440/bitmap.width,1000/bitmap.height),bytes;
    do{const canvas=new OffscreenCanvas(Math.max(1,Math.round(bitmap.width*scale)),Math.max(1,Math.round(bitmap.height*scale)));canvas.getContext('2d').drawImage(bitmap,0,0,canvas.width,canvas.height);bytes=new Uint8Array(await(await canvas.convertToBlob({type:'image/jpeg',quality:.75})).arrayBuffer());scale*=.75;}while(bytes.length>500000&&scale>.15);
    bitmap.close();if(bytes.length>500000)throw Error('Screenshot exceeds the safe transport bound; use DOM inspection.');
    let binary='';for(let i=0;i<bytes.length;i+=32768)binary+=String.fromCharCode(...bytes.subarray(i,i+32768));
    return {image:'data:image/jpeg;base64,'+btoa(binary)};
  }
  if(operation==='download'){
    if(!await chrome.permissions.contains({permissions:['downloads']}))throw Error('Enable Download Save Dialogs in the extension popup first.');
    if(exact(args.url)!==grant.origin)throw Error('Download destination site is not authorized.');
    const id=await chrome.downloads.download({url:args.url,saveAs:true});return {download:id,owner_save_dialog:true};
  }
  const supported=['inspect','context','action','upload_begin','upload_chunk','upload_finish'];
  if(!supported.includes(operation))throw Error('Unsupported bounded Chrome operation');
  if(operation==='upload_begin'){grant.uploadLocked=true;await networkGuard(grant);}
  let temporaryRule=null;
  if(operation==='action'&&args.owner_reviewed===true&&args.reviewed_form_url){
    if(exact(args.reviewed_form_url)!==grant.origin)throw Error('Reviewed form destination is not this authorized site.');
    temporaryRule=nextRule++;
    await chrome.declarativeNetRequest.updateSessionRules({addRules:[{id:temporaryRule,priority:200,action:{type:'allow'},condition:{tabIds:[tab.id],urlFilter:'|'+args.reviewed_form_url+'|',requestMethods:[String(args.reviewed_form_method||'POST').toLowerCase()]}}]});
    // A bounded allowance for the explicitly reviewed form, never a blanket
    // permission for opaque JavaScript endpoints or another website.
    setTimeout(()=>chrome.declarativeNetRequest.updateSessionRules({removeRuleIds:[temporaryRule]}).catch(()=>{}),2000);
  }
  const result=await content(args,operation);if(!result?.ok)throw Error(result?.error||'Content operation failed');return result.result;
}
async function handle(message){
  const id=message.id;if(typeof id!=='string'||id.length>80||running.has(id)||message.version!==VERSION)return;
  running.add(id);const startedSession=session;const args=message.arguments;
  const check=()=>{if(!connected||session!==startedSession||cancelled.has(id)||Date.now()/1000>message.deadline)throw Error('Operation cancelled or expired; inspect before continuing.');};
  try{
    if(!args||typeof args!=='object'||Array.isArray(args)||typeof message.deadline!=='number')throw Error('Invalid command');
    if(Number.isInteger(args.tab))await badge(args.tab,'WORK');
    const result=await execute(message.operation,args,check);check();post({type:'response',id,ok:true,result});
  }catch(error){try{post({type:'response',id,ok:false,error:String(error.message).slice(0,500)});}catch{}}
  finally{running.delete(id);cancelled.delete(id);if(grants.has(args?.tab))await badge(args.tab,grants.get(args.tab).manual?'HUMAN':'ON');}
}
chrome.runtime.onMessage.addListener((message,sender,reply)=>{
  if(sender.id!==chrome.runtime.id||!sender.url?.startsWith(chrome.runtime.getURL('popup.html'))||message?.popup!==true)return false;
  (async()=>{
    switch(message.operation){
      case 'status':return {connected,tabs:[...grants.values()],error:connectionError,authorization_error:lastAuthorizationError};
      case 'connect':autoConnect=true;await chrome.storage.local.set({autoConnect:true});connect();return {};
      case 'disconnect':autoConnect=false;await chrome.storage.local.set({autoConnect:false});disconnect();return {};
      case 'authorize':return authorize();
      case 'frame_choices':{
        const tab=await active();await requireTab({tab:tab.id},true);const frames=await chrome.webNavigation.getAllFrames({tabId:tab.id});
        return {frames:frames.filter(f=>f.frameId!==0&&/^https?:\/\//.test(f.url)).map(f=>({frame:f.frameId,origin:exact(f.url),url:publicUrl(f.url)}))};
      }
      case 'authorize_frame':{
        const tab=await active();const {grant}=await requireTab({tab:tab.id},true);const frames=await chrome.webNavigation.getAllFrames({tabId:tab.id});const frame=frames.find(f=>f.frameId===message.frame);
        if(!frame||exact(frame.url)!==message.origin)throw Error('Embedded frame changed; list frames again.');
        await chrome.scripting.executeScript({target:{tabId:tab.id,frameIds:[frame.frameId]},files:['content.js']});
        await chrome.tabs.sendMessage(tab.id,{channel:'codex-content',operation:'grant',origin:message.origin,session},{frameId:frame.frameId});
        grant.frames[String(frame.frameId)]=message.origin;post({type:'event',event:'grant',tab:grant});return {};
      }
      case 'stop':{const tab=await active();await revoke(tab.id);return {};}
      case 'manual':{const tab=await active();return execute('manual',{tab:tab.id,enabled:message.enabled},()=>{});}
      case 'open':{const p=chrome.runtime.connectNative(HOST);p.postMessage({type:'open_assistant',version:VERSION});return {};}
      default:throw Error('Unknown popup action');
    }
  })().then(result=>reply({ok:true,result}),error=>reply({ok:false,error:error.message}));return true;
});
chrome.tabs.onRemoved.addListener(tab=>revoke(tab));
chrome.tabs.onActivated.addListener(info=>activationEpoch.set(info.windowId,(activationEpoch.get(info.windowId)||0)+1));
chrome.tabs.onUpdated.addListener((tab,change)=>{if(change.url&&grants.has(tab)){try{if(exact(change.url)!==grants.get(tab).origin)revoke(tab);}catch{revoke(tab);}}});
chrome.webNavigation.onCommitted.addListener(details=>{
  navigationEpoch.set(details.tabId,(navigationEpoch.get(details.tabId)||0)+1);
  const grant=grants.get(details.tabId);if(!grant)return;
  if(details.frameId===0){grant.frames={'0':grant.origin};post({type:'event',event:'grant',tab:grant});}
  else if(grant.frames?.[String(details.frameId)]){
    let matches=false;try{matches=exact(details.url)===grant.frames[String(details.frameId)];}catch{}
    if(!matches){delete grant.frames[String(details.frameId)];post({type:'event',event:'grant',tab:grant});}
  }
});
chrome.alarms.create('connection-check',{periodInMinutes:.5});
chrome.alarms.onAlarm.addListener(()=>{if(connected)try{post({type:'event',event:'heartbeat'});}catch{disconnect();}else if(autoConnect&&!port)connect();});
chrome.storage.local.get('autoConnect').then(settings=>{autoConnect=settings.autoConnect===true;if(autoConnect)connect();});
