// Privileged messages originate only from the native port or our own popup.
// No externally_connectable, window message listener, cookies or debugger API.
const HOST='com.codex.desktop_assistant';const VERSION=1;
let port=null,session=null,connected=false,connectionError='';const grants=new Map(),cancelled=new Set(),running=new Set();
let autoConnect=false,grantAckSupported=false,lastAuthorizationError='';const grantWaiters=new Map();
let fullBrowser=false,trustedInput=false;
const approvedSites=new Set();
const wideOrigins=['http://*/*','https://*/*'];
async function browserScope(){fullBrowser=fullBrowser&&await chrome.permissions.contains({origins:wideOrigins});return fullBrowser;}
function scopeEvent(){if(connected)post({type:'event',event:'scope',full_browser:fullBrowser,trusted_input:trustedInput});}
const patternFor=url=>{const p=new URL(url);return `${p.protocol}//${p.hostname}/*`;};
async function siteAllowed(url){return await browserScope()||(approvedSites.has(exact(url))&&await chrome.permissions.contains({origins:[patternFor(url)]}));}
let nextRule=1;const tabRules=new Map();
// Session-local provenance, never supplied by a model or webpage. Only tabs
// actually created here and never activated/edited qualify for clean close.
const createdTabs=new Map();
const openingUrls=new Map();
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
      for(const receiver of grant.uploadReceivers||[])rules.push({id:nextRule++,priority:10,action:{type:'allow'},condition:{tabIds:[grant.tab],urlFilter:'|'+receiver+'|',requestMethods:['post']}});
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
async function revoke(tab,notify=true){grants.delete(tab);createdTabs.delete(tab);const rules=tabRules.get(tab)||[];tabRules.delete(tab);try{await chrome.declarativeNetRequest.updateSessionRules({removeRuleIds:rules});}catch{}await badge(tab,'');try{await chrome.tabs.sendMessage(tab,{channel:'codex-content',operation:'revoke'});}catch{}if(notify&&connected)post({type:'event',event:'revoke',tab});}
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
      session=message.session;connected=true;connectionError='';grantAckSupported=message.features?.includes('grant_ack')===true;grants.clear();browserScope().then(scopeEvent);return;
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
async function authorize(target=null,sourceScope='auto'){
  if(!connected)throw Error('Connect to the open Desktop Assistant first.');
  let tab=target||await active();const origin=exact(tab.url);
  // Restored/discarded tabs have no live document to inject into. Wake only
  // that existing tab, without activation or creating a duplicate.
  if(tab.discarded){
    await chrome.tabs.reload(tab.id);
    for(let n=0;n<100;n++){
      tab=await chrome.tabs.get(tab.id);
      if(!tab.discarded&&tab.status==='complete')break;
      await new Promise(resolve=>setTimeout(resolve,100));
    }
    if(tab.discarded||tab.status!=='complete')throw Error('Existing discarded tab has not finished reloading.');
    if(exact(tab.url)!==origin)throw Error('Existing tab changed site while waking; inspect its destination first.');
  }
  await chrome.scripting.executeScript({target:{tabId:tab.id},files:['content.js']});
  const previous=grants.get(tab.id);
  const grant={tab:tab.id,window:tab.windowId,origin,manual:false,scope:sourceScope==='auto'?(await browserScope()?'full':'site'):sourceScope,assistant_created:createdTabs.get(tab.id)?.session===session,frames:{'0':origin},uploadLocked:Boolean(previous?.origin===origin&&previous.uploadLocked),uploadReceivers:previous?.origin===origin?(previous.uploadReceivers||[]):[]};
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
    const tabs=await chrome.tabs.query({});return {full_browser:await browserScope(),tabs:tabs.map(t=>{const g=grants.get(t.id);return g?{tab:t.id,window:t.windowId,active:t.active,authorized:true,origin:g.origin,manual:g.manual,assistant_created:g.assistant_created,title:String(t.title||'Authorized page').slice(0,200),url:publicUrl(t.url)}:{tab:t.id,window:t.windowId,active:t.active,authorized:false};})};
  }
  if(operation==='find_tabs'){
    if(!await browserScope())throw Error('Full Browser Access is required for existing-tab title/URL matching. Restricted mode exposes authorized tabs only.');
    const query=String(args.query||'').toLowerCase();if(query.length<3||query.length>100)throw Error('Use a specific tab reference.');
    const tabs=await chrome.tabs.query({});return {tabs:tabs.filter(t=>/^https?:/.test(t.url||'')&&((t.title||'')+' '+publicUrl(t.url)).toLowerCase().includes(query)).slice(0,10).map(t=>({tab:t.id,title:String(t.title||'').slice(0,200),url:publicUrl(t.url),window:t.windowId,discarded:Boolean(t.discarded),status:t.status}))};
  }
  if(operation==='adopt_tab'){
    if(!await browserScope())throw Error('Existing tabs require a popup tab grant in Restricted mode.');
    const target=await chrome.tabs.get(args.tab);exact(target.url);await authorize(target);return {tab:target.id,authorized:true};
  }
  if(operation==='list_windows'){const windows=await chrome.windows.getAll();return {windows:windows.map(w=>({window:w.id,focused:w.focused,type:w.type}))};}
  if(operation==='manual'){
    const {grant}=await requireTab(args,true);grant.manual=Boolean(args.enabled);
    if(createdTabs.has(args.tab))createdTabs.get(args.tab).visited=true;
    await networkGuard(grant);
    await chrome.tabs.sendMessage(args.tab,{channel:'codex-content',operation:'manual',enabled:grant.manual});
    await badge(args.tab,grant.manual?'HUMAN':'ON');post({type:'event',event:'manual',tab:args.tab,enabled:grant.manual});return {manual:grant.manual};
  }
  if(operation==='release'){await revoke(args.tab);return {released:true};}
  if(operation==='open_tab'){
    const site=exact(args.url),url=new URL(args.url),key=url.href;
    // An exact requested URL is a bounded target reference, not permission to
    // enumerate or inspect unrelated personal tabs. Preserve its live document,
    // unsaved edits, foreground state and original creation provenance.
    if(openingUrls.has(key))return await openingUrls.get(key);
    const opening=(async()=>{
    const matches=(await chrome.tabs.query({})).filter(t=>{
      try{return new URL(t.url).href===key;}catch{return false;}
    }).sort((a,b)=>Number(Boolean(grants.get(b.id)))-Number(Boolean(grants.get(a.id)))||Number(a.active)-Number(b.active)||a.id-b.id);
    if(matches.length){
      const existing=matches[0],grant=grants.get(existing.id);
      if(grant?.manual)throw Error('This existing tab is under manual control. Release manual control before automating it.');
      const permitted=Boolean(grant)||await siteAllowed(args.url);
      if(permitted){check();if(!grant)await authorize(existing);return {tab:existing.id,authorized:true,reused:true,created:false,foreground_changed:false};}
      return {tab:existing.id,authorized:false,reused:true,created:false,authorization_required:true,foreground_changed:false};
    }
    const created=await chrome.tabs.create({url:'about:blank',active:false});
    createdTabs.set(created.id,{session,visited:false,edited:false});
    try{
      await networkGuard({tab:created.id,origin:site,manual:false});check();
      await chrome.tabs.update(created.id,{url:args.url});
      const permitted=await siteAllowed(args.url);
      if(permitted){
        for(let n=0;n<80;n++){
          check();const current=await chrome.tabs.get(created.id);
          if(current.status==='complete'){
            if(exact(current.url)!==site&&!await browserScope())break;
            await authorize(current);return {tab:created.id,authorized:true,reused:false,created:true,foreground_changed:false};
          }
          await new Promise(resolve=>setTimeout(resolve,100));
        }
      }
      // No automation controller exists on this tab. Do not leave network
      // restrictions behind when handing the newly opened page to its owner.
      await revoke(created.id,false);
      return {tab:created.id,authorized:false,reused:false,created:true,authorization_required:true,foreground_changed:false};
    }catch(error){await revoke(created.id);throw error;}
    })();
    openingUrls.set(key,opening);
    try{return await opening;}finally{if(openingUrls.get(key)===opening)openingUrls.delete(key);}
  }
  const {tab,grant}=await requireTab(args,operation==='show');check();
  if(operation==='show'){await chrome.tabs.update(tab.id,{active:true});await chrome.windows.update(tab.windowId,{focused:true});return {shown:true};}
  if(operation==='frames'){
    const frames=await chrome.webNavigation.getAllFrames({tabId:tab.id});
    for(const frame of frames){const site=frameOrigin(frame,frames);if(site&&(site===grant.origin||(grant.assistant_created&&await browserScope())))grant.frames[String(frame.frameId)]=site;}
    post({type:'event',event:'grant',tab:grant});
    return {frames:frames.map(f=>{const same=frameOrigin(f,frames)===(f.frameId===0?grant.origin:grant.frames?.[String(f.frameId)]);return {frame:f.frameId,parent:f.parentFrameId,authorized:same,url:same?(/^https?:/.test(f.url)?publicUrl(f.url):'about:blank'): 'Another site — authorization required'};})};
  }
  if(operation==='navigate'){
    if(exact(args.url)!==grant.origin)throw Error('Open and authorize the destination site in Chrome before navigating to it.');
    await chrome.tabs.update(tab.id,{url:args.url});return {navigation_started:true,tab:tab.id};
  }
  if(operation==='close_check'){
    const frames=await chrome.webNavigation.getAllFrames({tabId:tab.id});
    const own=createdTabs.get(tab.id),untouched=Boolean(own&&own.session===session&&!own.visited&&!own.edited&&!tab.active);
    let may_lose_edits=!untouched&&frames.some(f=>f.frameId!==0);
    const response=await content(args,'close_check');
    if(!response?.ok)throw Error(response?.error||'Could not check unsaved edits');
    grant.closeToken=crypto.randomUUID();grant.closeState=JSON.stringify({page:response.result,untouched,navigation:navigationEpoch.get(tab.id)||0});
    return {may_lose_edits:may_lose_edits||(!untouched&&response.result.may_lose_edits),close_token:grant.closeToken};
  }
  if(operation==='close_tab'){
    const response=await content(args,'close_check');
    const own=createdTabs.get(tab.id),current=await chrome.tabs.get(tab.id),untouched=Boolean(own&&own.session===session&&!own.visited&&!own.edited&&!current.active);
    const proof=JSON.stringify({page:response?.result,untouched,navigation:navigationEpoch.get(tab.id)||0});
    if(!response?.ok||!args.close_token||args.close_token!==grant.closeToken||proof!==grant.closeState)throw Error('Tab changed before closing. Check it again.');
    delete grant.closeToken;await chrome.tabs.remove(tab.id);return {closed:true};
  }
  if(operation==='back'){await chrome.tabs.goBack(tab.id);return {navigation_started:true};}
  if(operation==='forward'){await chrome.tabs.goForward(tab.id);return {navigation_started:true};}
  if(operation==='reload'){await chrome.tabs.reload(tab.id);return {navigation_started:true};}
  if(operation==='observe_check'){
    if(!tab.active)throw Error('Background screenshots are unavailable. Use DOM inspection.');
    const window=await chrome.windows.get(tab.windowId);if(!window.focused)throw Error('Chrome is not foregrounded. Use background DOM inspection.');
    return {available:true,pixels_returned:false};
  }
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
  if(operation==='asset_digest'){
    const response=await content(args,'asset_context');if(!response?.ok)throw Error(response?.error||'Saved asset unavailable');
    const source=response.result,sourceUrl=new URL(source.url);
    // Only the observed Payhip owner-download route may redirect to its exact
    // known storage origin. Signed locations remain inside Chrome, never logs.
    const ownerDownload=source.kind==='delivery'&&sourceUrl.origin==='https://payhip.com'&&/^\/product\/download\/[A-Za-z0-9]+$/.test(sourceUrl.pathname)&&!sourceUrl.search;
    let res=await fetch(source.url,{credentials:'include',redirect:ownerDownload?'follow':'error',signal:AbortSignal.timeout(10000)});
    if(ownerDownload&&!['https://payhip.com','https://pe56d.s3.amazonaws.com'].includes(new URL(res.url).origin)){await res.body?.cancel();throw Error('Owner download redirected outside the supported storage scope.');}
    if(!res.ok)throw Error('Saved asset could not be read.');
    if(ownerDownload&&res.headers.get('content-type')?.includes('json')){
      const info=await res.json();
      // Owner downloads can return a JSON storage link instead of redirecting.
      // Consume only one observed exact-bucket link; keep signed URLs private.
      const links=Object.values(info||{}).filter(value=>{
        if(typeof value!=='string')return false;
        try{const u=new URL(value);return u.origin==='https://pe56d.s3.amazonaws.com'&&!u.username&&!u.password;}catch{return false;}
      });
      if(links.length!==1)throw Error('Owner download JSON has no unique supported storage link; fields: '+Object.keys(info||{}).join(',').slice(0,200));
      res=await fetch(links[0],{credentials:'omit',redirect:'error',signal:AbortSignal.timeout(10000)});
      if(!res.ok)throw Error('Observed owner storage download failed with HTTP '+res.status);
    }
    const reader=res.body.getReader(),chunks=[];let length=0;
    while(true){const part=await reader.read();if(part.done)break;length+=part.value.length;if(length>25*1024*1024){await reader.cancel();throw Error('Saved asset exceeds verification limit.');}chunks.push(part.value);}
    let blob=new Blob(chunks,{type:res.headers.get('content-type')||'application/octet-stream'}),bytes=await blob.arrayBuffer();
    if(ownerDownload&&length<8192&&!(new Uint8Array(bytes)[0]===80&&new Uint8Array(bytes)[1]===75)){
      const text=new TextDecoder().decode(bytes).trim();let info;try{info=JSON.parse(text);}catch{info=text;}
      const values=typeof info==='string'?[info]:Object.values(info||{});
      const links=values.filter(value=>{try{const u=new URL(value);return typeof value==='string'&&u.origin==='https://pe56d.s3.amazonaws.com'&&!u.username&&!u.password;}catch{return false;}});
      if(links.length===1){
        const file=await fetch(links[0],{credentials:'omit',redirect:'error',signal:AbortSignal.timeout(10000)});
        if(!file.ok)throw Error('Observed storage download failed with HTTP '+file.status);
        const stream=file.body.getReader(),parts=[];length=0;
        while(true){const part=await stream.read();if(part.done)break;length+=part.value.length;if(length>25*1024*1024){await stream.cancel();throw Error('Saved asset exceeds verification limit.');}parts.push(part.value);}
        blob=new Blob(parts);bytes=await blob.arrayBuffer();
      }else{throw Error('Owner download is not ZIP bytes or a unique supported storage link; response type '+(res.headers.get('content-type')||'unknown')+', bytes '+length+', format '+(typeof info==='object'?'JSON fields '+Object.keys(info||{}).join(',').slice(0,100):text.startsWith('<')?'HTML':'text'));}
    }
    const sha256=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
    let image;
    if(source.kind==='image'){
      const bitmap=await createImageBitmap(blob),canvas=new OffscreenCanvas(8,8),ctx=canvas.getContext('2d');ctx.drawImage(bitmap,0,0,8,8);
      const pixels=ctx.getImageData(0,0,8,8).data,gray=[];for(let i=0;i<pixels.length;i+=4)gray.push(Math.round((pixels[i]+pixels[i+1]+pixels[i+2])/3));
      image={width:bitmap.width,height:bitmap.height,gray};bitmap.close();
    }
    check();await requireTab(args);return {bytes:length,sha256,image};
  }
  const supported=['inspect','context','action','trusted_action','upload_begin','upload_chunk','upload_finish'];
  if(!supported.includes(operation))throw Error('Unsupported bounded Chrome operation');
  if(createdTabs.has(tab.id)&&((['action','trusted_action'].includes(operation)&&!['scroll','hover'].includes(args.action))||operation==='upload_begin'))createdTabs.get(tab.id).edited=true;
  if(operation==='upload_begin'){
    const receivers=args.allowed_upload_receivers||[];
    if(!Array.isArray(receivers)||receivers.some(url=>grant.origin!=='https://payhip.com:443'||url!=='https://pe56d.s3.amazonaws.com/'))throw Error('Upload receiver is outside the bounded supported Payhip storage scope.');
    grant.uploadLocked=true;grant.uploadReceivers=receivers;await networkGuard(grant);
  }
  let temporaryRule=null;
  if(['action','trusted_action'].includes(operation)&&args.owner_reviewed===true&&args.reviewed_form_url){
    if(exact(args.reviewed_form_url)!==grant.origin)throw Error('Reviewed form destination is not this authorized site.');
    temporaryRule=nextRule++;
    await chrome.declarativeNetRequest.updateSessionRules({addRules:[{id:temporaryRule,priority:200,action:{type:'allow'},condition:{tabIds:[tab.id],urlFilter:'|'+args.reviewed_form_url+'|',requestMethods:[String(args.reviewed_form_method||'POST').toLowerCase()]}}]});
    // A bounded allowance for the explicitly reviewed form, never a blanket
    // permission for opaque JavaScript endpoints or another website.
    setTimeout(()=>chrome.declarativeNetRequest.updateSessionRules({removeRuleIds:[temporaryRule]}).catch(()=>{}),2000);
  }
  if(operation==='trusted_action'){
    if(!trustedInput||!await chrome.permissions.contains({permissions:['debugger']}))throw Error('Trusted browser input is optional. Enable it explicitly in the extension popup after DOM/pointer methods fail.');
    if(args.frame||!['click','hover'].includes(args.action))throw Error('Trusted input is bounded to root-frame click/hover targets.');
    const point=await content(args,'point');if(!point?.ok)throw Error(point?.error||'Target point unavailable');
    const target={tabId:tab.id};await chrome.debugger.attach(target,'1.3');
    try{
      check();await requireTab(args);const refreshed=await content(args,'point');if(!refreshed?.ok||JSON.stringify(refreshed.result)!==JSON.stringify(point.result))throw Error('Target moved before trusted input. Inspect again.');
      const {x,y}=point.result;await chrome.debugger.sendCommand(target,'Input.dispatchMouseEvent',{type:'mouseMoved',x,y});
      if(args.action==='click'){
        await chrome.debugger.sendCommand(target,'Input.dispatchMouseEvent',{type:'mousePressed',x,y,button:'left',clickCount:1});
        await chrome.debugger.sendCommand(target,'Input.dispatchMouseEvent',{type:'mouseReleased',x,y,button:'left',clickCount:1});
      }
      return {dispatched:true,method:'trusted-browser-input',next:'Inspect and verify. No physical Windows input was used.'};
    }finally{await chrome.debugger.detach(target).catch(()=>{});}
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
      case 'status':return {connected,full_browser:await browserScope(),trusted_input:trustedInput,tabs:[...grants.values()],error:connectionError,authorization_error:lastAuthorizationError};
      case 'full_access':{
        if(message.enabled&&!await chrome.permissions.contains({origins:wideOrigins}))throw Error('Approve broad HTTP/HTTPS website access in Chrome first.');
        fullBrowser=message.enabled===true;await chrome.storage.local.set({fullBrowser});if(!fullBrowser)for(const [tab,g]of [...grants])if(g.scope==='full')await revoke(tab);scopeEvent();return {};
      }
      case 'trusted_input':{
        if(!await chrome.permissions.contains({permissions:['debugger']}))throw Error('Chrome debugger permission was not granted.');trustedInput=true;await chrome.storage.local.set({trustedInput});scopeEvent();return {};
      }
      case 'connect':autoConnect=true;await chrome.storage.local.set({autoConnect:true});connect();return {};
      case 'disconnect':autoConnect=false;await chrome.storage.local.set({autoConnect:false});disconnect();return {};
      case 'authorize':return authorize(null,'tab');
      case 'authorize_site':{
        const tab=await active();if(!await chrome.permissions.contains({origins:[patternFor(tab.url)]}))throw Error('Chrome site permission was not granted.');
        approvedSites.add(exact(tab.url));await chrome.storage.local.set({approvedSites:[...approvedSites]});return authorize(tab,'site');
      }
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
chrome.tabs.onActivated.addListener(info=>{activationEpoch.set(info.windowId,(activationEpoch.get(info.windowId)||0)+1);if(createdTabs.has(info.tabId))createdTabs.get(info.tabId).visited=true;});
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
chrome.permissions.onRemoved?.addListener(async()=>{
  await browserScope();
  for(const site of [...approvedSites])if(!await chrome.permissions.contains({origins:[patternFor(site)]}))approvedSites.delete(site);
  for(const [tab,g]of [...grants])if((g.scope==='full'&&!fullBrowser)||(g.scope==='site'&&!await siteAllowed(g.origin)))await revoke(tab);
  await chrome.storage.local.set({approvedSites:[...approvedSites]});scopeEvent();
});
chrome.storage.local.get(['autoConnect','fullBrowser','trustedInput','approvedSites']).then(async settings=>{
  autoConnect=settings.autoConnect===true;fullBrowser=settings.fullBrowser===true;trustedInput=settings.trustedInput===true;
  for(const site of settings.approvedSites||[])try{approvedSites.add(exact(site));}catch{}
  if(settings.approvedSites===undefined&&chrome.permissions.getAll){
    // Migrate only individually granted hosts; broad Chrome permission is never
    // mistaken for a Restricted-mode site grant.
    const existing=await chrome.permissions.getAll();
    for(const p of existing.origins||[])if(/^https?:\/\/[^*]+\/\*$/.test(p))try{approvedSites.add(exact(p.slice(0,-1)));}catch{}
    await chrome.storage.local.set({approvedSites:[...approvedSites]});
  }
  if(autoConnect)connect();
});
