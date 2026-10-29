// Bundled isolated-world controller. A webpage cannot call this message handler.
(()=>{
  const previous=globalThis.__codexAuthorizedController;
  if(previous===true)throw Error('This page has an earlier controller. Refresh this page once after saving any work, then authorize it again.');
  if(previous?.dispose)previous.dispose();
  let grant=null,manual=false,observation=null,revision=0,observedRevision=0,observedAt=0;
  let elements=[],signatures=[],uploads=new Map(),humanAt=0,automating=0;
  const exact=url=>{const p=new URL(url);return `${p.protocol}//${p.hostname}:${p.port||(p.protocol==='https:'?'443':'80')}`;};
  const effectiveOrigin=()=>exact(/^https?:/.test(location.href)?location.href:globalThis.origin);
  const pageUrl=()=>/^https?:/.test(location.href)?cleanUrl(location.href):effectiveOrigin()+'/[embedded]';
  const cleanUrl=url=>{try{const p=new URL(url);return p.origin+p.pathname;}catch{return '';}};
  const safe=value=>String(value||'').replace(/\b(?:sk-|gh[pousr]_|github_pat_)[a-zA-Z0-9_-]{12,}/g,'[private token]').replace(/eyJ[\w-]+\.[\w-]+\.[\w-]+/g,'[private token]').replace(/\bBearer\s+[\w.~+/-]+=*/gi,'Bearer [private]').replace(/((?:password|access.?token|refresh.?token|api.?key|authorization|cookie)["']?\s*[:=]\s*["']?)[^\s,;<>"']+/gi,'$1[private]');
  const secret=/password|passwd|secret|token|one.?time|verification code|security code|captcha|card.?number|cvv|cvc|iban|mfa|two.factor/i;
  const label=e=>{
    let text='';if(e.labels?.[0]){const clone=e.labels[0].cloneNode(true);for(const child of clone.querySelectorAll('input,textarea,select,button'))child.remove();text=clone.textContent.trim();}
    return safe(e.getAttribute('aria-label')||text||e.innerText||e.placeholder||e.name||'').slice(0,250);
  };
  const privateField=e=>e.type==='password'||secret.test([e.name,e.id,e.autocomplete,label(e)].join(' '));
  const value=e=>e.isContentEditable?e.innerText:('value'in e?e.value:'');
  const signature=e=>[privateField(e)?'[private]':value(e),e.checked,e.selectedIndex];
  function sensitivePage(){return /\/(?:auth|login|signin|sign-in|oauth|captcha|challenge|mfa|payment|checkout)(?:\/|$)/i.test(location.pathname)||[...document.querySelectorAll('input[type=password],input[autocomplete="one-time-code"],input[autocomplete="cc-number"]')].some(visible);}
  function activity(event){if(event.isTrusted&&!automating){humanAt=Date.now();revision++;observation=null;}}
  for(const type of ['beforeinput','input','change','keydown','paste'])document.addEventListener(type,activity,true);
  function check(){if(!grant||manual||effectiveOrigin()!==grant.origin)throw Error('Tab access is revoked, changed or under Manual Control.');}
  function roots(root=document,output=[]){output.push(root);for(const e of root.querySelectorAll('*'))if(e.shadowRoot)roots(e.shadowRoot,output);return output;}
  function visible(e){const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none';}
  function inspect(){
    check();if(sensitivePage())throw Error('Authentication/payment screen: use Manual Control. No page content was returned.');
    const selector='a,button,input:not([type=hidden]),textarea,select,[role=button],[role=checkbox],[role=textbox],[contenteditable=true]';
    elements=roots().flatMap(root=>[...root.querySelectorAll(selector)]).filter(visible).slice(0,180);
    observation=crypto.randomUUID();observedRevision=revision;observedAt=Date.now();signatures=elements.map(signature);
    const controls=elements.map((e,i)=>{const r=e.getBoundingClientRect(),isPrivate=privateField(e);return {element:i,tag:e.tagName,role:e.getAttribute('role')||({'A':'Hyperlink','BUTTON':'Button','INPUT':'Edit','TEXTAREA':'Edit','SELECT':'ComboBox'}[e.tagName]||''),type:e.type||'',label:label(e),value:isPrivate?'[private]':safe(value(e)).slice(0,1200),private:isPrivate,editable:e.isContentEditable,disabled:Boolean(e.disabled),checked:Boolean(e.checked),bounds:{x:r.x,y:r.y,width:r.width,height:r.height},options:e.tagName==='SELECT'?[...e.options].slice(0,80).map(o=>({value:safe(o.value),label:safe(o.label)})):undefined};});
    const tables=[...document.querySelectorAll('table')].slice(0,4).map(t=>[...t.rows].slice(0,30).map(r=>[...r.cells].slice(0,12).map(c=>safe(c.innerText).slice(0,180))));
    return {url:pageUrl(),origin:effectiveOrigin(),title:safe(document.title).slice(0,250),observation,revision,active_element:elements.indexOf(document.activeElement),text:safe(document.body?.innerText).slice(0,10000),controls,tables};
  }
  function target(args){
    check();if(args.observation!==observation||Date.now()-observedAt>60000||observedRevision!==revision)throw Error('Observation changed. Inspect again and preserve human edits.');
    if(Date.now()-humanAt<900)throw Error('Human input has priority in this tab. Inspect again after editing finishes.');
    for(let i=0;i<elements.length;i++)if(!privateField(elements[i])&&JSON.stringify(signature(elements[i]))!==JSON.stringify(signatures[i]))throw Error('A field changed since inspection. Nothing was dispatched; inspect again.');
    if(args.action==='scroll'&&args.element===undefined)return document.scrollingElement;
    const e=elements[args.element];if(!e||!e.isConnected||!visible(e)||e.disabled)throw Error('Element is stale or unavailable. Inspect again.');
    if(privateField(e)||sensitivePage())throw Error('Sensitive control requires Manual Control.');return e;
  }
  function context(args){
    if(args.action==='scroll'&&args.element===undefined){target(args);return {source:'browser',role:'Document',label:'Page scroll',page_url:pageUrl()};}
    const e=target(args),f=e.form||e.closest('form'),type=e.type||'',tag=e.tagName;
    const editable=e.isContentEditable||['INPUT','TEXTAREA','SELECT'].includes(tag);
    const submitting=Boolean(f&&((args.action==='click'&&['submit','image'].includes(type))||(args.action==='press'&&args.key==='Enter'&&tag!=='TEXTAREA')));
    return {source:'browser',tag,type,editable,label:label(e),role:editable?'Edit':tag==='A'?'Hyperlink':tag==='BUTTON'?'Button':e.getAttribute('role')||'',
      form_submission:submitting,form_method:f?(f.method||'get').toUpperCase():'',form_action:f?cleanUrl(f.action):'',href:e.href?cleanUrl(e.href):'',
      credential_form:Boolean(f?.querySelector('input[type=password]')),expands_menu:e.getAttribute('aria-haspopup')==='menu'||e.hasAttribute('aria-expanded'),
      scripted_button:((tag==='BUTTON'||e.getAttribute('role')==='button'||(tag==='INPUT'&&type==='button'))&&!submitting&&!e.hasAttribute('aria-expanded'))||(tag==='A'&&!/^https?:/i.test(e.getAttribute('href')||'')),key:args.key||'',page_url:cleanUrl(location.href)};
  }
  function action(args){
    const e=target(args);observation=null;
    automating++;
    try{
    switch(args.action){
      case 'click':e.click();break;
      case 'fill':{
        const text=String(args.text??'');if(text.length>20000)throw Error('Text exceeds the editing bound.');
        if(e.isContentEditable){const lines=text.split('\n');e.replaceChildren();for(let i=0;i<lines.length;i++){if(i)e.appendChild(document.createElement('br'));e.appendChild(document.createTextNode(lines[i]));}}
        else{const proto=e.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:e.tagName==='INPUT'?HTMLInputElement.prototype:null;if(!proto||['file','button','submit','image','checkbox','radio','reset'].includes(e.type))throw Error('Choose an editable text field.');Object.getOwnPropertyDescriptor(proto,'value').set.call(e,text);}
        e.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText',data:text}));e.dispatchEvent(new Event('change',{bubbles:true}));break;
      }
      case 'select':if(e.tagName!=='SELECT')throw Error('Choose a select control.');if(![...e.options].some(o=>o.value===String(args.text)&&!o.disabled))throw Error('Option does not exist or is disabled.');e.value=String(args.text);e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));break;
      case 'check':if(!['checkbox','radio'].includes(e.type)||typeof args.checked!=='boolean')throw Error('Choose a checkbox/radio and a boolean.');if(e.type==='radio'&&!args.checked)throw Error('Select a different radio option to change this group.');if(e.checked!==args.checked)e.click();break;
      case 'scroll':e.scrollBy({top:Math.max(-2000,Math.min(2000,Number(args.amount)||0)),behavior:'instant'});break;
      case 'press':throw Error('Synthetic key events cannot reliably activate browser defaults in a background tab. Use a semantic click or fill; use Manual Control if a real key is required.');
      default:throw Error('Unsupported DOM action');
    }
    }finally{automating--;}
    return {dispatched:true,next:'Inspect the current page and verify the result. A dispatched event is not proof the website saved a change.'};
  }
  const messageHandler=(args,sender,reply)=>{
    if(sender.id!==chrome.runtime.id||args?.channel!=='codex-content')return false;
    try{
      if(args.operation==='grant'){
        if(effectiveOrigin()!==args.origin)throw Error('Origin changed before tab authorization.');
        grant={origin:args.origin,session:args.session};manual=false;observation=null;reply({ok:true});return;
      }
      if(args.operation==='revoke'){grant=null;observation=null;uploads.clear();reply({ok:true});return;}
      if(args.operation==='manual'){manual=Boolean(args.enabled);observation=null;uploads.clear();reply({ok:true});return;}
      check();if(args.session!==grant.session)throw Error('Stale browser session');
      let result;
      switch(args.operation){
        case 'inspect':result=inspect();break;
        case 'context':result=context(args);break;
        case 'action':result=action(args);break;
        case 'close_check':
          result={may_lose_edits:roots().some(r=>[...r.querySelectorAll('input:not([type=hidden]):not([type=button]):not([type=submit]),textarea,[contenteditable=true]')].some(e=>Boolean(value(e))||e.checked)),revision};break;
        case 'screenshot_check':if(sensitivePage()||roots().some(r=>[...r.querySelectorAll('input,textarea,[contenteditable=true]')].filter(visible).some(privateField)))throw Error('Sensitive page cannot be captured.');result={};break;
        case 'upload_begin':{
          const e=target(args);if(e.type!=='file'||!Number.isInteger(args.size)||args.size<0||args.size>25*1024*1024)throw Error('Unsupported file upload.');
          uploads.clear();uploads.set(args.upload,{element:e,name:String(args.name).replace(/[\\/]/g,'_').slice(0,200),size:args.size,sha256:args.sha256,chunks:[],received:0,revision,at:Date.now()});result={ready:true};break;
        }
        case 'upload_chunk':{
          const u=uploads.get(args.upload);if(!u||Date.now()-u.at>120000||u.revision!==revision||args.offset!==u.received)throw Error('Upload expired or a human edit took priority.');
          const bytes=Uint8Array.from(atob(args.data),c=>c.charCodeAt(0));if(bytes.length>128*1024||u.received+bytes.length>u.size)throw Error('Upload chunk exceeds approved size.');u.chunks.push(bytes);u.received+=bytes.length;result={received:u.received};break;
        }
        case 'upload_finish':{
          const u=uploads.get(args.upload);uploads.delete(args.upload);if(!u||u.revision!==revision||u.received!==u.size||!u.element.isConnected)throw Error('Upload changed before completion.');
          const file=new File(u.chunks,u.name,{type:'application/octet-stream'});
          file.arrayBuffer().then(b=>crypto.subtle.digest('SHA-256',b)).then(hash=>{
            check();if(u.revision!==revision)throw Error('Human edit took priority before file selection.');
            const hex=[...new Uint8Array(hash)].map(x=>x.toString(16).padStart(2,'0')).join('');if(hex!==u.sha256)throw Error('Upload checksum mismatch.');
            const transfer=new DataTransfer();transfer.items.add(file);u.element.files=transfer.files;observation=null;
            u.element.dispatchEvent(new Event('input',{bubbles:true}));u.element.dispatchEvent(new Event('change',{bubbles:true}));
            reply({ok:true,result:{selected:file.name,bytes:file.size,sha256:hex,next:'Inspect and verify the website upload result.'}});
          }).catch(error=>reply({ok:false,error:error.message}));return true;
        }
        default:throw Error('Unsupported content operation');
      }
      reply({ok:true,result});
    }catch(error){reply({ok:false,error:safe(error.message).slice(0,500)});}return false;
  };
  chrome.runtime.onMessage.addListener(messageHandler);
  globalThis.__codexAuthorizedController={dispose(){
    grant=null;observation=null;uploads.clear();
    for(const type of ['beforeinput','input','change','keydown','paste'])document.removeEventListener(type,activity,true);
    try{chrome.runtime.onMessage.removeListener(messageHandler);}catch{}
  }};
})();
