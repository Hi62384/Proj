// Bounded worker regressions; these mocks do not replace live Chrome acceptance.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
import {webcrypto} from 'node:crypto';
const event=()=>({listeners:[],addListener(fn){this.listeners.push(fn);}});
const tabs=new Map([[1,{id:1,windowId:7,url:'https://example.org/editor',status:'complete',active:false}]]);
let next=10;
let assetContext=null;
const reloaded=[];
const chrome={
  declarativeNetRequest:{getSessionRules:async()=>[],updateSessionRules:async()=>{}},
  action:{setBadgeText:async()=>{},setBadgeBackgroundColor:async()=>{}},
  runtime:{id:'test-extension',onMessage:event(),getURL:p=>'chrome-extension://test-extension/'+p},
  alarms:{create:()=>{},onAlarm:event()},storage:{local:{get:async()=>({autoConnect:false})}},
  permissions:{contains:async()=>true},scripting:{executeScript:async()=>{}},
  webNavigation:{getAllFrames:async({tabId})=>[{frameId:0,url:tabs.get(tabId).url,parentFrameId:-1},{frameId:2,url:'https://unapproved.example/frame',parentFrameId:0}],onCommitted:event()},
  tabs:{
    reload:async id=>{reloaded.push(id);Object.assign(tabs.get(id),{discarded:false,status:'complete'});},
    create:async(args)=>{const tab={id:next++,windowId:7,url:args.url,active:args.active,status:'complete'};tabs.set(tab.id,tab);return {...tab};},
    update:async(id,args)=>{Object.assign(tabs.get(id),args);return {...tabs.get(id)};},
    get:async id=>({...tabs.get(id)}),query:async()=>[...tabs.values()],
    remove:async id=>{tabs.delete(id);for(const fn of chrome.tabs.onRemoved.listeners)await fn(id);},
    sendMessage:async(id,args)=>args.operation==='grant'||args.operation==='revoke'?{ok:true}:{ok:true,result:args.operation==='asset_context'?assetContext:args.operation==='close_check'?{may_lose_edits:true,revision:0}:{dispatched:true}},
    onRemoved:event(),onActivated:event(),onUpdated:event()
  }
};
const context=vm.createContext({chrome,URL,crypto:webcrypto,setTimeout,clearTimeout,console,Blob,AbortSignal,TextDecoder});
const source=await readFile(new URL('../chrome_extension/worker.js',import.meta.url),'utf8');
vm.runInContext(source+`
connected=true;session='test-session';grantAckSupported=true;approvedSites.add('https://example.org:443');
port={postMessage(message){if(message.event==='grant')grantWaiters.get(message.tab.tab+':'+message.tab.origin)?.resolve();}};
globalThis.test={execute,authorize};`,context);
const run=(operation,args)=>context.test.execute(operation,args,()=>{});
await context.test.authorize(tabs.get(1));
const human=await run('close_check',{tab:1,assistant_created:true,untouched:true});
assert.equal(human.may_lose_edits,true,'Model fields cannot forge creation provenance');
const own=await run('open_tab',{url:'https://example.org/products'});
assert.equal(own.authorized,true);assert.equal(tabs.get(own.tab).active,false);
const count=tabs.size;
const reused=await run('open_tab',{url:'https://example.org/products'});
assert.equal(reused.tab,own.tab);assert.equal(reused.reused,true);assert.equal(tabs.size,count,'Same URL must not create another tab');
const clean=await run('close_check',{tab:own.tab});assert.equal(clean.may_lose_edits,false,'Unvisited/unedited assistant tab is clean despite initial fields/frames');
await run('close_tab',{tab:own.tab,close_token:clean.close_token});assert.equal(tabs.has(own.tab),false);
const visited=await run('open_tab',{url:'https://example.org/products'});
for(const fn of chrome.tabs.onActivated.listeners)fn({tabId:visited.tab,windowId:7});
assert.equal((await run('close_check',{tab:visited.tab})).may_lose_edits,true,'A human-visited tab loses the unattended clean-close exception');
const edited=await run('open_tab',{url:'https://example.org/products?edited=1'});
const before=await run('close_check',{tab:edited.tab});
await run('action',{tab:edited.tab,action:'fill',text:'Unsent owner work'});
await assert.rejects(run('close_tab',{tab:edited.tab,close_token:before.close_token}),/changed before closing/);
assert.equal((await run('close_check',{tab:edited.tab})).may_lose_edits,true);
const navigated=await run('open_tab',{url:'https://example.org/products?navigated=1'});const proof=await run('close_check',{tab:navigated.tab});
for(const fn of chrome.webNavigation.onCommitted.listeners)fn({tabId:navigated.tab,frameId:0,url:'https://example.org/products'});
await assert.rejects(run('close_tab',{tab:navigated.tab,close_token:proof.close_token}),/changed before closing/);
const restricted=await run('open_tab',{url:'https://different.example/page'});assert.equal(restricted.authorized,false,'Restricted mode does not inherit Chrome broad host permission');
const restrictedCount=tabs.size;
assert.equal((await run('open_tab',{url:'https://different.example/page'})).tab,restricted.tab);
assert.equal(tabs.size,restrictedCount,'An existing unapproved tab requires authorization, not a duplicate');
tabs.set(222,{id:222,windowId:7,url:'https://example.org/restored',active:false,discarded:true,status:'unloaded'});
const restoredCount=tabs.size;
const restored=await run('open_tab',{url:'https://example.org/restored'});
assert.equal(restored.tab,222);assert.equal(restored.reused,true);assert.deepEqual(reloaded,[222]);assert.equal(tabs.size,restoredCount);assert.equal(tabs.get(222).active,false,'Waking a discarded tab never activates it');
const [concurrentA,concurrentB]=await Promise.all([run('open_tab',{url:'https://example.org/concurrent'}),run('open_tab',{url:'https://example.org/concurrent'})]);
assert.equal(concurrentA.tab,concurrentB.tab,'Concurrent same-URL requests share one creation');
const humanBefore={...tabs.get(1)},humanCount=tabs.size;
const existingHuman=await run('open_tab',{url:'https://example.org/editor'});
assert.equal(existingHuman.tab,1);assert.equal(existingHuman.reused,true);assert.deepEqual(tabs.get(1),humanBefore);assert.equal(tabs.size,humanCount);
assert.equal((await run('close_check',{tab:1})).may_lose_edits,true,'Reuse never forges clean-close provenance for an existing human tab');
await run('manual',{tab:1,enabled:true});
await assert.rejects(run('open_tab',{url:'https://example.org/editor'}),/manual control/);
assert.equal(tabs.size,humanCount,'Manual takeover must not create a duplicate workaround');
await assert.rejects(run('trusted_action',{tab:visited.tab,action:'click'}),/optional/);
let requestedOptions=null,finalUrl='https://pe56d.s3.amazonaws.com/approved.zip';
context.fetch=async(url,options)=>{requestedOptions=options;const response=new Response('PKapproved ZIP bytes');return {ok:true,url:finalUrl,body:response.body,headers:response.headers};};
assetContext={url:'https://payhip.com/product/download/Observed123',kind:'delivery'};
const verifiedAsset=await run('asset_digest',{tab:edited.tab,observation:'fresh',element:2,kind:'delivery'});
assert.equal(requestedOptions.redirect,'follow');assert.equal(verifiedAsset.bytes,20);assert.match(verifiedAsset.sha256,/^[a-f0-9]{64}$/);
finalUrl='https://unapproved.example/asset';
await assert.rejects(run('asset_digest',{tab:edited.tab,observation:'fresh',element:2,kind:'delivery'}),/outside the supported storage scope/);
assetContext={url:'https://example.org/download/Observed123',kind:'delivery'};finalUrl=assetContext.url;
await run('asset_digest',{tab:edited.tab,observation:'fresh',element:2,kind:'delivery'});
assert.equal(requestedOptions.redirect,'error','Other download sources do not gain redirect authority');
assetContext={url:'https://payhip.com/product/download/Observed123',kind:'delivery'};
let fetchCount=0;
context.fetch=async(url,options)=>{
 fetchCount++;const response=new Response(fetchCount===1?'https://pe56d.s3.amazonaws.com/observed.zip?private=inside-browser':'approved ZIP bytes',{headers:{'content-type':'text/plain'}});
 return {ok:true,url,body:response.body,headers:response.headers};
};
assert.equal((await run('asset_digest',{tab:edited.tab,observation:'fresh',element:2,kind:'delivery'})).bytes,18);
assert.equal(fetchCount,2,'Plain-text observed storage link is consumed inside browser');
context.fetch=async(url,options)=>{const response=new Response('https://unapproved.example/file',{headers:{'content-type':'text/plain'}});return {ok:true,url,body:response.body,headers:response.headers};};
await assert.rejects(run('asset_digest',{tab:edited.tab,observation:'fresh',element:2,kind:'delivery'}),/not ZIP bytes or a unique supported storage link/);
console.log('PASS: exact-URL and concurrent reuse, unchanged human tabs, manual takeover, restricted access, clean close and provenance races');
