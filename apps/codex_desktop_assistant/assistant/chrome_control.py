"""Conversation-bound Chrome capabilities; independent from desktop/PW grants."""
import base64
import hashlib
import json
import time
import uuid
import threading
from contextlib import contextmanager
from .permissions import Denied,origin
from .action_policy import classify,Review,request_review
from .web_policy import safe_text
from .chrome_bridge import ChromeBridge


class ChromeControl:
    def __init__(self,permissions,store,approve,emit,attachments):
        self.permissions,self.store,self.approve,self.emit,self.attachments=permissions,store,approve,emit,attachments
        def event(kind,conversation,data):
            if kind=='chrome_status':permissions.chrome_protected=bool(data.get('tabs'))
            emit(kind,conversation,data)
        self.bridge=ChromeBridge(store.directory,event);self.grants={};self.selected=None;self.observations={};self.frames={};self.image_consent=set();self.draft_scopes={};self.adapter_context=threading.local();self.mode=False

    @contextmanager
    def adapter_review(self,authorizer):
        previous=getattr(self.adapter_context,'authorizer',None);self.adapter_context.authorizer=authorizer
        try:yield
        finally:self.adapter_context.authorizer=previous

    def register_draft_fixture(self,conversation,url):
        from urllib.parse import urlsplit
        parts=urlsplit(url)
        if parts.hostname!='127.0.0.1':raise Denied('Fixture draft scope is local-only')
        self.draft_scopes[conversation]={'origin':origin(url),'page':url,'form':parts.scheme+'://'+parts.netloc+'/save-draft','id':'synthetic-draft','expires':time.time()+3600}

    def approved_draft(self,conversation,context):
        scope=self.draft_scopes.get(conversation)
        return bool(scope and time.time()<scope['expires'] and context.get('page_url')==scope['page'] and context.get('form_action')==scope['form'] and context.get('form_id')==scope['id'] and context.get('form_visibility')=='draft' and context.get('form_method')=='POST' and context.get('label')=='Save draft')

    def status(self):
        state=self.bridge.status();state['attached']=[{'tab':t,'origin':g['origin'],'conversation':g['conversation']} for t,g in self.grants.items() if g['epoch']==self.permissions.generation and g['session']==state['session']]
        state['selected']=self.selected;return state

    def check(self,conversation,epoch=None):
        p=self.permissions
        if p.cancelled() or p.halted.is_set() or p.owner!=conversation or (epoch is not None and epoch!=p.generation):raise Denied('Chrome control is stopped, cancelled, or belongs to another conversation')
        if p.manual_requests:raise Denied('A manual step is pending; return control before Chrome automation')
        if p.safety_check and not p.safety_check():raise Denied('Desktop is locked; review before continuing')
        return True

    def tab_guard(self,conversation,tab,epoch):
        self.check(conversation,epoch);state=self.bridge.status();grant=self.grants.get(tab);offered=next((x for x in state['tabs'] if x['tab']==tab),None)
        if not grant or grant['conversation']!=conversation or grant['epoch']!=epoch or grant['session']!=state['session'] or not offered or offered['origin']!=grant['origin']:raise Denied('Attach this exact extension-authorized tab to the current chat')
        if offered.get('manual'):raise Denied('This Chrome tab is under Manual Control')
        return True

    def attach(self,conversation,tab,ask=True):
        self.check(conversation);state=self.bridge.status();offered=next((x for x in state['tabs'] if x['tab']==tab),None)
        if not offered:raise Denied('First choose Allow Codex to Control This Tab in its Chrome extension popup')
        epoch=self.permissions.generation
        existing=self.grants.get(tab)
        if existing and existing=={'conversation':conversation,'epoch':epoch,'origin':offered['origin'],'session':state['session']}:self.selected=tab;return
        if ask and not self.approve(conversation,'Attach Chrome tab '+str(tab),{'website_access':True,'chrome_tab':True,'operation':'website_access','origin':offered['origin'],'reason':'Use this exact existing Chrome tab and its signed-in session in this chat.','note':'The extension already authorized this tab. Page text and authorized screenshots can be sent to your Codex account. Sensitive actions remain separately reviewed.'}):raise Denied('Owner denied attaching the Chrome tab')
        self.check(conversation,epoch)
        self.grants[tab]={'conversation':conversation,'epoch':epoch,'origin':offered['origin'],'session':state['session']};self.selected=tab

    def request(self,conversation,operation,args,epoch,unattached=False):
        tab=args.get('tab');guard=(lambda:self.tab_guard(conversation,tab,epoch)) if tab is not None and not unattached else (lambda:self.check(conversation,epoch))
        if args.get('frame',0):
            previous=guard
            def guard():
                previous();self.frame_guard(conversation,args['tab'],args['frame'],epoch,ask=False);return True
        return self.bridge.request(operation,args,cancel=self.permissions.cancelled,guard=guard)

    def frame_guard(self,conversation,tab,frame,epoch,ask=False):
        offered=next((t for t in self.bridge.status()['tabs'] if t['tab']==tab),{})
        expected=offered.get('frames',{}).get(str(frame));key=(tab,frame,epoch,self.bridge.session if hasattr(self.bridge,'session') else self.bridge.status()['session'])
        if not expected:raise Denied('Authorize this exact embedded frame in the Chrome extension first')
        if expected==self.grants[tab]['origin']:self.frames[key]=expected;return expected
        if self.frames.get(key)!=expected:
            if not ask:raise Denied('Embedded frame authority changed; inspect again')
            if not (self.bridge.status().get('full_browser') and offered.get('assistant_created')) and not self.approve(conversation,'Allow embedded Chrome frame',{'website_access':True,'chrome_tab':True,'operation':'website_access','origin':expected,'reason':'Inspect or interact with this explicitly extension-authorized frame in the attached tab.'}):raise Denied('Owner denied embedded frame access')
            self.tab_guard(conversation,tab,epoch);self.frames[key]=expected
        return expected

    def call(self,conversation,operation,args,attachment_map=None):
        self.check(conversation);epoch=self.permissions.generation
        if operation=='find_tabs':
            if not self.bridge.status().get('full_browser'):raise Denied('Enable Full Browser Access for owner-referenced existing-tab search')
            query=str(args.get('query','')).strip()
            messages=[m['text'] for m in self.store.messages(conversation) if m['role']=='user']
            if not 3<=len(query)<=120:raise Denied('Provide a specific bounded existing-tab reference')
            referenced=bool(messages and query.casefold() in messages[-1].casefold())
            authorizer=getattr(self,'reference_authorizer',None)
            if not referenced and not (authorizer and authorizer(conversation,query)):raise Denied('Existing-tab search needs a specific owner reference or local approval. New agent tabs need no attachment.')
            return self.request(conversation,'find_tabs',{'query':query},epoch)
        if operation=='adopt_tab':
            query=str(args.get('query','')).strip();matches=self.call(conversation,'find_tabs',{'query':query})
            tab=args.get('tab')
            if type(tab) is not int or tab not in {row['tab'] for row in matches['tabs']}:raise Denied('Choose a matching owner-referenced tab')
            self.request(conversation,'adopt_tab',{'tab':tab},epoch,unattached=True)
            self.attach(conversation,tab,ask=False);return {'selected':tab,'foreground_changed':False}
        if operation in ('list_tabs','list_windows'):
            return self.request(conversation,operation,{},epoch)
        # Do not forward model-supplied proof/privilege fields to the worker.
        allowed={'tab','frame','observation','element','end_element','operation','text','checked','amount','key','attachment_id','url','milliseconds','method','query','offset','text_offset','text_query'}
        args={key:value for key,value in args.items() if key in allowed};tab=args.get('tab',self.selected)
        if operation=='open_tab':
            origin(args['url']);decision=request_review('GET',args['url'])
            if decision.required:raise Denied(decision.reason)
            result=self.request(conversation,'open_tab',{'url':args['url']},epoch)
            self.check(conversation,epoch)
            created=result['tab']
            if result.get('authorized'):self.attach(conversation,created,ask=False)
            return result
        if type(tab) is not int:raise Denied('Select an extension-authorized Chrome tab first')
        if 'frame' in args and (type(args['frame']) is not int or args['frame']<0):raise Denied('Use a numeric frame ID from Chrome inspection')
        args['tab']=tab
        if operation=='switch_tab':
            self.attach(conversation,tab,ask=False);return {'selected':tab,'foreground_changed':False}
        if tab not in self.grants and any(t['tab']==tab for t in self.bridge.status()['tabs']):self.attach(conversation,tab,ask=False)
        self.tab_guard(conversation,tab,epoch)
        if operation=='show':return self.request(conversation,'show',args,epoch)
        frame_origin=self.frame_guard(conversation,tab,args['frame'],epoch,ask=True) if args.get('frame',0) else self.grants[tab]['origin']
        if operation=='inspect':
            result=self.request(conversation,'inspect',args,epoch)
            if origin(result.get('origin',result['url']))!=frame_origin:raise Denied('Chrome page origin changed before observation delivery')
            result={**result,'tab':tab,'frame':args.get('frame',0)}
            self.observations[(tab,args.get('frame',0))]=result['observation'];return result
        if operation=='observe':
            # Availability is checked without pixels before requesting consent.
            # A background tab cannot be captured even if consent were granted.
            self.request(conversation,'observe_check',args,epoch)
            consent=(tab,epoch,self.bridge.status()['session'])
            if consent not in self.image_consent:
                if not self.approve(conversation,'Allow screenshots of this Chrome tab',{'operation':'chrome_screenshot','approval_reason':'Capture this exact authorized, visible Chrome tab when needed and send its pixels to your Codex account. Authentication/payment screens and unapproved frames remain excluded. This consent expires with this tab session.','target_context':{'tab':tab,'origin':self.grants[tab]['origin']}}):raise Denied('Owner denied Chrome screen observation')
                self.tab_guard(conversation,tab,epoch);self.image_consent.add(consent)
            args['allowed_frames']={str(key[1]):site for key,site in self.frames.items() if key[0]==tab and key[2]==epoch and key[3]==self.bridge.status()['session']}
            result=self.request(conversation,'observe',args,epoch);image=result.get('image','')
            if not image.startswith(('data:image/png;base64,','data:image/jpeg;base64,')):raise Denied('Unsupported screenshot response')
            return base64.b64decode(image.split(',',1)[1],validate=True)
        if operation=='navigate':
            if origin(args['url'])!=self.grants[tab]['origin']:
                if self.bridge.status().get('full_browser'):return self.call(conversation,'open_tab',{'url':args['url']})
                raise Denied('Authorize the destination tab/site in the extension; navigation does not expand an existing tab grant')
            decision=request_review('GET',args['url'])
            if decision.required:raise Denied(decision.reason)
        if operation=='close_tab':
            state=self.request(conversation,'close_check',{'tab':tab},epoch)
            if state.get('may_lose_edits',True):
                reason='Closing this tab could discard editor or form contents. Review before closing.'
                if not self.approve(conversation,'Close tab with possible unsaved edits',{'operation':'close_tab','approval_reason':reason,'target_context':{'tab':tab,'origin':self.grants[tab]['origin']}}):raise Denied('Owner denied closing a tab with possible unsaved edits')
            return self.request(conversation,'close_tab',{'tab':tab,'close_token':state.get('close_token')},epoch)
        if operation=='download':
            if operation=='download' and origin(args['url'])!=self.grants[tab]['origin']:raise Denied('Download site is outside this authorized tab')
            reason='Close this exact authorized Chrome tab.' if operation=='close_tab' else 'Open Chrome’s Save As dialog for this authorized download. You must choose the destination yourself; the assistant will not select or overwrite a file.'
            if not self.approve(conversation,reason,{'operation':operation,'approval_reason':reason,'target_context':{'tab':tab,'origin':self.grants[tab]['origin']}}):raise Denied('Owner denied this Chrome operation')
        if operation=='wait':
            deadline=time.monotonic()+min(5,max(0,float(args.get('milliseconds',500))/1000))
            while time.monotonic()<deadline:self.tab_guard(conversation,tab,epoch);time.sleep(.05)
            return self.call(conversation,'inspect',{'tab':tab,'frame':args.get('frame',0)})
        if operation=='action':
            if args.get('operation') not in ('click','hover','fill','select','check','scroll','upload','drag'):raise Denied('Unsupported Chrome action. Use semantic click/fill; real keyboard defaults need Manual Control.')
            if not (args.get('operation')=='scroll' and 'element' not in args) and (type(args.get('element')) is not int or args['element']<0):raise Denied('Choose a numeric element from the latest inspection')
            if args.get('observation')!=self.observations.get((tab,args.get('frame',0))):raise Denied('Inspect this tab/frame before acting')
            args['action']=args.pop('operation')
            context=self.request(conversation,'context',args,epoch)
            if args['action']=='click' and context.get('href','').startswith(('http://','https://')) and not context.get('form_submission'):
                decision=request_review('GET',context['href'])
                if decision.required:raise Denied(decision.reason)
                if origin(context['href'])!=self.grants[tab]['origin']:
                    if self.bridge.status().get('full_browser'):return self.call(conversation,'open_tab',{'url':context['href']})
                    raise Denied('The link targets a site outside this Restricted Browser grant')
            upload_record=None
            if args['action']=='upload':
                upload_record=(attachment_map or {}).get(args.get('attachment_id'))
                if not upload_record:raise Denied('Upload requires an existing attachment from this chat; arbitrary paths are not accepted')
                path=self.attachments.path(upload_record)
                if path.stat().st_size>25*1024*1024:raise Denied('Chrome upload limit is 25 MB')
                receiver=context.get('form_action') or context['page_url']
                if origin(receiver)!=self.grants[tab]['origin']:raise Denied('Upload form destination is outside this authorized tab site')
            if context.get('credential_form'):raise Denied('Credential form requires Manual Control')
            decision=classify(args['action'],context)
            if args['action']=='upload':decision=Review('Transfer this specific approved file into this authorized tab. Website code may upload it immediately.','submission')
            authorizer=getattr(self.adapter_context,'authorizer',None)
            scoped=decision.category=='submission' and (self.approved_draft(conversation,context) or (authorizer and authorizer(conversation,args,context,upload_record,decision)))
            if decision.required and not scoped:
                details={'operation':args['action'],'approval_reason':decision.reason,'approval_category':decision.category,'target_context':context,'tab':tab}
                if upload_record:details['file']={'name':upload_record['name'],'bytes':path.stat().st_size,'sha256':upload_record['sha256']}
                if not self.approve(conversation,context.get('label') or args['action'],details):raise Denied('Owner denied this exact Chrome action')
            self.tab_guard(conversation,tab,epoch)
            current=self.request(conversation,'context',args,epoch)
            if context!=current:raise Denied('Control changed while awaiting approval; inspect again')
            if decision.required and context.get('form_submission'):
                args['owner_reviewed']=True;args['reviewed_form_url']=context.get('form_action');args['reviewed_form_method']=context.get('form_method')
            self.observations.pop((tab,args.get('frame',0)),None)
            if args['action']=='upload':return self.upload(conversation,args,attachment_map or {},epoch,context)
            result=self.request(conversation,'trusted_action' if args.get('method')=='trusted' else 'action',args,epoch)
            return {'dispatch':result,'next':'Inspect and verify the current page. Do not infer a saved change from event dispatch.'}
        allowed=('navigate','open_tab','close_tab','back','forward','reload','frames','download')
        if operation not in allowed:raise Denied('Unsupported bounded Chrome capability')
        self.observations.pop((tab,args.get('frame',0)),None)
        return self.request(conversation,operation,args,epoch)

    def upload(self,conversation,args,attachments,epoch,context):
        record=attachments.get(args.get('attachment_id'))
        if not record:raise Denied('Select a file attachment in this chat before uploading; local paths are not accepted by the extension')
        path=self.attachments.path(record)
        if path.stat().st_size>25*1024*1024:raise Denied('Chrome upload limit is 25 MB')
        destination=context.get('form_action') or context['page_url']
        if origin(destination)!=self.grants[args['tab']]['origin']:raise Denied('Upload form targets another site. That destination is not authorized by this tab grant.')
        raw=path.read_bytes();upload=uuid.uuid4().hex;digest=hashlib.sha256(raw).hexdigest()
        if digest!=record['sha256']:raise Denied('Attachment changed after it was approved; reattach the intended file')
        base={k:args[k] for k in ('tab','frame','observation','element') if k in args};base['upload']=upload
        mime='image/png' if raw.startswith(b'\x89PNG\r\n\x1a\n') else 'image/jpeg' if raw.startswith(b'\xff\xd8') else 'application/zip' if raw.startswith(b'PK\x03\x04') else 'application/octet-stream'
        receivers=record.get('_upload_receivers',[])
        if receivers and (origin(destination)!='https://payhip.com:443' or receivers!=['https://pe56d.s3.amazonaws.com/']):raise Denied('Unsupported platform storage receiver')
        self.request(conversation,'upload_begin',{**base,'name':record['name'],'size':len(raw),'sha256':digest,'mime':mime,'allowed_upload_receivers':receivers},epoch)
        for offset in range(0,len(raw),128*1024):self.request(conversation,'upload_chunk',{**base,'offset':offset,'data':base64.b64encode(raw[offset:offset+128*1024]).decode()},epoch)
        return self.request(conversation,'upload_finish',base,epoch)

    def stop(self):
        self.grants.clear();self.observations.clear();self.frames.clear();self.image_consent.clear();self.draft_scopes.clear();self.selected=None;self.permissions.chrome_protected=False;self.bridge.stop_tabs()
