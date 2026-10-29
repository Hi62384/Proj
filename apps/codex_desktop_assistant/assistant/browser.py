"""Dedicated Playwright profile. Never attaches to or reads ordinary browser secrets."""
import uuid
import time
import re
from urllib.parse import urljoin,urlsplit,urlunsplit
from pathlib import Path
from .permissions import Denied, origin

CONTROLS='button:visible,input:not([type=hidden]):visible,textarea:visible,select:visible,a:visible,[role=button]:visible,[role=checkbox]:visible'


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

    def start(self):
        if not self.permissions.browser:raise Denied('Browser control is off')
        if self.context:return
        from playwright.sync_api import sync_playwright
        self.runtime=sync_playwright().start()
        try:
            self.context=self.runtime.chromium.launch_persistent_context(str(self.directory/'browser-profile'),
                headless=False,service_workers='block',accept_downloads=True)
            self.context.set_default_timeout(1500)
            self.context.route('**/*',self.route)
            # WebSockets are blocked: they cannot bypass origin or submission checks.
            self.context.route_web_socket('**/*',lambda ws:ws.close())
            self.context.on('page',self.configure)
            self.page=self.context.pages[0] if self.context.pages else self.context.new_page()
            self.configure(self.page)
        except Exception:
            self.close();raise

    def route(self, route):
        try:
            self.permissions.check_origin(route.request.url)
            if not self.permissions.browser or (self.permissions.halted.is_set() and not self.manual_mode):raise Denied('Paused')
            # Unreviewed mutation requests are denied at network dispatch too.
            if route.request.method not in ('GET','HEAD','OPTIONS') and not (self.manual_mode or getattr(self,'submission_allowed',False)):
                raise Denied('Submission needs owner approval')
            # Fetch does not follow redirects: an allowed first hop cannot hide an
            # unapproved destination further down a redirect chain.
            options={'max_redirects':0,'timeout':10000}
            content_type=route.request.headers.get('content-type','')
            if 'multipart/form-data' in content_type and self.uploads:
                # Chromium's intercepted postData omits file bytes. Restore only
                # files explicitly granted to this origin/input by the owner.
                options['post_data']=self.multipart(route.request,content_type)
            response=route.fetch(**options)
            if response.status in (301,302,303,307,308):
                destination=urljoin(route.request.url,response.headers.get('location',''))
                try:self.permissions.check_origin(destination)
                except Denied:
                    self.last_error='Redirect destination is not approved.'
                    route.fulfill(status=403,content_type='text/html',body='<html><body>Redirect destination blocked by local permissions.</body></html>');return
                if route.request.is_navigation_request() and route.request.frame==self.page.main_frame and (route.request.method=='GET' or response.status in (301,302,303)):
                    self.redirect_target=destination
                    headers={k:v for k,v in response.headers.items() if k.lower() not in ('location','content-length','content-encoding','content-type')}
                    headers.update({'content-type':'text/html','content-security-policy':"default-src 'none'"})
                    route.fulfill(status=200,headers=headers,body='<html><body>Following approved redirect.</body></html>');return
                self.last_error='Redirect requires explicit navigation; its request was not replayed.'
                route.fulfill(status=403,content_type='text/plain',body='Redirect requires explicit owner navigation.');return
            route.fulfill(response=response)
        except Exception as error:
            self.last_error='Request blocked: '+type(error).__name__
            route.abort('blockedbyclient')

    def configure(self, page):
        page.on('dialog',lambda dialog:dialog.dismiss())
        page.on('pageerror',lambda error:setattr(self,'last_error',str(error)[:300]))
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

    def _inspect_once(self):
        self.permissions.check_origin(self.page.url)
        self.observation=uuid.uuid4().hex
        self.observed_at=time.monotonic()
        self.elements=self.page.locator(CONTROLS).element_handles()[:160]
        controls=[element.evaluate('''(e,i)=>({element:i,tag:e.tagName,role:e.getAttribute('role'),type:e.type||'',label:e.getAttribute('aria-label')||e.labels?.[0]?.innerText||e.innerText||e.placeholder||e.name||'',value:e.type==='password'?'[private]':(e.value||'').slice(0,1000),checked:e.checked,disabled:e.disabled,options:e.tagName==='SELECT'?[...e.options].map(x=>({value:x.value,label:x.label})):undefined})''',i) for i,element in enumerate(self.elements)]
        self.value_signatures={c['element']:(c['value'],c.get('checked')) for c in controls if c.get('type') in ('text','email','number','search','tel','url','textarea','select-one','select-multiple','checkbox','radio') or c['tag'] in ('TEXTAREA','SELECT')}
        tabs=[]
        for index,page in enumerate(self.context.pages):
            try:self.permissions.check_origin(page.url)
            except Denied:continue
            tabs.append({'tab':index,'url':display_url(page.url)})
        return {'url':display_url(self.page.url),'title':self.page.title(),'observation':self.observation,
                'text':self.page.locator('body').inner_text()[:20000],'controls':controls,'error':self.last_error,
                'tabs':tabs,'downloads':self.downloads[-10:]}

    def call(self, args, approved=False):
        if self.permissions.cancelled():raise Denied('Originating turn ended; action cancelled')
        if self.permissions.manual_requests and args.get('operation') not in ('inspect','screenshot'):raise Denied('Waiting for the owner to finish the requested manual step')
        if self.permissions.halted.is_set():raise Denied('Browser automation is paused; manual browsing remains separate')
        if args.get('operation')=='check' and type(args.get('checked')) is not bool:raise ValueError('checked must be a JSON boolean')
        self.start();op=args['operation']
        self.submission_allowed=approved
        try:
            if op=='navigate':
                self.uploads.clear()
                self.permissions.check_origin(args['url'])
                response=self.goto(args['url'])
                if response and response.status>=400:self.last_error=f'HTTP {response.status}'
            elif op=='new_tab':
                self.permissions.check_origin(args['url']);self.page=self.context.new_page();self.goto(args['url'])
            elif op=='switch_tab':
                p=self.context.pages[int(args['tab'])];self.permissions.check_origin(p.url);self.page=p
            elif op=='inspect':return self.inspect()
            elif op=='screenshot':
                if not self.permissions.observe:raise Denied('Observation is off')
                self.permissions.check_origin(self.page.url)
                return self.page.screenshot(type='png',full_page=False)
            else:
                self.permissions.check_origin(self.page.url)
                locator=self.target(args)
                if op in ('click','fill','select','check','upload','press'):
                    if locator.get_attribute('type')=='password':raise Denied('Password entry requires human takeover')
                    label=locator.evaluate("e=>e.getAttribute('aria-label')||e.labels?.[0]?.innerText||e.innerText||e.placeholder||e.name||''")
                    if re.search(r'\b(password|captcha|otp|verification|credit.?card|card.?number|cvv|cvc|iban|mfa|two.factor|security code|one.time|log[ -]?in|sign[ -]?in)\b',label,re.I):raise Denied('Authentication or payment field requires takeover')
                self.observation=None
                if op=='click':
                    try:locator.click(no_wait_after=False,timeout=1500)
                    except Exception:
                        if self.redirect_target is None:raise
                    if self.redirect_target:self.goto(self.redirect_target)
                elif op=='fill':locator.fill(str(args['text'])[:20000])
                elif op=='select':locator.select_option(value=str(args['text']))
                elif op=='check':locator.set_checked(bool(args['checked']))
                elif op=='upload':
                    path=Path(args['approved_path'])
                    self.uploads[(origin(self.page.url),locator.get_attribute('name') or '',path.name)]=path
                    locator.set_input_files(str(path))
                elif op=='press':
                    if args['key'] not in ('Enter','Tab','Escape','ArrowDown','ArrowUp'):raise Denied('Unsupported browser key')
                    locator.press(args['key'])
                elif op=='scroll':self.page.mouse.wheel(0,max(-2000,min(2000,int(args['amount']))))
                else:raise ValueError('Unsupported browser operation')
            return self.inspect()
        finally:self.submission_allowed=False

    def goto(self,url):
        for _ in range(8):
            self.permissions.check_origin(url);self.redirect_target=None
            try:response=self.page.goto(url,wait_until='domcontentloaded',timeout=10000)
            except Exception:
                if not self.redirect_target:raise
                response=None
            if self.redirect_target:url=self.redirect_target;continue
            if response and response.status==403 and self.last_error.startswith('Redirect'):raise Denied(self.last_error)
            return response
        self.redirect_target=None
        raise Denied('Redirect limit reached; inspect before continuing')

    def target(self,args):
        if args.get('observation')!=self.observation or time.monotonic()-self.observed_at>90:
            raise Denied('Inspect this page again before acting')
        index=int(args.get('element',0))
        if index<0 or index>=len(self.elements):raise Denied('Unknown browser element')
        for observed,signature in self.value_signatures.items():
            element=self.elements[observed]
            current=element.evaluate("e=>[(e.value||'').slice(0,1000),e.checked===undefined?null:e.checked]")
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
        if self.runtime:
            try:self.runtime.stop()
            except Exception:pass
        self.context=self.runtime=self.page=None

    def pump_manual(self):
        if self.manual_mode and self.context:
            try:
                if self.context.pages:self.context.pages[0].wait_for_timeout(40)
                if self.redirect_target:self.goto(self.redirect_target)
            except Exception:pass
