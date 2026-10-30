"""Singleton Windows controller. Authorization stays in this owner-controlled process."""
import json
import os
import secrets
import threading
import time
import uuid
from multiprocessing import AuthenticationError
from pathlib import Path

from assistant.attachments import Attachments
from assistant.browser import Browser
from assistant.chrome_bridge import UserPipeListener,private_json
from assistant.desktop import Desktop,EmergencyStop,SessionGuard
from assistant.file_policy import FilePolicy
from assistant.permissions import Permissions,Denied
from assistant.storage import Store
from assistant.tools import Broker,CAPABILITIES

MAX_REQUEST=150000


class MultiplexPipeListener(UserPipeListener):
    def create(self):
        import win32pipe
        first=0x00080000 if not getattr(self,'created_once',False) else 0
        self.handle=win32pipe.CreateNamedPipe(self.address,win32pipe.PIPE_ACCESS_DUPLEX|0x40000000|first,win32pipe.PIPE_TYPE_MESSAGE|win32pipe.PIPE_READMODE_MESSAGE|win32pipe.PIPE_WAIT|0x8,16,65536,65536,1000,self.attributes)
        self.created_once=True


class Runtime:
    def __init__(self,directory,emit):
        self.emit=emit;self.closed=threading.Event();self.lock=threading.RLock();self.clients={};self.inflight={};self.requests=[];self.fixtures=[];self.latest='Ready';self.active=None;self.listener=None
        self.store=Store(directory);self.attachments=Attachments(directory);self.permissions=Permissions()
        self.permissions.file_policy=FilePolicy(self.store.settings().get('file_rules',[]))
        self.owner=self.store.settings().get('computer_bridge_owner')
        if not self.owner or not self.store.conversation(self.owner):
            self.owner=self.store.new('Official Codex computer bridge activity');self.store.setting('computer_bridge_owner',self.owner)
        self.permissions.resume(self.owner)
        if self.store.settings().get('bridge_stopped',False):self.permissions.halt()
        self.desktop=Desktop(self.permissions);self.browser=Browser(directory,self.permissions)
        self.broker=Broker(self.permissions,self.desktop,self.browser,self.attachments,self.store,self.event,self.approve)
        self.broker.chrome.mode=True;self.permissions.chrome_mode=True
        self.broker.chrome.reference_authorizer=self.authorize_reference;self.reference_queries=set()
        self.hotkey=EmergencyStop(self.stop);self.session_guard=SessionGuard(lambda:self.stop('Windows locked or resumed; review before resuming'))
        self.permissions.safety_check=self.session_guard.check
        from assistant.attention import InputGuard
        self.input_guard=InputGuard(self.permissions);self.permissions.input_check=self.input_guard.check;self.permissions.input_coordinator=self.input_guard;self.broker.input_guard=self.input_guard
        queue=self.broker.projects.queue
        from .migration import migrate_projects
        migrate_projects(queue,self.owner)
        self.restore_local_stores()
        queue.start()  # deterministic jobs only; dispatch remains None
        self.broker.chrome.bridge.start()

    def restore_local_stores(self):
        from assistant.test_storefront import TestStorefront,LocalStoreAdapter
        for record in self.store.settings().get('bridge_local_stores',[])[:20]:
            if record.get('owner')!=self.owner or record.get('expires',0)<time.time():continue
            path=(self.store.directory/record['relative']).resolve();root=(self.store.directory/'verification').resolve()
            if not path.is_relative_to(root) or path.name!='store' or path.is_symlink():continue
            try:
                store=TestStorefront(path,port=int(record['port']));self.broker.projects.local_stores.append(store);self.broker.projects.queue.adapters[record['store']]=LocalStoreAdapter(store)
                if not self.permissions.halted.is_set():self.broker.projects.synthetic_runs[self.owner]={'store':record['store'],'expires':record['expires'],'products':record['products']}
            except OSError:self.latest='Local test store could not recover its original port; existing effects were not replayed.'

    def event(self,kind,conversation,data):
        if kind=='action':self.latest=str(data)
        self.emit(kind,conversation,data)

    def authorize_reference(self,conversation,query):
        if query.casefold() in self.reference_queries:return True
        accepted=self.approve(conversation,'Access existing tabs matching '+query,{'operation':'existing_tab_reference','query':query,'approval_reason':'Search and access only existing personal tabs matching this reference. New agent tabs already work automatically; unrelated personal tabs stay private.'})
        if accepted:self.reference_queries.add(query.casefold())
        return accepted

    def approve(self,conversation,label,args):
        self.requests[:]=[r for r in self.requests if not r['event'].is_set() and r['deadline']>time.monotonic()]
        if len(self.requests)>=20:return False
        generation=self.permissions.generation
        request={'id':uuid.uuid4().hex,'conversation':conversation,'label':label,'args':args,'event':threading.Event(),'allowed':False,'generation':generation,'deadline':time.monotonic()+300}
        self.requests.append(request);self.emit('request',conversation,request)
        while not request['event'].wait(.1):
            if self.closed.is_set() or self.permissions.halted.is_set() or self.permissions.cancelled() or self.permissions.generation!=generation or time.monotonic()>request['deadline']:
                request['event'].set();return False
        return request['allowed'] and generation==self.permissions.generation and not self.permissions.halted.is_set() and time.monotonic()<request['deadline']

    def pending(self):
        return [{'id':r['id'],'action':r['label'],'reason':r['args'].get('approval_reason') or r['args'].get('reason') or r['args'].get('question','Owner decision required'),'details':r['args']} for r in self.requests if not r['event'].is_set() and r['deadline']>time.monotonic() and r['generation']==self.permissions.generation]

    def status(self):
        now=time.monotonic();clients=sum(now-at<45 for at in self.clients.values());chrome=self.broker.chrome.status();queue=self.broker.projects.queue
        work=queue.rows("SELECT id,objective,state FROM projects WHERE state NOT IN ('completed','cancelled') ORDER BY updated DESC LIMIT 25")
        for project in work:
            counts={row['state']:row['n'] for row in queue.rows('SELECT state,COUNT(*) n FROM jobs WHERE project=? GROUP BY state',(project['id'],))};project['completed_tasks']=counts.get('completed',0);project['total_tasks']=sum(counts.values())
        waiting=queue.rows("SELECT j.id,j.project,j.key,j.payload FROM jobs j JOIN projects p ON p.id=j.project WHERE j.kind='reason' AND j.state='pending' AND p.state='running' AND p.conversation=? AND j.version=p.version AND NOT EXISTS(SELECT 1 FROM dependencies d JOIN jobs n ON n.id=d.needs WHERE d.job=j.id AND n.state!='completed') LIMIT 50",(self.owner,))
        return {'name':'Codex Computer Bridge','pid':os.getpid(),'controller_ready':not self.closed.is_set(),'mcp_clients_connected':clients,'chrome_connected':chrome['connected'],'full_browser_access':chrome.get('full_browser',False),'trusted_input':chrome.get('trusted_input',False),'desktop_authorized':self.permissions.desktop,'stopped':self.permissions.halted.is_set(),'active_tool':self.active,'latest_action':self.latest,'current_website':self.broker.chrome.grants.get(self.broker.chrome.selected,{}).get('origin'),'pending_requests':len(self.pending()),'projects':work,'reasoning_state':'Waiting for Codex' if waiting else 'No reasoning jobs waiting','waiting_for_codex':waiting,'independent_ai_engine':False}

    def stop(self,reason='Stopped by owner'):
        self.reference_queries.clear()
        self.store.setting('bridge_stopped',True)
        self.permissions.revoke();self.broker.chrome.stop();self.broker.projects.stop();self.latest=reason
        for r in self.requests:r['event'].set()
        self.emit('stopped',None,reason)
        return {'stopped':True,'reason':reason}

    def call(self,client,operation,arguments,request_id=None):
        if not isinstance(client,str) or len(client)!=32 or not isinstance(arguments,dict):raise Denied('Invalid client request')
        now=time.monotonic();self.clients={key:at for key,at in self.clients.items() if now-at<45}
        if operation=='bridge_mcp_connected':
            if client not in self.clients and len(self.clients)>=64:raise Denied('Too many concurrent bridge clients')
            self.clients[client]=now;return {'mcp_initialized':True}
        if operation=='bridge_mcp_heartbeat':
            if client in self.clients:self.clients[client]=now
            return {'connected':client in self.clients}
        if operation in ('bridge_status','bridge_health','bridge_start_services','bridge_get_active_work'):return self.status()
        if operation=='bridge_wait_ready':
            deadline=time.monotonic()+max(0,min(25,float(arguments.get('seconds',20))))
            while time.monotonic()<deadline and not self.closed.is_set():
                if self.broker.chrome.bridge.status()['connected']:break
                time.sleep(.25)
            return self.status()
        if operation=='bridge_capabilities':return {'capabilities':CAPABILITIES,'desktop_default':'off','file_policy':'Explicit Deny wins; existing independent Read/Write/Create/Delete rules','no_shell':True,'no_arbitrary_javascript':True,'reasoning':'Official Codex only'}
        if operation=='bridge_get_pending_requests':return {'requests':self.pending()}
        if operation=='bridge_open_dashboard':self.emit('show_dashboard',None,None);return {'requested':True}
        if operation=='bridge_stop':return self.stop()
        if operation=='bridge_cancel_call':
            event=self.inflight.get((client,arguments.get('request')))
            if event:event.set()
            return {'cancelled':bool(event),'note':'An already dispatched external effect may be uncertain. Inspect before continuing.'}
        if operation=='bridge_detach':
            self.clients.pop(client,None)
            for (identity,_),event in list(self.inflight.items()):
                if identity==client:event.set()
            return {'disconnected':True}
        if operation=='bridge_history':
            # Historical messages are not deleted; no inference/old thread is resumed.
            return {'conversations':self.store.conversations()[:100],'projects':self.broker.projects.queue.rows('SELECT id,objective,state,conversation FROM projects ORDER BY updated DESC LIMIT 100')}
        if operation=='bridge_reason_tasks':return {'tasks':self.status()['waiting_for_codex']}
        if operation=='bridge_verify_saved_payhip':
            from .payhip_verification import verify_saved
            return verify_saved(self)
        if operation in ('bridge_start_local_business_test','bridge_start_local_builder_test'):
            if self.permissions.halted.is_set():raise Denied('Resume locally before starting tests')
            if operation=='bridge_start_local_business_test':
                scope=self.broker.projects.prepare_synthetic(self.owner);store=self.broker.projects.local_stores[-1]
                records=[r for r in self.store.settings().get('bridge_local_stores',[]) if r.get('expires',0)>time.time()]
                records.append({'owner':self.owner,'store':scope['store'],'expires':scope['expires'],'products':scope['products'],'relative':str(store.directory.relative_to(self.store.directory)),'port':store.server.server_port})
                self.store.setting('bridge_local_stores',records[-20:]);return scope
            from assistant.builder_fixture import BuilderFixture
            if len(self.fixtures)>=3:raise Denied('Local fixture limit reached; reuse the existing disposable builder')
            fixture=BuilderFixture();self.fixtures.append(fixture);self.broker.chrome.register_draft_fixture(self.owner,fixture.url)
            return {'url':fixture.url,'visibility':'synthetic unpublished draft','approved_actions':['ordinary editing','exact Save draft'],'excluded':['Publish','Pay now'],'expected_human_interruptions':0}
        if operation=='bridge_local_test_state':
            return {'builders':[{'url':fixture.url,'state':dict(fixture.state)} for fixture in self.fixtures],'stores':[{'url':store.url,'listings':store.count()} for store in self.broker.projects.local_stores]}
        if operation=='bridge_get_artifact':
            if self.permissions.halted.is_set():raise Denied('Resume locally before retrieving artifacts')
            from assistant.products import digest
            records={r['id']:r for message in self.store.messages(self.owner) if message['text'].startswith('Generated product delivery: ') for r in json.loads(message['attachments'])}
            record=records.get(arguments.get('attachment_id'))
            if not record:raise Denied('Not a generated deliverable owned by this bridge')
            path=self.attachments.path(record)
            if self.permissions.file_policy.decision(path,'read')=='deny':raise Denied('Explicit Read denial applies to this artifact')
            if digest(path)!=record['sha256']:raise Denied('Deliverable changed after verification')
            self.broker.register([record]);return {'attachment_id':record['id'],'path':str(path),'sha256':record['sha256'],'bytes':path.stat().st_size,'name':record['name']}
        if operation=='bridge_reason_result':
            if self.permissions.halted.is_set():raise Denied('Resume locally before continuing project work')
            queue=self.broker.projects.queue;rows=queue.rows("SELECT * FROM jobs WHERE id=? AND kind='reason' AND state='pending'",(arguments.get('job'),))
            if not rows or not queue.rows("SELECT id FROM projects WHERE id=? AND conversation=? AND state='running' AND version=?",(rows[0]['project'],self.owner,rows[0]['version'])):raise Denied('Not an owned running project with a waiting reasoning task')
            if queue.rows("SELECT n.id FROM dependencies d JOIN jobs n ON n.id=d.needs WHERE d.job=? AND n.state!='completed'",(rows[0]['id'],)):raise Denied('Complete the reasoning task prerequisites first')
            result=arguments.get('result');encoded=json.dumps(result,allow_nan=False)
            if not isinstance(result,dict) or len(encoded)>50000:raise Denied('Provide a bounded structured reasoning result')
            state='blocked' if arguments.get('blocked') else 'completed'
            with queue.lock:
                queue.db.execute('UPDATE jobs SET state=?,result=?,error=? WHERE id=?',(state,json.dumps({'reported':True,'result':result}),'Official Codex reported a reasoning blocker' if state=='blocked' else '',rows[0]['id']));queue.event(rows[0]['project'],rows[0]['id'],'official_codex_result',{'state':state});queue.db.commit()
            queue.wake.set();return {'state':state,'reasoning_only':True}
        if operation not in CAPABILITIES:raise Denied('Unknown bridge capability')
        event=threading.Event();key=(client,request_id or uuid.uuid4().hex);self.inflight[key]=event
        try:
            with self.lock:
                if event.is_set() or self.permissions.halted.is_set():raise Denied('Stopped. Resume locally in the dashboard; MCP cannot grant itself permission')
                self.active=operation
                try:
                    result=self.broker.call(self.owner,{'capability':operation,'arguments':json.dumps(arguments,allow_nan=False)},cancel_event=event)
                    if operation=='projects.deliver':
                        records=[r for message in self.store.messages(self.owner) if message['text'].startswith('Generated product delivery: ') for r in json.loads(message['attachments'])]
                        self.broker.register(records)
                    return {'content':result}
                finally:self.active=None
        finally:self.inflight.pop(key,None)

    def start_pipe(self):
        key=secrets.token_bytes(32);address=r'\\.\pipe\codex-computer-'+uuid.uuid4().hex
        self.listener=MultiplexPipeListener(address,key);private_json(self.store.directory/'computer-bridge.json',{'version':1,'address':address,'key':key.hex(),'pid':os.getpid()})
        threading.Thread(target=self.serve,daemon=True,name='computer-bridge-ipc').start()

    def serve(self):
        while not self.closed.is_set():
            try:
                connection=self.listener.accept()
                threading.Thread(target=self.handle,args=(connection,),daemon=True).start()
            except (OSError,EOFError,AuthenticationError):
                if not self.closed.is_set():time.sleep(.1)

    def handle(self,connection):
        try:
            if not connection.poll(5):return
            request=json.loads(connection.recv_bytes(MAX_REQUEST))
            if set(request)!={'client','operation','arguments','request'} or not isinstance(request['request'],str) or len(request['request'])!=32:raise Denied('Invalid IPC envelope')
            result=self.call(request['client'],request['operation'],request['arguments'],request['request'])
            response={'ok':True,'result':result}
        except Exception as error:
            from portfolio_autopilot.codex_relay.diagnostics import sanitize
            response={'ok':False,'error':type(error).__name__+': '+sanitize(error)[:600]}
            self.latest=response['error'];self.emit('error',None,self.latest)
        try:connection.send_bytes(json.dumps(response,ensure_ascii=False,allow_nan=False).encode())
        except (OSError,EOFError):pass
        finally:connection.close()

    def close(self):
        self.stop('Bridge shut down');self.closed.set()
        for fixture in self.fixtures:fixture.close()
        if self.listener:self.listener.close()
        self.hotkey.close();self.session_guard.close();self.input_guard.close();self.broker.chrome.bridge.close();self.browser.close();self.broker.projects.close();self.store.close()
