"""Payhip UI adapter: browser observations only, never a guessed private API.

Account writes require a separate owner-approved manifest and verified Invisible
controls. Probe is read-only and returns reasons when a page cannot establish that
contract. Ambiguous completion is reconciled from Products before another attempt.
"""
import hashlib
import json
import re
import time
import threading
from decimal import Decimal
from urllib.parse import urlsplit
from .permissions import Denied
from .products import digest


class PayhipBrowserAdapter:
    def __init__(self,chrome,conversation,store,attachments):
        self.chrome,self.conversation,self.store,self.attachments=chrome,conversation,store,attachments
        self.tab=None;self.probe_result=None;self.scope=None;self.pending=None;self.queue=None;self.project=None;self.scope_id=None;self.factory=None;self.lock=threading.RLock();self.expected=None;self.currency=None

    def call(self,operation,args):
        self.store.action(self.conversation,'payhip.'+operation,'requested')
        result=self.chrome.call(self.conversation,operation,args)
        self.store.action(self.conversation,'payhip.'+operation,'completed');return result

    @staticmethod
    def url(url):
        p=urlsplit(url)
        if p.scheme!='https' or p.hostname!='payhip.com' or p.username or p.password or p.port not in (None,443):raise Denied('Payhip adapter only operates the approved HTTPS Payhip site')
        if any(part in ('logout','settings','delete','remove','publish','payment','checkout','auth') for part in p.path.lower().split('/')):raise Denied('Not a product-preparation page')
        return p.scheme+'://'+p.netloc+p.path+('?' + p.query if p.query else '')

    def inspect(self):
        if self.tab is None:raise Denied('Open an agent-owned Payhip product page first')
        return self.call('inspect',{'tab':self.tab})

    def open(self,url):
        self.url(url);result=self.call('open_tab',{'url':url})
        if not result.get('authorized'):raise Denied('Approve Payhip site access or Full Browser Access in Chrome; no account mutation occurred')
        self.tab=result['tab']
        for _ in range(15):
            snapshot=self.inspect()
            if snapshot.get('controls') or snapshot.get('text'):return snapshot
            time.sleep(.2)
        raise Denied('Payhip product page did not expose supported controls')

    def probe(self):
        snapshot=self.open('https://payhip.com/products');controls=snapshot.get('controls',[])
        calculator=[c for c in controls if 'cleaning business' in c.get('label','').lower() and 'calculator' in c.get('label','').lower()]
        baseline={'calculator_controls':[{'label':c['label'],'href':c.get('href','')} for c in calculator],'hidden_label_visible':'HIDDEN' in snapshot.get('text','')}
        links=[c for c in controls if re.fullmatch(r'add (?:a )?new product|add product',c.get('label','').strip(),re.I)]
        product_url=None
        if links:
            add=links[0];href=add.get('href','')
            if add.get('controls') or add.get('fragment') or href==snapshot['url']:
                args={'tab':self.tab,'observation':snapshot['observation'],'element':add['element'],'action':'click'}
                context=self.chrome.request(self.conversation,'context',args,self.chrome.permissions.generation)
                # Payhip documents these two navigation steps before any upload
                # or product submission. Never generalize this to Save/Add forms.
                if context.get('form_submission') or context.get('credential_form'):raise Denied('New-product entry unexpectedly submits a form; stop before account mutation')
                self.call('action',{'tab':self.tab,'observation':snapshot['observation'],'element':add['element'],'operation':'click'})
                snapshot=self.inspect()
                for _ in range(12):
                    if any(re.match(r'Digital Product\b',c.get('label',''),re.I) for c in snapshot['controls']):break
                    time.sleep(.15);snapshot=self.inspect()
                digital=next((c for c in snapshot['controls'] if re.match(r'Digital Product\b',c.get('label',''),re.I)),None)
                if digital:
                    href=digital.get('href','')
                    if not href or href==snapshot['url'] or digital.get('fragment'):
                        args={'tab':self.tab,'observation':snapshot['observation'],'element':digital['element'],'action':'click'}
                        context=self.chrome.request(self.conversation,'context',args,self.chrome.permissions.generation)
                        if context.get('form_submission'):raise Denied('Product type entry unexpectedly submits content; stop before account mutation')
                        self.call('action',{'tab':self.tab,'observation':snapshot['observation'],'element':digital['element'],'operation':'click'});time.sleep(.3);snapshot=self.inspect();href=''
                else:href=''
            if href:
                product_url=self.url(href)
                if not urlsplit(product_url).path.startswith(('/products','/product/')):raise Denied('New-product link is not a verified product-management route')
                if product_url!=snapshot['url']:snapshot=self.open(product_url)
        fields=[{'element':c['element'],'label':c.get('label',''),'tag':c.get('tag'),'type':c.get('type'),'name':c.get('name',''),'id':c.get('id',''),'href':c.get('href',''),'options':c.get('options',[]),'accept':c.get('accept',''),'nearby':c.get('nearby',''),'checked':c.get('checked',False),'editable':c.get('editable',False),'value':c.get('value','') if c.get('type') in ('checkbox','radio','select-one') else ''} for c in snapshot.get('controls',[]) if not c.get('private')]
        invisible=any((c.get('name')=='product_status' and c.get('value')=='invisible') or any(re.search(r'invisible|hidden',o.get('label',''),re.I) for o in c.get('options',[])) for c in snapshot.get('controls',[]))
        self.probe_result={'read_only':True,'page_url':snapshot['url'],'new_product_url':product_url,'baseline':baseline,'controls':fields,'currency':snapshot.get('commerce',{}).get('currency'),'upload_receiver':snapshot.get('commerce',{}).get('upload_receiver'),'invisible_control_observed':invisible,'guaranteed_hidden_preparation':False,'reason':'A real product-write manifest and the complete Invisible/save control contract must be verified before account mutation.'}
        return self.probe_result

    def authorize(self,manifest,scope_id=None):
        if not self.probe_result:raise Denied('Complete the read-only Payhip probe first')
        if manifest.get('visibility')!='invisible' or manifest.get('max_new_products')!=1 or manifest.get('spending_limit_cents')!=0 or not time.time()<manifest.get('expires',0)<=time.time()+86400:raise Denied('Invalid bounded first-product authorization')
        if manifest.get('upload_receivers',[]) not in ([],['https://pe56d.s3.amazonaws.com/']):raise Denied('Unsupported external storage receiver')
        self.scope=dict(manifest);self.scope_id=scope_id

    def manifest(self,queue,project,package):
        from .products import ProductFactory
        if not self.probe_result or not self.probe_result.get('invisible_control_observed'):raise Denied('Read-only probe must first expose Invisible')
        factory=ProductFactory(queue.root/project/'artifacts');archive=factory.path(package['archive'])
        if not package.get('qa_verified') or digest(archive)!=package['sha256']:raise Denied('Validated delivery changed')
        snapshot=self.open(self.probe_result['new_product_url'])
        button=self.find(snapshot,lambda c:c.get('type')=='submit' and c.get('name')=='add')
        context=self.chrome.request(self.conversation,'context',{'tab':self.tab,'observation':snapshot['observation'],'element':button['element'],'action':'click'},self.chrome.permissions.generation)
        receiver=context.get('form_action','');self.url(receiver)
        if context.get('form_method')!='POST' or not context.get('form_submission'):raise Denied('Product save contract is not verified')
        upload_receiver=snapshot.get('commerce',{}).get('upload_receiver')
        if upload_receiver!='https://pe56d.s3.amazonaws.com/':raise Denied('Payhip storage receiver changed; inspect and authorize it before any upload')
        assets={archive.name:{'relative':package['archive'],'sha256':package['sha256'],'bytes':archive.stat().st_size}}
        for name in ('Cover.png','Preview-1.png','Preview-2.png'):
            relative=package['product']+'/customer/'+name;path=factory.path(relative)
            if not path.is_file():raise Denied('Validated cover and two previews required')
            expected=package['files'].get(name,{})
            if digest(path)!=expected.get('sha256') or path.stat().st_size!=expected.get('bytes'):raise Denied('Image differs from the validated customer package')
            assets[name]={'relative':relative,'sha256':digest(path),'bytes':path.stat().st_size}
        return {'mode':'prepare_hidden','project':project,'store':'payhip-invisible-'+project,'products':{package['product']:{'sha256':package['sha256']}},'product':package['product'],'title':package['listing']['title'],'description':self.description(package),'sha256':package['sha256'],'bytes':archive.stat().st_size,'price_cents':package['listing']['price_cents'],'currency':'CAD','visibility':'invisible','max_new_products':1,'spending_limit_cents':0,'assets':assets,'archive_name':archive.name,'save_urls':[receiver],'upload_receivers':[upload_receiver],'max_blocked_transfer_retries':1,'expires':time.time()+3600,'baseline':self.probe_result['baseline']}

    @staticmethod
    def description(package):
        return package['listing']['description']+'\n\nIncludes an editable spreadsheet, step-by-step instructions and worksheet previews. Change the sample inputs for your business. No macros. Illustrative planning aid; not professional advice.'

    def prepare_hidden(self,package,archive,factory,cancel,verify_only=False):
        self.factory=factory;self.cancel=cancel
        package={**package,'listing':{**package['listing'],'currency':self.scope['currency']}}
        self.pending=package;self.guard(package);cancel()
        result=self.verify(self.lookup(None),package) if verify_only else self.prepare(package,archive)
        if not result.get('files_verified'):raise Denied(result.get('reason','Saved asset verification is incomplete'))
        return {'listing':result,'product':package['product'],'verified':True,'visibility':'invisible'}

    def guard(self,package):
        scope=self.scope
        if not scope or scope['expires']<time.time():raise Denied('First real Payhip account mutation needs separate owner authorization')
        if self.queue and not self.queue.rows('SELECT id FROM scopes WHERE id=? AND revoked=0 AND expires>?',(self.scope_id,time.time())):raise Denied('Payhip test authorization was revoked')
        if scope.get('sha256')!=package['sha256'] or scope.get('title')!=package['listing']['title'] or scope.get('price_cents')!=package['listing']['price_cents']:raise Denied('Payhip package/title/price is outside the approved single-product scope')
        if scope.get('currency')!='CAD':raise Denied('This verified first-test store currency is CAD; other currencies need a separately verified store contract')
        self.chrome.check(self.conversation)
        if getattr(self,'cancel',None):self.cancel()

    def checkpoint(self,phase,detail=None):
        self.guard(self.pending)
        if not self.queue:return
        key='payhip:'+self.project+':'+self.pending['product']
        value={'phase':phase,'tab':self.tab,'title':self.scope['title'],'recovery_attempts':getattr(self,'recovery_attempts',0),'client_save_rejections_recovered':getattr(self,'client_save_rejections_recovered',0),**(detail or {})}
        with self.queue.lock:
            self.queue.db.execute('INSERT OR REPLACE INTO effects VALUES(?,?,?,?,?,?,?,?)',(key,self.project,None,self.scope['store'],phase,self.pending['sha256'],json.dumps(value),time.time()))
            self.queue.event(self.project,None,'payhip_'+phase,value);self.queue.db.commit()

    def find(self,snapshot,predicate):
        controls=[c for c in snapshot.get('controls',[]) if predicate(c)]
        if len(controls)!=1:raise Denied('Payhip control is missing or ambiguous; inspected '+str(len(controls))+' matches')
        return controls[0]

    def act(self,predicate,operation,**values):
        self.guard(self.pending);snapshot=self.inspect();self.last_snapshot=snapshot;control=self.find(snapshot,predicate)
        args={'tab':self.tab,'observation':snapshot['observation'],'element':control['element'],'operation':operation,**values}
        self.expected={'observation':snapshot['observation'],'element':control['element'],'action':operation}
        try:
            with self.chrome.adapter_review(self.review):result=self.call('action',args)
        finally:self.expected=None
        return result

    def review(self,conversation,args,context,record,decision):
        self.guard(self.pending)
        if conversation!=self.conversation or not self.expected or any(args.get(k)!=v for k,v in self.expected.items()):return False
        if decision.category!='submission' or not context.get('page_url','').startswith('https://payhip.com/product/'):return False
        if record:
            return record['sha256'] in {a['sha256'] for a in self.scope['assets'].values()} and context.get('type')=='file' and context.get('form_visibility')=='invisible'
        # A new inspect here would invalidate the control being reviewed.
        return context.get('form_submission') and context.get('form_method')=='POST' and context.get('form_visibility')=='invisible' and context.get('form_action') in self.scope['save_urls'] and self.verify_fields(self.last_snapshot)

    def verify_fields(self,snapshot):
        controls=snapshot.get('controls',[])
        title=next((c.get('value') for c in controls if c.get('name')=='p_name'),None)
        price=next((c.get('value') for c in controls if c.get('name')=='p_price'),None)
        hidden=any(c.get('name')=='product_status' and c.get('value')=='invisible' and c.get('checked') for c in controls)
        try:correct=Decimal(str(price))*100==self.scope['price_cents']
        except Exception:correct=False
        description=True
        if self.scope.get('description'):
            editors=[c for c in controls if c.get('editable')]
            description=len(editors)==1 and ' '.join(editors[0].get('value','').split())==' '.join(self.scope['description'].split())
        return title==self.scope['title'] and correct and hidden and description

    def lookup(self,key):
        if getattr(self,'products_tab',None) is None:
            snapshot=self.open('https://payhip.com/products');self.products_tab=self.tab
        else:
            self.tab=self.products_tab;self.call('reload',{'tab':self.tab});time.sleep(.4);snapshot=self.inspect()
        # Bind the first write to the account actually inspected by the owner.
        # Never create first and only discover the wrong account during verification.
        baseline=self.scope.get('baseline',{}).get('calculator_controls',[])
        if not baseline:raise Denied('Original store fingerprint is missing; no account write is permitted')
        def baseline_matches(current):
            return all(len(found:=[c for c in current.get('controls',[]) if c.get('href')==old.get('href') and c.get('label')==old.get('label')])==1 and 'HIDDEN' in found[0].get('nearby','').upper() for old in baseline)
        # A reload can return an intermediate document. Wait for the previously
        # observed account identity without treating a loading page as absence.
        for _ in range(20):
            if baseline_matches(snapshot):break
            time.sleep(.2);snapshot=self.inspect()
        if not baseline_matches(snapshot):raise Denied('The authorized store/account fingerprint changed or did not finish loading; stop before uploads or save')
        def candidate(control):
            label=control.get('label','').strip()
            if label==self.scope['title']:return True
            # Payhip visually truncates product titles. This is only a candidate:
            # verify() must reopen its observed Edit link and match full fields.
            prefix=re.sub(r'(?:\.\.\.|\u2026)$','',label).rstrip()
            return prefix!=label and len(prefix)>=24 and self.scope['title'].startswith(prefix)
        controls=[c for c in snapshot['controls'] if candidate(c) and c.get('href')]
        if len(controls)>1:raise Denied('Duplicate matching Payhip listings exist; do not create another')
        if not controls:return None
        selected=controls[0];nearby=selected.get('nearby','')
        if 'HIDDEN' not in nearby.upper():raise Denied('Matching product is not verified HIDDEN; no publication/visibility change is allowed by this test')
        public=selected['href'];identifier=urlsplit(public).path.rsplit('/',1)[-1]
        edit=next((c.get('href') for c in snapshot['controls'] if c.get('href','').endswith('/product/edit/'+identifier)),None)
        if not edit:
            edit=next((c.get('href') for c in snapshot['controls'] if c.get('label','').strip().lower()=='edit' and self.scope['title'] in c.get('nearby','')),None)
        return {'title':self.scope['title'],'url':public,'edit_url':edit,'visibility':'invisible','price_cents':self.scope['price_cents'],'currency':self.scope['currency'],'product':self.pending['product'],'sha256':self.pending['sha256']}

    def upload(self,path,name,kind):
        if digest(path)!=self.scope['assets'][name]['sha256']:raise Denied('Approved upload asset changed')
        record=self.attachments.add(path);record['name']=name;record['_upload_receivers']=self.scope.get('upload_receivers',[])
        self.guard(self.pending);snapshot=self.inspect()
        if not self.verify_fields(snapshot):raise Denied('Listing fields changed before upload; no file was transferred')
        initial_images=len(snapshot.get('images',[]));files=[c for c in snapshot['controls'] if c.get('type')=='file']
        if kind=='product':
            candidates=[c for c in files if not c.get('accept','').startswith('image/')]
            target=candidates[0] if candidates else None
        else:
            candidates=[c for c in files if c.get('accept','').startswith('image/') or 'product image' in c.get('nearby','').lower()]
            target=candidates[-1] if candidates else files[-1] if len(files)>1 else None
        if not target:raise Denied('Verified '+kind+' upload control is unavailable')
        self.expected={'observation':snapshot['observation'],'element':target['element'],'action':'upload'}
        try:
            with self.chrome.adapter_review(self.review):
                result=self.chrome.call(self.conversation,'action',{'tab':self.tab,'observation':snapshot['observation'],'element':target['element'],'operation':'upload','attachment_id':record['id']},{record['id']:record})
        finally:self.expected=None
        self.checkpoint('asset_selected',{'name':name,'sha256':record['sha256'],'receipt':result})
        deadline=time.monotonic()+90
        while time.monotonic()<deadline:
            self.guard(self.pending);current=self.inspect();text=current.get('text','')
            if re.search(r'(?:upload failed|upload error|unsupported file|file type is not allowed)',text,re.I):raise Denied('Payhip reported an upload failure; no save was attempted')
            receipts=current.get('commerce',{}).get('digital_files',[])
            complete=current.get('commerce',{}).get('upload_in_progress') is False
            if kind=='product' and complete and any(f.get('name')==name and f.get('bytes')==path.stat().st_size and f.get('receipt') for f in receipts):return
            if kind=='image' and complete and any(f.get('name')==name and f.get('bytes')==path.stat().st_size and f.get('receipt') for f in current.get('commerce',{}).get('cover_images',[])):return
            time.sleep(.5)
        raise Denied('Upload completion is uncertain; do not repeat it without inspecting this exact editor')

    def prepare(self,package,archive):
        with self.lock:
            self.pending=package;self.guard(package)
            if digest(archive)!=package['sha256']:raise Denied('Payhip delivery changed after authorization')
            existing=self.lookup(None)
            if existing:return self.verify(existing,package)
            key='payhip:'+self.project+':'+package['product']
            previous=self.queue.rows('SELECT * FROM effects WHERE key=?',(key,)) if self.queue else []
            self.completed_assets=set()
            if previous:self.reconcile_blocked_transfer(previous[0],package)
            else:
                snapshot=self.open(self.probe_result['new_product_url'])
                if not any(c.get('name')=='product_status' and c.get('value')=='invisible' for c in snapshot['controls']):raise Denied('Invisible control not exposed before upload; no account mutation attempted')
                self.checkpoint('preparing')
                self.act(lambda c:c.get('name')=='product_status' and c.get('value')=='invisible','check',checked=True)
                if not any(c.get('name')=='product_status' and c.get('value')=='invisible' and c.get('checked') for c in self.inspect()['controls']):raise Denied('Invisible was not selected; stop before uploads/save')
                self.act(lambda c:c.get('name')=='p_name','fill',text=self.scope['title'])
                self.act(lambda c:c.get('name')=='p_price','fill',text=f"{self.scope['price_cents']/100:.2f}")
                description=self.description(package)
                snapshot=self.inspect();editors=[c for c in snapshot['controls'] if c.get('editable')]
                if len(editors)!=1:raise Denied('Description editor is not uniquely available; stop before uploads/save')
                editor=editors[0];self.act(lambda c:c.get('element')==editor['element'],'fill',text=description)
            if self.scope['archive_name'] not in self.completed_assets:self.upload(archive,self.scope['archive_name'],'product')
            for name,asset in self.scope['assets'].items():
                if name==self.scope['archive_name'] or name in self.completed_assets:continue
                self.upload(self.factory.path(asset['relative']),name,'image')
            if not self.verify_fields(self.inspect()):raise Denied('Title, price or Invisible changed; no product submission occurred')
            self.checkpoint('create_submitted')
            self.act(lambda c:c.get('type')=='submit' and c.get('name') in ('add','update','save'),'click')
            time.sleep(.7);self.checkpoint('reconciling')
            deadline=time.monotonic()+30
            while time.monotonic()<deadline:
                listing=self.lookup(None)
                if listing:
                    verified=self.verify(listing,package)
                    self.checkpoint('verified' if verified.get('files_verified') else 'verification_incomplete',verified);return verified
                time.sleep(1)
            raise Denied('Saved listing not confirmed. No creation/upload was repeated; inspect the Products page before retry')

    def reconcile_blocked_transfer(self,effect,package):
        prior=json.loads(effect['result'])
        client_rejected=prior.get('phase')=='reconciling' and prior.get('client_save_rejections_recovered',0)==0
        if effect['fingerprint']!=package['sha256'] or (not client_rejected and (prior.get('phase')!='asset_selected' or prior.get('name') not in self.scope['assets'])) or prior.get('recovery_attempts',0) not in (0,1) or self.scope.get('max_blocked_transfer_retries')!=1 or self.scope.get('upload_receivers')!=['https://pe56d.s3.amazonaws.com/']:raise Denied('Prior external attempt cannot be safely reconciled under this bounded storage authorization')
        # Genuine local existing-tab approval is required; no forged user message
        # or model-supplied permission flag is used to recover the saved editor.
        tab=prior['tab'];self.chrome.call(self.conversation,'adopt_tab',{'query':'payhip.com/product/add/digital','tab':tab});self.tab=tab;snapshot=self.inspect()
        commerce=snapshot.get('commerce',{})
        if prior.get('recovery_attempts',0)==1:
            if snapshot.get('url')!=self.probe_result['new_product_url'] or not self.verify_fields(snapshot) or commerce.get('digital_files_state')!='valid' or commerce.get('cover_images_state')!='valid':raise Denied('Original editor or receipt inventory changed; no transfer was repeated')
            files=commerce.get('digital_files',[])
            if len(files)!=1 or files[0].get('name')!=self.scope['archive_name'] or files[0].get('bytes')!=self.scope['bytes'] or not files[0].get('receipt'):raise Denied('The consumed archive retry has no unique completed receipt; no further retry is allowed')
            completed={self.scope['archive_name']}
            for receipt in commerce.get('cover_images',[]):
                name=receipt.get('name');expected=self.scope['assets'].get(name)
                if name in completed or not expected or not receipt.get('receipt') or receipt.get('bytes')!=expected['bytes']:raise Denied('Image receipt differs from the approved asset inventory')
                actual=self.chrome.request(self.conversation,'asset_digest',{'tab':tab,'observation':snapshot['observation'],'kind':'uploaded_image','asset':receipt['asset']},self.chrome.permissions.generation)
                if actual.get('sha256')!=expected['sha256'] or actual.get('bytes')!=expected['bytes']:raise Denied('Completed image bytes differ; no transfer was repeated')
                completed.add(name)
            if client_rejected:
                # A visible, documented pre-submit validation rejection is not an
                # uncertain server commit. Let the site's own progress flag clear;
                # never set it or bypass its validation/authentication checks.
                if completed!=set(self.scope['assets']) or commerce.get('upload_in_progress') is not False or 'Please wait there are files still being uploaded.' not in snapshot.get('text',''):raise Denied('The previous submit was not a verified local upload-progress rejection; do not submit again')
                self.client_save_rejections_recovered=1
                self.act(lambda c:c.get('label','').strip()=='OK','click')
            elif prior['name'] not in completed:raise Denied('The last selected asset has no completed verified receipt; it cannot be uploaded again')
            self.recovery_attempts=1;self.completed_assets=completed;self.checkpoint('resuming_completed_receipts',{'confirmed_assets':sorted(completed),'no_completed_uploads_repeated':True,'local_validation_rejection_resolved':client_rejected});return
        if snapshot.get('url')!=self.probe_result['new_product_url'] or not self.verify_fields(snapshot) or commerce.get('upload_receiver')!='https://pe56d.s3.amazonaws.com/' or commerce.get('digital_files_state')!='valid' or commerce.get('digital_files'):raise Denied('The original editor or empty upload-receipt state changed; no retry was issued')
        if self.scope['archive_name'] not in snapshot.get('text','') or 'Uploading' not in snapshot.get('text',''):raise Denied('The original blocked transfer is not uniquely recognizable')
        self.recovery_attempts=1
        self.checkpoint('blocked_transfer_retry_authorized',{'prior_phase':prior['phase'],'completed_receipts_before_retry':0,'receiver':'https://pe56d.s3.amazonaws.com/','scope':self.scope_id})

    def verify(self,listing,package):
        if not listing or listing['visibility']!='invisible' or listing['title']!=self.scope['title']:raise Denied('Saved listing identity/Invisible mismatch')
        if not listing.get('edit_url'):raise Denied('Saved listing Edit link not uniquely observed; cannot verify saved fields/files')
        snapshot=self.open(listing['edit_url'])
        for _ in range(25):
            if self.verify_fields(snapshot):break
            time.sleep(.2);snapshot=self.inspect()
        if not self.verify_fields(snapshot):raise Denied('Reopened Payhip title/price/Invisible mismatch')
        for _ in range(40):
            if self.scope['archive_name'] in snapshot.get('text',''):break
            time.sleep(.2);snapshot=self.inspect()
        if self.scope['archive_name'] not in snapshot.get('text',''):raise Denied('Saved delivery filename not visible in reopened editor')
        # Download links may load after the initial editor and may be outside
        # the first bounded controls page. Search the live observed controls.
        for _ in range(25):
            snapshot=self.inspect()
            matches=[c for c in snapshot['controls'] if c.get('href') and (self.scope['archive_name'] in c.get('label','') or 'download' in c.get('label','').lower() or '/product/download/' in c.get('href',''))]
            if matches:break
            time.sleep(.2)
        delivery=None
        for control in matches:
            self.guard(package)
            actual=self.chrome.request(self.conversation,'asset_digest',{'tab':self.tab,'observation':snapshot['observation'],'element':control['element'],'kind':'delivery'},self.chrome.permissions.generation)
            if actual.get('sha256')==package['sha256'] and actual.get('bytes')==self.scope['bytes']:delivery=actual;break
        if not delivery:raise Denied('Saved delivery bytes are not independently verified; creation will not be repeated')
        snapshot=self.inspect()
        expected={name:asset for name,asset in self.scope['assets'].items() if name!=self.scope['archive_name']}
        verified={}
        for observed in snapshot.get('commerce',{}).get('cover_images',[]):
            self.guard(package)
            name=observed.get('name');asset=expected.get(name)
            if not asset or name in verified:raise Denied('Saved image identity is unexpected or duplicated')
            actual=self.chrome.request(self.conversation,'asset_digest',{'tab':self.tab,'observation':snapshot['observation'],'asset':observed['asset'],'kind':'uploaded_image'},self.chrome.permissions.generation)
            if actual.get('sha256')!=asset['sha256'] or actual.get('bytes')!=asset['bytes']:raise Denied('Saved original image differs from its approved bytes')
            verified[name]={'sha256':actual['sha256'],'bytes':actual['bytes']}
        if set(verified)!=set(expected):raise Denied('Reopened saved cover/two previews are not all verified; no upload or creation was repeated')
        baseline=self.open('https://payhip.com/products')
        for old in self.scope['baseline'].get('calculator_controls',[]):
            controls=[c for c in baseline['controls'] if c.get('href')==old.get('href') and c.get('label')==old['label']]
            if len(controls)!=1 or 'HIDDEN' not in controls[0].get('nearby','').upper() or not re.search(r'29[.,]00',controls[0].get('nearby','')):raise Denied('Original calculator identity/HIDDEN/price could not be reverified')
        return {**listing,'saved_fields_verified':True,'files_verified':True,'delivery':delivery,'images':verified,'original_calculator_unchanged':True}
