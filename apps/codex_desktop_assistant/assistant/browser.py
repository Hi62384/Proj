"""Dedicated Playwright profile. Never attaches to or reads ordinary browser secrets."""
import uuid
import time
import re
from urllib.parse import urljoin,urlsplit,urlunsplit
from pathlib import Path
from .permissions import Denied, origin
from .action_policy import classify,request_review
from .web_policy import WebsiteAccess,network_intent,safe_text,SECRET_KEY

CONTROLS='button:visible,input:not([type=hidden]):visible,textarea:visible,select:visible,a:visible,[role=button]:visible,[role=checkbox]:visible,[contenteditable=true]:visible,[role=textbox]:visible'


def display_url(url):
    p=urlsplit(url)
    # OAuth codes, signed queries and fragments never enter model messages/logs.
    return urlunsplit((p.scheme,p.netloc,p.path,'',''))


class Browser:
    def __init__(self, directory, permissions):
        self.directory=Path(directory);self.permissions=permissions
        self.runtime=self.context=None;self.page=None;self.observation=None
        self.last_error='';self.downloads=[];self.elements=[];self.observed_at=0
        self.manual_mode=False
        self.uploads={}
        self.redirect_target=None
        self.value_signatures={}
        self.ask=None;self.access=WebsiteAccess(permissions,lambda label,args:self.ask(label,args) if self.ask else False)
        self.page_ids={};self.next_tab=0;self.element_frames={};self.background=True;self.diagnostics=[]
        self.edit_until=0;self.review_lease=None;self.anonymous=None;self.resource_grants=set()
        self.configured=set();self.denied_network=set()
        self.navigation_tabs={};self.pending_visits={}
        self.blocked_pages={}

    @property
    def review_blocked(self):
        return self.blocked_pages.get(self.tab_id() if self.page else None,'')

    @review_blocked.setter
    def review_blocked(self,value):
        self.blocked_pages[self.tab_id() if self.page else None]=value

    def start(self):
        if not self.permissions.browser:raise Denied('Browser control is off')
        if self.context:return
        from playwright.sync_api import sync_playwright
        self.runtime=sync_playwright().start()
        try:
            self.context=self.runtime.chromium.launch_persistent_context(str(self.directory/'browser-profile'),
                headless=False,service_workers='block',accept_downloads=True,
                args=['--disable-backgrounding-occluded-windows','--disable-renderer-backgrounding','--disable-background-timer-throttling'])
            self.context.set_default_timeout(1500)
            self.context.route('**/*',self.route)
            self.context.route_web_socket('**/*',lambda ws:ws.close(code=1008,reason='Page origin not established'))
            self.anonymous=self.runtime.request.new_context()
            self.context.on('page',self.configure)
            self.page=self.context.pages[0] if self.context.pages else self.context.new_page()
            for existing in self.context.pages:self.configure(existing)
            self.refresh_processes()
        except Exception:
            self.close();raise

    def tab_id(self,page=None):
        page=page or self.page
        if page not in self.page_ids:self.page_ids[page]=self.next_tab;self.next_tab+=1
        return self.page_ids[page]

    def effective_url(self,page=None):
        page=page or self.page
        for _ in range(4):
            if page is None:return ''
            if page.url.startswith(('http://','https://')):return page.url
            page=page.opener()
        return ''

    def authorize(self,url,reason='The task needs to browse this website.',force=False,page=None):
        self.access.authorize(url,self.tab_id(page),reason,force)
        # Fulfilled navigations have no native network address-space metadata.
        # Chromium consequently asks for local-network permission even for a
        # same-origin loopback socket. Grant it only to an explicitly authorized
        # local site; HTTP routes still validate every receiving origin.
        if self.context and self.access.full(url,self.tab_id(page)):
            import ipaddress
            host=urlsplit(url).hostname
            try:local=not ipaddress.ip_address(host).is_global
            except ValueError:local=host=='localhost' or host.endswith(('.localhost','.local','.internal'))
            key=('local-network',origin(url))
            if local and key not in self.resource_grants:
                try:self.context.grant_permissions(['local-network-access'],origin=origin(url));self.resource_grants.add(key)
                except Exception:self.blocked(url,'This Chromium version cannot grant local-network access; local realtime connections may need manual browser permission.','compatibility')

    def blocked(self,url,reason,kind='request'):
        try:destination=origin(url.replace('wss:','https:',1).replace('ws:','http:',1))
        except Exception:destination='unsupported address'
        item={'origin':destination,'kind':kind,'reason':safe_text(reason)[:500]}
        if not self.diagnostics or self.diagnostics[-1]!=item:self.diagnostics.append(item)
        self.diagnostics=self.diagnostics[-40:];self.last_error=destination+': '+item['reason']

    def ask_network(self,label,details):
        epoch=self.permissions.generation
        key=(self.permissions.generation,label,details.get('approval_reason',''))
        if key in self.denied_network:raise Denied('This network operation was already denied; no repeat request will be sent')
        if not self.ask:raise Denied(details['approval_reason'])
        if not self.ask(label,details):
            self.denied_network.add(key);raise Denied('Owner denied: '+details['approval_reason'])
        if epoch!=self.permissions.generation or self.permissions.halted.is_set() or self.permissions.cancelled():raise Denied('Network approval expired before dispatch')

    def proof(self,destination,consume=True,url=None,method=None):
        lease=self.review_lease
        valid=lease and lease['origin']==destination and lease['epoch']==self.permissions.generation and time.monotonic()<lease['until'] and not lease['used']
        if valid and lease.get('url'):valid=bool(url and display_url(url)==lease['url'] and method==lease['method'])
        if valid and consume:lease['used']=True
        return bool(valid)

    def connection_access(self,url,source,tab,reason):
        target=origin(url);pair=(source,target)
        if (tab,*pair) in self.access.data_pairs or pair in self.permissions.browser_data_pairs:return
        self.ask_network('Allow data connection to '+target,{'website_access':True,'permission_kind':'data_connection','operation':'website_access',
            'origin':target,'source_origin':source,'reason':reason,'approval_reason':'This website will receive data from '+source+'. Rendering-resource permission alone does not grant this data connection.'})
        self.access.data_pairs.add((tab,*pair))

    def route(self, route):
        request=route.request
        try:
            if not self.permissions.browser or (self.permissions.halted.is_set() and not self.manual_mode):raise Denied('Browser authorization is stopped or revoked')
            try:
                page=request.frame.page;tab=self.tab_id(page)
                top=request.is_navigation_request() and request.frame==page.main_frame
                root=self.effective_url(page)
            except Exception:
                # Chromium's first popup request can precede its Page/Frame.
                # Reserve a visit identity, authorize before dispatch, and bind
                # it to the resulting page once Chromium creates that page.
                if not request.is_navigation_request():raise Denied('The request has no verifiable page')
                page=None;top=True
                tab=self.navigation_tabs.get(request.redirected_from)
                if tab is None:tab=self.next_tab;self.next_tab+=1
                self.navigation_tabs[request]=tab;self.pending_visits[tab]=request.url
                root=request.headers.get('referer','')
            source=origin(root) if root else origin(request.url)
            destination=origin(request.url)
            if top:
                if page:self.authorize(request.url,'Navigate or follow a redirect to this website.',page=page)
                else:self.access.authorize(request.url,tab,'A new browser window is opening this website.')
            elif not self.access.available(root,tab):
                raise Denied('The initiating page is no longer authorized')
            body=request.post_data_buffer
            content_type=request.headers.get('content-type','')
            intent=network_intent(request.method,request.url,body,content_type)
            navigation_submit=request.is_navigation_request() and request.method not in ('GET','HEAD','OPTIONS')
            manual=self.manual_mode or self.permissions.browser_manual
            full=self.access.full(request.url,tab)
            private_query=any(SECRET_KEY.search(key) for key in __import__('urllib.parse',fromlist=['parse_qs']).parse_qs(urlsplit(request.url).query))
            cross=source!=destination and not top
            if cross and not full:
                if intent.kind=='read' and request.method in ('GET','HEAD','OPTIONS') and request.resource_type not in ('xhr','fetch','eventsource') and not private_query and self.access.rendering(request.url,tab):pass
                else:self.connection_access(request.url,source,tab,'A required API, embedded app or resource needs a data-bearing connection.')
            if intent.kind=='credentials' and not manual:raise Denied('Authentication/payment fields require Manual Control; no credential payload was forwarded')
            if intent.kind=='refresh' and not full and not manual:self.authorize(request.url,'This sign-in service needs explicit session access for token refresh.',force=True,page=page)
            review=intent.kind in ('consequential','unknown') or navigation_submit
            if intent.kind=='unknown' and self.permissions.public_browsing and not full and not manual and not navigation_submit and not self.proof(destination,consume=False,url=request.url,method=request.method):
                raise Denied('Public research access does not permit opaque background writes. Explicitly authorize this website for account work if this operation is required.')
            if review and not manual:
                if not self.proof(destination,url=request.url,method=request.method):
                    reason=intent.reason or 'This request submits a form or may change website data.'
                    self.ask_network('Review website request to '+destination,{'operation':'network_request','approval_reason':reason,'target_context':{'source':'browser','page_url':display_url(root),'destination':destination,'method':request.method},'body_bytes':len(body or b'')})
            elif intent.kind=='draft' and not manual:
                if time.monotonic()>self.edit_until or not self.access.full(request.url,tab):
                    self.authorize(request.url,'Allow routine draft/account editing for this explicitly requested workflow.',force=True,page=page)
                    if time.monotonic()>self.edit_until:
                        self.ask_network('Review draft update on '+destination,{'operation':'network_request','approval_reason':'A draft update occurred outside a recent owner-requested edit.','target_context':{'destination':destination}})
            # Cross-origin rendering uses a cookie-free API context, so an asset
            # permission cannot forward or overwrite another site's stored login.
            anonymous=not self.access.full(request.url,tab) and (cross or self.permissions.public_browsing) and (tab,source,destination) not in self.access.data_pairs and (source,destination) not in self.permissions.browser_data_pairs
            headers=request.all_headers()
            options={'max_redirects':0,'max_retries':0,'timeout':15000}
            if 'multipart/form-data' in content_type and self.uploads:body=self.multipart(request,content_type)
            if anonymous:
                headers={k:v for k,v in headers.items() if k.lower() not in ('cookie','authorization','proxy-authorization','host','content-length','referer')}
                response=self.anonymous.fetch(request.url,method=request.method,headers=headers,data=body,**options)
            else:
                options['post_data']=body
                response=route.fetch(**options)
            if response.status in (301,302,303,307,308):
                destination_url=urljoin(request.url,response.headers.get('location',''))
                if top:
                    self.access.authorize(destination_url,tab,'The website redirects to this origin; sign-in data may be carried by the browser.')
                    if page is None:self.pending_visits[tab]=destination_url
                elif not self.access.available(destination_url,tab) and not self.access.rendering(destination_url,tab):raise Denied('Redirect destination is not authorized')
                if response.status in (307,308) and request.method not in ('GET','HEAD','OPTIONS') and origin(destination_url)!=destination:
                    self.connection_access(destination_url,destination,tab,'This redirect preserves a request body across websites.')
            response_headers=dict(response.headers)
            if anonymous:response_headers.pop('set-cookie',None)
            if self.permissions.halted.is_set() or not self.permissions.browser:raise Denied('Stopped before response delivery')
            route.fulfill(status=response.status,headers=response_headers,body=response.body())
        except Exception as error:
            reason=str(error) if isinstance(error,Denied) else 'Browser transport failed: '+type(error).__name__
            self.blocked(request.url,reason)
            self.blocked_pages[locals().get('tab',self.tab_id() if self.page else None)]=reason
            try:route.fulfill(status=403,content_type='text/html',body='<html><title>Browser access needs review</title><p>A request was blocked by the local browser policy. Review the assistant activity.</p></html>')
            except Exception:route.abort('blockedbyclient')

    def websocket(self,ws,page):
        url=ws.url.replace('wss:','https:',1).replace('ws:','http:',1)
        try:
            if not self.permissions.browser or self.permissions.halted.is_set():raise Denied('Browser input is stopped')
            tab=self.tab_id(page);root=self.effective_url(page);source=origin(root)
            if not self.access.available(root,tab):raise Denied('The initiating page is unauthorized')
            if origin(url)!=source and not self.access.full(url,tab):self.connection_access(url,source,tab,'This page needs a realtime WebSocket data connection.')
            server=ws.connect_to_server()
            def message(value):
                try:
                    if self.permissions.halted.is_set() or not self.permissions.browser:raise Denied('Stopped before realtime dispatch')
                    intent=network_intent('POST',url,value,'application/json')
                    manual=self.manual_mode or self.permissions.browser_manual
                    if intent.kind=='credentials' and not manual:raise Denied('Realtime credentials require manual control')
                    if intent.kind not in ('read','refresh') and not manual and not self.proof(origin(url)):
                        self.ask_network('Review realtime message to '+origin(url),{'operation':'websocket_message','approval_reason':intent.reason or 'This realtime message may change data.','target_context':{'destination':origin(url)},'message_bytes':len(value)})
                    server.send(value)
                except Exception as error:self.blocked(url,str(error),'websocket');ws.close(code=1008,reason='Local owner review required')
            ws.on_message(message)
        except Exception as error:self.blocked(url,str(error),'websocket');ws.close(code=1008,reason='Local authorization required')

    def configure(self, page):
        if page in self.configured:return
        self.configured.add(page)
        page.route_web_socket('**/*',lambda ws:self.websocket(ws,page))
        self.tab_id(page)
        page.on('close',lambda _:self.access.leave(self.tab_id(page)))
        def navigated(frame):
            if frame!=page.main_frame:return
            for tab,url in list(self.pending_visits.items()):
                if page.url==url:
                    self.page_ids[page]=tab;self.pending_visits.pop(tab,None);break
            if page==self.page:self.observation=None
        page.on('framenavigated',navigated)
        navigated(page.main_frame)
        page.on('dialog',lambda dialog:dialog.dismiss())
        page.on('pageerror',lambda error:setattr(self,'last_error',safe_text(str(error))[:300]))
        page.on('download',self.download)

    def download(self, download):
        directory=self.directory/'downloads';directory.mkdir(exist_ok=True)
        # Suggested filenames never determine destination paths and nothing executes.
        path=directory/(uuid.uuid4().hex+Path(download.suggested_filename).suffix[:12])
        download.save_as(path);self.downloads.append({'name':download.suggested_filename,'path':str(path)})

    def inspect(self):
        for attempt in range(3):
            try:return self._inspect_once()
            except Exception as error:
                self.observation=None
                if attempt==2 or not any(x in str(error) for x in ('Execution context was destroyed','Cannot find context')):raise
                # Read-only retry after navigation; never replay the action.
                self.page.wait_for_load_state('domcontentloaded',timeout=5000)
                self.page.wait_for_timeout(100)

    def tabs(self):
        if not self.context:return []
        result=[]
        for page in self.context.pages:
            if page.is_closed():continue
            url=self.effective_url(page)
            allowed=bool(url and self.access.available(url,self.tab_id(page)))
            try:title=safe_text(page.title())[:200] if allowed else 'Website needs authorization' if url else 'New tab'
            except Exception:title='Loading…'
            result.append({'tab':self.tab_id(page),'url':display_url(url) if url else 'about:blank','title':title,'authorized':allowed,'active':page==self.page})
        return result

    def _inspect_once(self):
        if not self.page or self.page.is_closed():
            pages=[p for p in self.context.pages if not p.is_closed()]
            self.page=pages[0] if pages else self.context.new_page()
        url=self.effective_url();tab=self.tab_id()
        if not url:return {'url':'about:blank','title':'New tab','text':'','controls':[],'tabs':self.tabs(),'diagnostics':self.diagnostics[-10:]}
        self.authorize(url,'Inspect the current website.')
        self.observation=uuid.uuid4().hex;self.observed_at=time.monotonic();self.elements=[];self.element_frames={};self.value_signatures={}
        controls=[];frames=[];texts=[]
        script="""(e,i)=>{const label=(e.getAttribute('aria-label')||e.labels?.[0]?.innerText||e.innerText||e.placeholder||e.name||'').slice(0,300);
            const privateField=e.type==='password'||/password|secret|token|one.?time|card.?number|cvv|cvc|security code|verification code/i.test(label+' '+e.autocomplete);
            return {element:i,tag:e.tagName,role:e.getAttribute('role'),type:e.type||'',label,value:privateField?'[private]':(e.isContentEditable?e.innerText:e.value||'').slice(0,1000),private:privateField,
                editable:e.isContentEditable,checked:e.checked,disabled:e.disabled,options:e.tagName==='SELECT'?[...e.options].slice(0,100).map(x=>({value:x.value,label:x.label})):undefined}}"""
        for frame_index,frame in enumerate(self.page.frames[:16]):
            frame_url=frame.url if frame.url.startswith(('https://','http://')) else url
            allowed=self.access.available(frame_url,tab) or origin(frame_url) in self.access.resources.get(tab,set())
            frames.append({'frame':frame_index,'url':display_url(frame_url),'authorized':allowed})
            if not allowed:continue
            try:
                text=safe_text(frame.locator('body').inner_text(timeout=1000))[:12000];texts.append(text)
                for element in frame.locator(CONTROLS).element_handles()[:max(0,200-len(controls))]:
                    i=len(self.elements);item=element.evaluate(script,i);item['frame']=frame_index;item['label']=safe_text(item['label']);item['value']=safe_text(item['value'])
                    self.elements.append(element);self.element_frames[i]=frame;controls.append(item)
                    if not item['private'] and (item.get('type') in ('text','email','number','search','tel','url','checkbox','radio','textarea','select-one','select-multiple') or item['editable'] or item['tag'] in ('TEXTAREA','SELECT')):
                        self.value_signatures[i]=(item['value'],item.get('checked'))
            except Exception as error:
                frames[-1]['status']='Frame not ready: '+type(error).__name__
        return {'url':display_url(url),'title':safe_text(self.page.title())[:300],'observation':self.observation,'text':'\n\n'.join(texts)[:24000],
                'controls':controls,'frames':frames,'error':self.last_error,'diagnostics':self.diagnostics[-10:],'tabs':self.tabs(),'downloads':self.downloads[-10:],
                'manual_control':self.permissions.browser_manual,'background':self.background}

    def action_context(self,args):
        element=self.target(args)
        context=element.evaluate('''(e,op)=>{
            const label=x=>(x.getAttribute('aria-label')||x.labels?.[0]?.innerText||x.innerText||x.placeholder||x.name||'').slice(0,300);
            const f=e.form||e.closest('form'),tag=e.tagName,type=(e.type||'').toLowerCase();
            const submit=(tag==='BUTTON'&&type==='submit')||(tag==='INPUT'&&['submit','image'].includes(type));
            const textInput=tag==='INPUT'&&!['button','submit','image','checkbox','radio','file','reset'].includes(type);
            const submitting=!!f&&((op==='click'&&submit)||(op==='press'&&(submit||textInput)));
            return {source:'browser',label:label(e),tag,type,editable:tag==='TEXTAREA'||textInput||e.isContentEditable,
                role:tag==='BUTTON'||tag==='INPUT'&&['submit','image','button'].includes(type)?'Button':(['INPUT','TEXTAREA'].includes(tag)?'Edit':tag==='A'?'Hyperlink':tag==='SELECT'?'ComboBox':e.getAttribute('role')||''),
                form_submission:submitting,form_method:f?(f.method||'get').toUpperCase():'',form_action:f?f.action:'',
                form_submit_labels:f?[...f.querySelectorAll('button,input[type=submit],input[type=image]')].slice(0,160).filter(x=>x.type==='submit'||x.type==='image').map(label):[],
                enter_submits:e.enterKeyHint==='send',credential_form:!!f&&!!f.querySelector('input[type=password],input[autocomplete="new-password"],input[autocomplete="current-password"]'),href:e.href||''};
        }''',args['operation'])
        context['key']=args.get('key','');context['page_url']=display_url(self.element_frames.get(int(args.get('element',0)),self.page).url)
        # A known send/publish submit control is stronger evidence than newline
        # characters or the name of the editable field.
        from .action_policy import commit_label
        if args['operation']=='press' and args.get('key')=='Enter':
            context['enter_submits']=context['enter_submits'] or any(commit_label(label).required for label in context.get('form_submit_labels',[]))
        if context.get('form_action'):context['form_action']=display_url(context['form_action'])
        if context.get('href'):context['href']=display_url(context['href'])
        context['label']=safe_text(context['label'])
        return context

    def call(self, args, approved=False):
        if self.permissions.cancelled():raise Denied('Originating turn ended; action cancelled')
        if self.permissions.browser_manual or self.permissions.manual_requests:raise Denied('The owner has Manual Control. Return control before automated browser inspection or input.')
        if self.permissions.halted.is_set():raise Denied('Browser automation is stopped; explicitly Continue or open the browser to start a new session')
        op=args['operation']
        if op in ('navigate','new_tab'):
            url=args['url'];tab=self.tab_id() if self.page else self.next_tab
            if not self.page:self.access.authorize(url,tab,args.get('reason','The task needs this website.'),args.get('authorize',False));self.permissions.browser=True
        self.start()
        if op in ('navigate','new_tab'):self.permissions.browser=True
        if args.get('operation')=='check' and type(args.get('checked')) is not bool:raise ValueError('checked must be a JSON boolean')
        self.owner_reviewed=approved;self.review_blocked='';self.submission_allowed=True
        try:
            if op=='navigate':
                self.uploads.clear();self.goto(args['url'],args.get('reason','Navigate to this website.'),args.get('authorize',False))
            elif op=='new_tab':
                self.page=self.new_page();self.configure(self.page);self.goto(args['url'],args.get('reason','Open a new website tab.'),args.get('authorize',False))
            elif op=='switch_tab':
                self.page=self.resolve_tab(args['tab']);self.observation=None
            elif op=='close_tab':
                target=self.resolve_tab(args.get('tab',self.tab_id()));target.close()
                remaining=[p for p in self.context.pages if not p.is_closed()];self.page=remaining[0] if remaining else self.context.new_page();self.observation=None
            elif op in ('back','forward','reload'):
                self.observation=None
                getattr(self.page,{'back':'go_back','forward':'go_forward','reload':'reload'}[op])(wait_until='domcontentloaded',timeout=20000)
            elif op=='wait':self.page.wait_for_timeout(max(0,min(5000,int(args.get('milliseconds',500)))))
            elif op=='tabs':return {'tabs':self.tabs()}
            elif op=='inspect':return self.inspect()
            elif op=='screenshot':return self.screenshot()
            elif op=='scroll':
                if args.get('observation')!=self.observation:raise Denied('Inspect before scrolling')
                self.page.mouse.wheel(0,max(-2000,min(2000,int(args['amount']))));self.observation=None
            else:
                self.authorize(self.effective_url(),'Interact with this website.')
                locator=self.target(args);context=self.action_context(args)
                if locator.get_attribute('type')=='password' or context.get('credential_form') or re.search(r'\b(password|captcha|otp|verification|credit.?card|card.?number|cvv|cvc|iban|mfa|two.factor|security code|one.time|log[ -]?in|sign[ -]?in)\b',context.get('label',''),re.I):
                    raise Denied('Authentication/payment control requires Manual Control; no automated secrets are entered')
                decision=classify(op,context)
                if decision.required and not approved:raise Denied('Owner approval is required: '+decision.reason)
                receiver=context.get('form_action') if context.get('form_submission') else context.get('page_url')
                destination=origin(receiver or self.effective_url())
                if approved:self.review_lease={'origin':destination,'until':time.monotonic()+15,'epoch':self.permissions.generation,'used':False,
                    'url':context.get('form_action') if context.get('form_submission') else None,'method':context.get('form_method')}
                if op in ('fill','select','check'):self.edit_until=time.monotonic()+30
                self.observation=None
                if op=='click':locator.click(timeout=3000)
                elif op=='fill':locator.fill(str(args['text'])[:20000])
                elif op=='select':locator.select_option(value=str(args['text']))
                elif op=='check':locator.set_checked(bool(args['checked']))
                elif op=='upload':
                    path=Path(args['approved_path']);receiver=context.get('form_action') or self.page.url
                    self.uploads[(origin(receiver),locator.get_attribute('name') or '',path.name)]=path
                    locator.set_input_files(str(path))
                elif op=='press':
                    if args['key'] not in ('Enter','Tab','Escape','ArrowDown','ArrowUp'):raise Denied('Unsupported browser key')
                    locator.press(args['key'])
                elif op=='scroll':self.page.mouse.wheel(0,max(-2000,min(2000,int(args['amount']))))
                else:raise ValueError('Unsupported browser operation')
            if self.review_blocked:raise Denied('A request was blocked before forwarding: '+self.review_blocked)
            return self.inspect()
        except Exception:
            self.observation=None
            raise  # Never replay a click, submission, upload or uncertain mutation.
        finally:self.submission_allowed=False;self.owner_reviewed=False

    def resolve_tab(self,ident):
        for page in self.context.pages:
            if self.tab_id(page)==int(ident) and not page.is_closed():return page
        raise Denied('Tab no longer exists; inspect Browser Tabs again')

    def new_page(self):
        if not self.background:return self.context.new_page()
        session=self.context.browser.new_browser_cdp_session()
        try:
            with self.context.expect_page() as created:
                session.send('Target.createTarget',{'url':'about:blank','background':True})
            return created.value
        finally:session.detach()

    def screenshot(self):
        if not self.permissions.observe:raise Denied('Observation consent is off')
        self.authorize(self.effective_url(),'Capture this authorized website.')
        if re.search(r'/(?:login|signin|sign-in|oauth|challenge|captcha|mfa)(?:/|$)',urlsplit(self.page.url).path,re.I):raise Denied('Authentication screenshots require manual handling')
        masks=[]
        for frame in self.page.frames:
            url=frame.url if frame.url.startswith(('http://','https://')) else self.effective_url()
            if not self.access.available(url,self.tab_id()) and origin(url) not in self.access.resources.get(self.tab_id(),set()):masks.append(frame.locator(':root'))
            else:masks.append(frame.locator('input[type=password],input[autocomplete="one-time-code"],input[autocomplete="cc-number"],input[autocomplete="cc-csc"],input[name*=token i],input[name*=secret i]'))
        return self.page.screenshot(type='png',full_page=False,mask=masks,mask_color='#000000')

    def goto(self,url,reason='Navigate to this website.',force=False):
        previous=self.effective_url();tab=self.tab_id()
        if previous and origin(previous)!=origin(url):self.access.leave(tab,keep_denials=True)
        self.authorize(url,reason,force)
        self.observation=None
        try:
            response=self.page.goto(url,wait_until='domcontentloaded',timeout=25000)
        except Exception as error:
            # A timed-out GET may already have navigated. Report actual state,
            # never start another navigation or repeat a submission blindly.
            self.blocked(url,'Navigation did not fully settle: '+type(error).__name__,'navigation')
            if self.review_blocked or not self.effective_url():raise
            response=None
        if self.review_blocked:raise Denied(self.review_blocked)
        return response

    def target(self,args):
        if args.get('observation')!=self.observation or time.monotonic()-self.observed_at>90:
            raise Denied('Inspect this page again before acting')
        index=int(args.get('element',0))
        if index<0 or index>=len(self.elements):raise Denied('Unknown browser element')
        frame=self.element_frames.get(index,self.page.main_frame)
        self.authorize(frame.url if frame.url.startswith(('http://','https://')) else self.effective_url(),'Interact with this embedded website.')
        for observed,signature in self.value_signatures.items():
            if self.element_frames.get(observed)!=frame:continue
            element=self.elements[observed]
            current=element.evaluate("e=>[(e.isContentEditable?e.innerText:e.value||'').slice(0,1000),e.checked===undefined?null:e.checked]")
            current[0]=safe_text(current[0])
            if tuple(current)!=signature:raise Denied('A form field changed after inspection. Nothing was dispatched; inspect again and preserve owner edits.')
        target=self.elements[index]
        if not target.is_visible() or not target.evaluate('e=>e.isConnected'):raise Denied('Element changed; inspect again')
        return target

    def multipart(self,request,content_type):
        match=re.search(r'boundary=(?:"([^"]+)"|([^;\s]+))',content_type)
        raw=request.post_data_buffer
        if not match or raw is None:raise Denied('Cannot safely reconstruct this file-upload request')
        marker=b'--'+(match.group(1) or match.group(2)).encode()
        parts=raw.split(marker);destination=origin(request.url)
        for index,part in enumerate(parts):
            if b'\r\n\r\n' not in part:continue
            header,body=part.split(b'\r\n\r\n',1)
            field=re.search(br'\bname="([^"]*)"',header)
            filename=re.search(br'\bfilename="([^"]*)"',header)
            if filename:
                path=self.uploads.get((destination,field.group(1).decode() if field else '',filename.group(1).decode()))
                if path is None or not path.is_file() or path.stat().st_size>25*1024*1024:raise Denied('Unapproved or oversized upload part')
                parts[index]=header+b'\r\n\r\n'+path.read_bytes()+b'\r\n'
        return marker.join(parts)

    def close(self):
        if self.context:
            try:self.context.close()
            except Exception:pass
        if self.anonymous:
            try:self.anonymous.dispose()
            except Exception:pass
            self.anonymous=None
        if self.runtime:
            try:self.runtime.stop()
            except Exception:pass
        self.context=self.runtime=self.page=None
        self.resource_grants.clear();self.configured.clear();self.navigation_tabs.clear();self.pending_visits.clear();self.observation=None
        self.blocked_pages.clear()

    def refresh_processes(self):
        try:
            session=self.context.browser.new_browser_cdp_session()
            try:self.permissions.browser_pids={int(p['id']) for p in session.send('SystemInfo.getProcessInfo')['processInfo']}
            finally:session.detach()
        except Exception:self.permissions.browser_pids=set()

    def show_window(self):
        self.page.bring_to_front();self.refresh_processes()
        # bring_to_front activates a Chromium tab. Windows can still keep a
        # different application foreground; this owner-only control explicitly
        # restores the dedicated browser's native window as well.
        try:
            import win32gui,win32process,win32con
            windows=[]
            def collect(hwnd,_):
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(hwnd).startswith('Chrome_WidgetWin') and win32process.GetWindowThreadProcessId(hwnd)[1] in self.permissions.browser_pids:windows.append(hwnd)
            win32gui.EnumWindows(collect,None)
            title=self.page.title();windows.sort(key=lambda hwnd:title not in win32gui.GetWindowText(hwnd))
            if windows:
                win32gui.ShowWindow(windows[0],win32con.SW_RESTORE)
                from pywinauto import Desktop as Native
                Native(backend='win32').window(handle=windows[0]).set_focus()
        except Exception:self.blocked(self.effective_url(),'Windows kept another app in the foreground; select the Chromium window on the taskbar.','window')

    def command(self,operation,**args):
        # Only the local Qt controls enqueue this method. Model arguments never
        # acquire this owner-command path.
        if operation=='public':self.permissions.public_browsing=bool(args['enabled'])
        elif operation=='manual':
            self.permissions.browser_manual=bool(args['enabled']);self.observation=None;self.refresh_processes()
            if not args['enabled']:self.edit_until=time.monotonic()+30
        elif operation=='background':
            self.background=bool(args['enabled'])
            if not self.background:self.start();self.show_window()
        elif operation in ('open','show'):
            self.start()
            self.show_window()
        elif operation=='tab':
            self.page=self.resolve_tab(args['tab']);self.observation=None;self.show_window()
        elif operation=='close_tab':
            self.resolve_tab(args['tab']).close();self.page=next((p for p in self.context.pages if not p.is_closed()),None);self.observation=None
        elif operation=='new_tab':
            self.start();self.page=self.context.new_page();self.configure(self.page)
            if args.get('url'):
                # Entering an exact URL in the owner's local tab dialog is itself
                # a visit authorization; it grants neither account mutations nor publication.
                self.access.once.setdefault(self.tab_id(),set()).add(origin(args['url']));self.goto(args['url'])
        return {'tabs':self.tabs(),'manual':self.permissions.browser_manual,'background':self.background,'public':self.permissions.public_browsing,'diagnostics':self.diagnostics[-10:]}

    def pump_manual(self):
        if self.context:
            try:
                pages=[p for p in self.context.pages if not p.is_closed()]
                if pages:pages[0].wait_for_timeout(20)
            except Exception:pass
