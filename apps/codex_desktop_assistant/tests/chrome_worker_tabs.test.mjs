// Bounded worker regressions; these mocks do not replace live Chrome acceptance.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
import {webcrypto} from 'node:crypto';
const event=()=>({listeners:[],addListener(fn){this.listeners.push(fn);}});
const tabs=new Map([[1,{id:1,windowId:7,url:'https://example.org/editor',status:'complete',active:false}]]);
let next=10;
const chrome={
  declarativeNetRequest:{getSessionRules:async()=>[],updateSessionRules:async()=>{}},
  action:{setBadgeText:async()=>{},setBadgeBackgroundColor:async()=>{}},
  runtime:{id:'test-extension',onMessage:event(),getURL:p=>'chrome-extension://test-extension/'+p},
  alarms:{create:()=>{},onAlarm:event()},storage:{local:{get:async()=>({autoConnect:false})}},
  permissions:{contains:async()=>true},scripting:{executeScript:async()=>{}},
  webNavigation:{getAllFrames:async({tabId})=>[{frameId:0,url:tabs.get(tabId).url,parentFrameId:-1},{frameId:2,url:'https://unapproved.example/frame',parentFrameId:0}],onCommitted:event()},
  tabs:{
    create:async(args)=>{const tab={id:next++,windowId:7,url:args.url,active:args.active,status:'complete'};tabs.set(tab.id,tab);return {...tab};},
    update:async(id,args)=>{Object.assign(tabs.get(id),args);return {...tabs.get(id)};},
    get:async id=>({...tabs.get(id)}),query:async()=>[...tabs.values()],
    remove:async id=>{tabs.delete(id);for(const fn of chrome.tabs.onRemoved.listeners)await fn(id);},
    sendMessage:async(id,args)=>args.operation==='grant'||args.operation==='revoke'?{ok:true}:{ok:true,result:args.operation==='close_check'?{may_lose_edits:true,revision:0}:{dispatched:true}},
    onRemoved:event(),onActivated:event(),onUpdated:event()
  }
};
const context=vm.createContext({chrome,URL,crypto:webcrypto,setTimeout,clearTimeout,console});
const source=await readFile(new URL('../chrome_extension/worker.js',import.meta.url),'utf8');
vm.runInContext(source+`
connected=true;session='test-session';grantAckSupported=true;
port={postMessage(message){if(message.event==='grant')grantWaiters.get(message.tab.tab+':'+message.tab.origin)?.resolve();}};
globalThis.test={execute,authorize};`,context);
const run=(operation,args)=>context.test.execute(operation,args,()=>{});
await context.test.authorize(tabs.get(1));
const human=await run('close_check',{tab:1,assistant_created:true,untouched:true});
assert.equal(human.may_lose_edits,true,'Model fields cannot forge creation provenance');
const own=await run('open_tab',{url:'https://example.org/products'});
assert.equal(own.authorized,true);assert.equal(tabs.get(own.tab).active,false);
const clean=await run('close_check',{tab:own.tab});assert.equal(clean.may_lose_edits,false,'Unvisited/unedited assistant tab is clean despite initial fields/frames');
await run('close_tab',{tab:own.tab,close_token:clean.close_token});assert.equal(tabs.has(own.tab),false);
const visited=await run('open_tab',{url:'https://example.org/products'});
for(const fn of chrome.tabs.onActivated.listeners)fn({tabId:visited.tab,windowId:7});
assert.equal((await run('close_check',{tab:visited.tab})).may_lose_edits,true,'A human-visited tab loses the unattended clean-close exception');
const edited=await run('open_tab',{url:'https://example.org/products'});
const before=await run('close_check',{tab:edited.tab});
await run('action',{tab:edited.tab,action:'fill',text:'Unsent owner work'});
await assert.rejects(run('close_tab',{tab:edited.tab,close_token:before.close_token}),/changed before closing/);
assert.equal((await run('close_check',{tab:edited.tab})).may_lose_edits,true);
const navigated=await run('open_tab',{url:'https://example.org/products'});const proof=await run('close_check',{tab:navigated.tab});
for(const fn of chrome.webNavigation.onCommitted.listeners)fn({tabId:navigated.tab,frameId:0,url:'https://example.org/products'});
await assert.rejects(run('close_tab',{tab:navigated.tab,close_token:proof.close_token}),/changed before closing/);
console.log('PASS: automatic background creation, clean close, forged ownership, human visits, edits and navigation races');
