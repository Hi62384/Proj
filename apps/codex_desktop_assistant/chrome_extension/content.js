// Bundled isolated-world controller. A webpage cannot call this message handler.
(()=>{
  const previous=globalThis.__codexAuthorizedController;
  if(previous===true)throw Error('This page has an earlier controller. Refresh this page once after saving any work, then authorize it again.');
  if(previous?.dispose)previous.dispose();
  let grant=null,manual=false,observation=null,revision=0,observedRevision=0,observedAt=0;
  let elements=[],signatures=[],media=[],uploads=new Map(),humanAt=0,automating=0;
  const exact=url=>{const p=new URL(url);return `${p.protocol}//${p.hostname}:${p.port||(p.protocol==='https:'?'443':'80')}`;};
  const effectiveOrigin=()=>exact(/^https?:/.test(location.href)?location.href:globalThis.origin);
  const pageUrl=()=>/^https?:/.test(location.href)?cleanUrl(location.href):effectiveOrigin()+'/[embedded]';
  const cleanUrl=url=>{try{const p=new URL(url),q=new URLSearchParams();if(!["http:","https:"].includes(p.protocol))return "";for(const [key,value]of p.searchParams)if(/^(?:q|query|search|page|sort|filter|category|product|product_type|type|new|add|view|mode|tab|section|action|operation|do|command)$/i.test(key)&&value.length<=500&&!/password|token|secret|authorization|api.?key/i.test(value))q.append(key,safe(value));return p.origin+p.pathname+(q.size?'?'+q.toString():'');}catch{return '';}};
  const safe=value=>String(value||'').replace(/\b(?:sk-|gh[pousr]_|github_pat_)[a-zA-Z0-9_-]{12,}/g,'[private token]').replace(/eyJ[\w-]+\.[\w-]+\.[\w-]+/g,'[private token]').replace(/\bBearer\s+[\w.~+/-]+=*/gi,'Bearer [private]').replace(/((?:password|access.?token|refresh.?token|api.?key|authorization|cookie)["']?\s*[:=]\s*["']?)[^\s,;<>"']+/gi,'$1[private]');
  const secret=/password|passwd|secret|token|one.?time|verification code|security code|captcha|card.?number|cvv|cvc|iban|mfa|two.factor/i;
  const label=e=>{
    let text='';if(e.labels?.[0]){const clone=e.labels[0].cloneNode(true);for(const child of clone.querySelectorAll('input,textarea,select,button'))child.remove();text=clone.textContent.trim();}
    const parent=e.closest('button,a,[role=button],[aria-label]');return safe(e.getAttribute('aria-label')||e.getAttribute('title')||text||e.innerText||e.placeholder||(['submit','button'].includes(e.type)?e.value:'')||e.name||parent?.getAttribute('aria-label')||'').slice(0,250);
  };
  const privateField=e=>e.type==='password'||secret.test([e.name,e.id,e.autocomplete,label(e)].join(' '));
  const value=e=>e.isContentEditable?e.innerText:('value'in e?e.value:'');
  const signature=e=>[privateField(e)?'[private]':value(e),e.checked,e.selectedIndex];
  function sensitivePage(){return /\/(?:auth|login|signin|sign-in|oauth|captcha|challenge|mfa|payment|checkout)(?:\/|$)/i.test(location.pathname)||[...document.querySelectorAll('input[type=password],input[autocomplete="one-time-code"],input[autocomplete="cc-number"]')].some(visible);}
  function activity(event){if(event.isTrusted&&!automating){humanAt=Date.now();revision++;observation=null;}}
  for(const type of ['beforeinput','input','change','keydown','paste'])document.addEventListener(type,activity,true);
  function check(){if(!grant||manual||effectiveOrigin()!==grant.origin)throw Error('Tab access is revoked, changed or under Manual Control.');}
  function roots(root=document,output=[]){output.push(root);for(const e of root.querySelectorAll('*'))if(e.shadowRoot)roots(e.shadowRoot,output);return output;}
  function visible(e){const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'&&!e.closest('[hidden],[inert],[aria-hidden="true"]');}
  function interactive(e){return e.matches('a,button,input,textarea,select,summary,[role=button],[role=tab],[role=option],[role=checkbox],[role=radio],[role=menuitem],[role=textbox],[role=combobox],[role=switch],[role=slider],[onclick],[tabindex],[contenteditable]')||getComputedStyle(e).cursor==='pointer';}
  function elementRole(e){return e.getAttribute('role')||({'A':'Hyperlink','BUTTON':'Button','INPUT':'Edit','TEXTAREA':'Edit','SELECT':'ComboBox','SUMMARY':'Button','LABEL':'Button'}[e.tagName]||(getComputedStyle(e).cursor==='pointer'?'Button':''));}
  function nearby(e){let node=e.parentElement,best='';for(let i=0;i<4&&node;i++,node=node.parentElement){const text=safe(node.innerText).trim();if(text.length>1600)break;if(text.length>best.length)best=text;}return best.slice(0,500);}
  function commerce(){
    const currency=[document.querySelector('meta[itemprop="priceCurrency"],meta[property="product:price:currency"],meta[property="og:price:currency"]')?.content,document.querySelector('[name=currency],[name=p_currency]')?.value,document.querySelector('[data-currency]')?.getAttribute('data-currency')].find(v=>/^(?:USD|CAD|GBP|EUR|AUD|NZD|JPY|INR|ZAR|BRL)$/i.test(v||''));
    // Only the nonsensitive receiver and receipt inventory used by Payhip's
    // observed uploader. Never read AWS keys, policies, signatures or tokens.
    const receiver=document.querySelector('meta[property="aws-s3-url"]')?.getAttribute('value');let uploadReceiver=null,files=[],filesState='missing';
    try{const p=new URL(receiver);if(p.protocol==='https:'&&!p.username&&!p.password&&!p.search)uploadReceiver=p.origin+p.pathname;}catch{}
    try{const raw=document.querySelector('meta[property="digital-file-upload-data"]')?.getAttribute('value');if(raw&&raw.length<100000){const parsed=JSON.parse(raw);filesState=Array.isArray(parsed)?'valid':'invalid';if(Array.isArray(parsed))files=parsed.slice(0,40).map(f=>({name:safe(f.file_orig),bytes:Number(f.size)||0,status:safe(f.status),receipt:Boolean(f.file&&/^https:\/\//.test(f.file))}));}}catch{filesState='invalid';}
    let images=[],imagesState='missing';
    try{const raw=document.querySelector('meta[property="cover-image-upload-data"]')?.getAttribute('value');if(raw&&raw.length<100000){const parsed=JSON.parse(raw);imagesState=Array.isArray(parsed)?'valid':'invalid';if(Array.isArray(parsed))images=parsed.slice(0,9).map((f,i)=>({asset:i,name:safe(f.name),bytes:Number(f.size)||0,status:safe(f.status),receipt:Boolean(f.thumb&&/^https:\/\//.test(f.thumb))}));}}catch{imagesState='invalid';}
    return {currency:currency?currency.toUpperCase():null,upload_receiver:uploadReceiver,digital_files:files,digital_files_state:filesState,cover_images:images,cover_images_state:imagesState,upload_in_progress:document.querySelector('meta[property="upload-in-progress"]')?.getAttribute('value')==='1'};
  }
  function inspect(args={}){
    check();if(sensitivePage())throw Error('Authentication/payment screen: use Manual Control. No page content was returned.');
    const selector='a,button,input:not([type=hidden]),textarea,select,summary,[role=button],[role=tab],[role=option],[role=checkbox],[role=radio],[role=menuitem],[role=textbox],[role=combobox],[role=switch],[role=slider],[onclick],[tabindex],[contenteditable]:not([contenteditable=false])';
    const all=roots(),semantic=all.flatMap(root=>[...root.querySelectorAll(selector)]);
    const custom=all.flatMap(root=>[...root.querySelectorAll('div,span,svg')].slice(0,6000).filter(e=>getComputedStyle(e).cursor==='pointer'&&!e.closest('button,a,[role=button]')));
    const candidates=[...new Set([...semantic,...custom])].filter(visible).filter(e=>!args.query||label(e).toLowerCase().includes(String(args.query).slice(0,120).toLowerCase()));const offset=Math.max(0,Math.min(6000,Number(args.offset)||0));elements=candidates.slice(offset,offset+120);
    observation=crypto.randomUUID();observedRevision=revision;observedAt=Date.now();signatures=elements.map(signature);
    const controls=elements.map((e,i)=>{const r=e.getBoundingClientRect(),isPrivate=privateField(e);return {element:i,tag:e.tagName,role:elementRole(e),type:e.type||'',accept:e.accept||'',multiple:Boolean(e.multiple),files:e.type==='file'?[...e.files].map(f=>({name:safe(f.name),bytes:f.size,type:f.type})):undefined,label:label(e),nearby:nearby(e),href:e.href?cleanUrl(e.href):'',name:privateField(e)?'[private]':safe(e.name||''),id:safe(e.id||''),value:isPrivate?'[private]':safe(value(e)).slice(0,1200),private:isPrivate,editable:e.isContentEditable,disabled:Boolean(e.disabled),checked:Boolean(e.checked),expanded:e.getAttribute('aria-expanded'),controls:e.getAttribute('aria-controls')||e.getAttribute('data-target')||e.getAttribute('data-bs-target')||e.hash||'',fragment:e.hash||'',popup:e.getAttribute('aria-haspopup'),background:getComputedStyle(e).backgroundColor,interactive:interactive(e),in_viewport:r.x+r.width>0&&r.y+r.height>0&&r.x<innerWidth&&r.y<innerHeight,bounds:{x:r.x,y:r.y,width:r.width,height:r.height},options:e.tagName==='SELECT'?[...e.options].slice(0,80).map(o=>({value:safe(o.value),label:safe(o.label)})):undefined};});
    const pageText=safe(document.body?.innerText),textOffset=Math.max(0,Math.min(1000000,Number(args.text_offset)||0));const tables=[...document.querySelectorAll('table')].slice(0,4).map(t=>[...t.rows].slice(0,30).map(r=>[...r.cells].slice(0,12).map(c=>safe(c.innerText).slice(0,180))));
    media=all.flatMap(root=>[...root.querySelectorAll('img')]).filter(visible).slice(0,50);
    const images=media.map((e,i)=>({asset:i,label:safe(e.alt),url:cleanUrl(e.currentSrc||e.src),width:e.naturalWidth,height:e.naturalHeight}));
    return {script_sources:[...document.scripts].map(e=>cleanUrl(e.src)).filter(Boolean).slice(0,60).map(url=>url.slice(0,500)),resource_origins:[...new Set(performance.getEntriesByType('resource').filter(e=>['fetch','xmlhttprequest'].includes(e.initiatorType)).map(e=>{try{return new URL(e.name).origin;}catch{return '';}}))].filter(Boolean).slice(-30),headings:[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(visible).slice(0,40).map(e=>({level:Number(e.tagName.slice(1)),text:safe(e.innerText).slice(0,500)})),commerce:commerce(),images,url:pageUrl(),origin:effectiveOrigin(),title:safe(document.title).slice(0,250),observation,offset,total_controls:candidates.length,next_offset:offset+elements.length<candidates.length?offset+elements.length:null,revision,active_element:elements.indexOf(document.activeElement),text:pageText.slice(textOffset,textOffset+10000),text_offset:textOffset,next_text_offset:textOffset+10000<pageText.length?textOffset+10000:null,text_tail:pageText.length>10000?pageText.slice(-10000):undefined,total_text:pageText.length,controls,tables};
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
    return {source:'browser',tag,type,editable,label:label(e),role:editable?'Edit':elementRole(e),
      form_submission:submitting,form_method:f?((e.hasAttribute('formmethod')?e.formMethod:f.method)||'get').toUpperCase():'',form_action:f?cleanUrl(e.hasAttribute('formaction')?e.formAction:f.action):'',href:e.href?cleanUrl(e.href):'',
      credential_form:Boolean(f?.querySelector('input[type=password]')),expands_menu:Boolean(e.getAttribute('aria-haspopup'))||e.hasAttribute('aria-expanded')||tag==='SUMMARY'||((e.getAttribute('aria-controls')||e.getAttribute('data-target')||e.getAttribute('data-bs-target')||e.hash)&&document.getElementById((e.getAttribute('aria-controls')||e.getAttribute('data-target')||e.getAttribute('data-bs-target')||e.hash).replace(/^#/,''))),control_kind:type==='color'?'color':editable?'editor':elementRole(e),form_visibility:f?.querySelector('[name=product_status]:checked,[name=visibility]')?.value||'',form_currency:commerce().currency,form_id:f?.id||'',explicit_action:e.getAttribute('data-action')||'',
      scripted_button:((tag==='BUTTON'||e.getAttribute('role')==='button'||(tag==='INPUT'&&type==='button'))&&!submitting&&!e.hasAttribute('aria-expanded'))||(tag==='A'&&!/^https?:/i.test(e.getAttribute('href')||'')),key:args.key||'',page_url:cleanUrl(location.href)};
  }
  function action(args){
    const e=target(args);observation=null;
    automating++;
    try{
    switch(args.action){
      case 'click':
        if(e.matches('input:not([type=file]),textarea,[contenteditable=true]'))e.focus({preventScroll:true});
        if(args.method==='pointer')for(const type of ['pointerover','pointerdown','mousedown','pointerup','mouseup'])e.dispatchEvent(type.startsWith('pointer')?new PointerEvent(type,{bubbles:true,pointerType:'mouse',button:0}):new MouseEvent(type,{bubbles:true,button:0}));
        if(typeof e.click==='function')e.click();else e.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window}));break;
      case 'hover':for(const type of ['pointerover','pointerenter','mouseover','mouseenter'])e.dispatchEvent(type.startsWith('pointer')?new PointerEvent(type,{bubbles:true,pointerType:'mouse'}):new MouseEvent(type,{bubbles:true,view:window}));break;
      case 'fill':{
        const text=String(args.text??'');if(e.type==='color'&&!/^#[0-9a-f]{6}$/i.test(text))throw Error('Use a six-digit hex color.');if(text.length>20000)throw Error('Text exceeds the editing bound.');
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
        case 'inspect':result=inspect(args);break;
        case 'context':result=context(args);break;
        case 'asset_context':{
          if(args.observation!==observation||observedRevision!==revision||Date.now()-observedAt>60000||sensitivePage())throw Error('Inspect the saved asset page again.');
          if(args.kind==='uploaded_image'){
            const raw=document.querySelector('meta[property="cover-image-upload-data"]')?.getAttribute('value');
            if(!raw||raw.length>100000)throw Error('Image receipt is unavailable.');
            const records=JSON.parse(raw),record=Array.isArray(records)&&records[args.asset];
            if(!record||!Number.isInteger(args.asset)||args.asset<0||args.asset>8)throw Error('Image receipt is unavailable.');
            const p=new URL(record.thumb);
            if(p.origin!=='https://pe56d.s3.amazonaws.com'||p.search||p.username||p.password||!p.pathname.toLowerCase().endsWith('.png'))throw Error('Not a supported approved original image.');
            result={url:p.href,kind:'image'};break;
          }
          const e=args.kind==='image'?media[args.asset]:target({...args,action:'read'});
          if(!e?.isConnected||!visible(e))throw Error('Saved asset is unavailable.');
          const url=args.kind==='image'?(e.currentSrc||e.src):e.href,p=new URL(url);
          if(!['http:','https:'].includes(p.protocol)||p.username||p.password||/\/(?:delete|remove|publish|checkout|logout|auth|payment|settings)(?:\/|$)/i.test(p.pathname))throw Error('Not a supported saved asset.');
          if(args.kind!=='image'&&!/\.zip(?:$|\?)|download/i.test(p.pathname+' '+label(e)))throw Error('Not an observed delivery download.');
          result={url,kind:args.kind};break;
        }
        case 'point':{const e=target(args),r=e.getBoundingClientRect();if(r.x<0||r.y<0||r.right>innerWidth||r.bottom>innerHeight)throw Error('Scroll this target into view before trusted input.');result={x:r.x+r.width/2,y:r.y+r.height/2};break;}
        case 'action':result=action(args);break;
        case 'close_check':
          result={may_lose_edits:roots().some(r=>[...r.querySelectorAll('input:not([type=hidden]):not([type=button]):not([type=submit]):not([type=reset]),textarea,select,[contenteditable=true]')].some(e=>{
            if(e.type==='checkbox'||e.type==='radio')return e.checked!==e.defaultChecked;
            if(e.type==='file')return Boolean(e.files?.length);
            if(e.tagName==='SELECT'){
              if(e.multiple)return [...e.options].some(o=>o.selected!==o.defaultSelected);
              const initial=[...e.options].findIndex(o=>o.defaultSelected);return e.selectedIndex!==(initial<0?0:initial);
            }
            return Boolean(String(value(e)||'').trim());
          })),revision};break;
        case 'screenshot_check':if(sensitivePage()||roots().some(r=>[...r.querySelectorAll('input,textarea,[contenteditable=true]')].filter(visible).some(privateField)))throw Error('Sensitive page cannot be captured.');result={};break;
        case 'upload_begin':{
          const e=target(args);if(e.type!=='file'||!Number.isInteger(args.size)||args.size<0||args.size>25*1024*1024)throw Error('Unsupported file upload.');
          uploads.clear();uploads.set(args.upload,{element:e,mime:['image/png','image/jpeg','application/zip'].includes(args.mime)?args.mime:'application/octet-stream',name:String(args.name).replace(/[\\/]/g,'_').slice(0,200),size:args.size,sha256:args.sha256,chunks:[],received:0,revision,at:Date.now()});result={ready:true};break;
        }
        case 'upload_chunk':{
          const u=uploads.get(args.upload);if(!u||Date.now()-u.at>120000||u.revision!==revision||args.offset!==u.received)throw Error('Upload expired or a human edit took priority.');
          const bytes=Uint8Array.from(atob(args.data),c=>c.charCodeAt(0));if(bytes.length>128*1024||u.received+bytes.length>u.size)throw Error('Upload chunk exceeds approved size.');u.chunks.push(bytes);u.received+=bytes.length;result={received:u.received};break;
        }
        case 'upload_finish':{
          const u=uploads.get(args.upload);uploads.delete(args.upload);if(!u||u.revision!==revision||u.received!==u.size||!u.element.isConnected)throw Error('Upload changed before completion.');
          const file=new File(u.chunks,u.name,{type:u.mime});
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
