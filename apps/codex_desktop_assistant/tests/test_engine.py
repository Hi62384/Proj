"""Protocol/state fault tests; no network, model usage or desktop input."""
import json
import queue
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch

sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[3])]
from assistant.engine import Engine
from assistant.storage import Store
from assistant.permissions import Permissions
from portfolio_autopilot.codex_relay.diagnostics import RelayError


class Protocol:
    def __init__(self):
        self.events=queue.Queue();self.calls=[];self.replies=[];self.turns=0
        self.workspace='/approved';self.hold=False;self.ambiguous=False
    def request(self,method,params,**kwargs):
        self.calls.append((method,params))
        if method.startswith('thread/'):
            return {'thread':{'id':params.get('threadId','thread-one')}}
        if method=='mcpServerStatus/list':return {'data':[]}
        if method=='turn/start':
            self.turns+=1
            if self.ambiguous:raise RelayError('timeout','turn/start','Ambiguous result; review')
            if not self.hold:self.finish('Actual protocol fixture text')
            return {'turn':{'id':str(self.turns)}}
        if method=='turn/steer':self.finish('Correction incorporated');return {}
        if method=='turn/interrupt':return {}
        return {}
    def finish(self,text):
        params={'threadId':'thread-one','turnId':str(self.turns)}
        self.events.put({'method':'item/agentMessage/delta','params':{**params,'itemId':'agent-'+str(self.turns),'delta':text}})
        self.events.put({'method':'item/completed','params':{**params,'item':{'type':'agentMessage','id':'agent-'+str(self.turns),'text':text}}})
        self.events.put({'method':'turn/completed','params':{'threadId':'thread-one','turn':{'id':str(self.turns),'status':'completed'}}})
    def send(self,response):self.replies.append(response)
    def close(self):pass


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=Store(Path(self.temp.name));self.addCleanup(self.store.close)
        self.permissions=Permissions();self.protocol=Protocol();self.events=[]
        self.broker=Mock();self.broker.attachments.content.return_value=[]
        self.config=SimpleNamespace()
        patches=[patch('assistant.engine.configuration',return_value=self.config),
                 patch('assistant.engine.preflight',return_value={'sandbox':'verified'}),
                 patch('assistant.engine.discover',return_value=({'steer':True},[{'id':'test','model':'test'}]))]
        for context in patches:context.start();self.addCleanup(context.stop)
        self.engine=Engine(self.store,self.permissions,self.broker,lambda *args:self.events.append(args),lambda config,**kwargs:self.protocol)
        self.addCleanup(self.engine.close)
        self.conversation=self.store.new()

    def wait(self,predicate):
        deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            if predicate():return
            time.sleep(.01)
        self.fail('Coordinator did not reach the expected state')

    def test_stream_persist_resume_same_thread(self):
        self.engine.submit(self.conversation,'First')
        self.wait(lambda:any(x[0]=='idle' and x[1]==self.conversation for x in self.events))
        self.assertEqual(self.store.conversation(self.conversation)['thread'],'thread-one')
        self.assertTrue(any(x[0]=='delta' for x in self.events))
        self.assertEqual(self.store.messages(self.conversation)[-1]['text'],'Actual protocol fixture text')
        self.events.clear();self.engine.submit(self.conversation,'Follow up')
        self.wait(lambda:any(x[0]=='idle' for x in self.events))
        resume=[p for m,p in self.protocol.calls if m=='thread/resume']
        self.assertEqual(resume[0]['threadId'],'thread-one')
        for m,p in self.protocol.calls:
            if m in ('thread/start','thread/resume','turn/start'):
                self.assertEqual(p['permissions'],'relay-locked');self.assertEqual(p['approvalPolicy'],'never')

    def test_correction_uses_actual_turn_steer_and_is_durable(self):
        self.protocol.hold=True
        self.engine.submit(self.conversation,'Start')
        self.wait(lambda:self.engine.turn is not None)
        correction=self.engine.submit(self.conversation,'Correction')
        self.wait(lambda:any(x[0]=='steered' for x in self.events))
        self.wait(lambda:any(x[0]=='idle' for x in self.events))
        steer=next(p for m,p in self.protocol.calls if m=='turn/steer')
        self.assertEqual(steer['expectedTurnId'],'1')
        self.assertEqual(steer['input'][0]['text'],'Correction')
        self.assertEqual(next(x['state'] for x in self.store.messages(self.conversation) if x['id']==correction),'sent')

    def test_ambiguous_start_is_not_automatically_replayed(self):
        self.protocol.ambiguous=True
        ident=self.engine.submit(self.conversation,'Make a change')
        self.wait(lambda:any(x[0]=='error' for x in self.events))
        self.assertEqual(sum(m=='turn/start' for m,p in self.protocol.calls),1)
        self.assertEqual(next(x['state'] for x in self.store.messages(self.conversation) if x['id']==ident),'Review after error')
        self.assertTrue(self.permissions.halted.is_set())

    def test_late_tool_from_previous_turn_is_denied(self):
        self.protocol.hold=True
        self.engine.submit(self.conversation,'Start')
        self.wait(lambda:self.engine.turn is not None)
        self.protocol.events.put({'id':99,'method':'item/tool/call','params':{'threadId':'thread-one','turnId':'old-turn','tool':'assistant_control','arguments':{}}})
        self.wait(lambda:bool(self.protocol.replies))
        self.assertIn('error',self.protocol.replies[0]);self.broker.call.assert_not_called()
        self.protocol.finish('Done');self.wait(lambda:any(x[0]=='idle' for x in self.events))

    def test_pause_retains_queued_correction_until_explicit_resume(self):
        self.protocol.hold=True
        self.engine.submit(self.conversation,'Start');self.wait(lambda:self.engine.turn is not None)
        # Durable queued message represents a correction awaiting dispatch.
        ident=self.store.add(self.conversation,'user','Retained correction','queued')
        self.engine.pause();self.wait(lambda:self.engine.active is None)
        self.assertEqual(next(x['state'] for x in self.store.messages(self.conversation) if x['id']==ident),'held after pause')
        self.protocol.hold=False;self.events.clear();self.engine.resume(self.conversation)
        self.wait(lambda:any(x[0]=='idle' for x in self.events))
        prompt=[p for m,p in self.protocol.calls if m=='turn/start'][-1]['input'][0]['text']
        self.assertIn('Retained correction',prompt)

    def test_typed_continue_resumes_only_retained_owner_grants(self):
        self.permissions.files['approved.txt']='read';self.permissions.resume(self.conversation);self.permissions.halt()
        self.engine.submit(self.conversation,'Continue.')
        self.wait(lambda:any(x[0]=='idle' for x in self.events))
        self.assertFalse(self.permissions.halted.is_set())
        self.permissions.revoke();self.events.clear()
        self.engine.submit(self.conversation,'Continue.')
        self.wait(lambda:any(x[0]=='idle' for x in self.events))
        self.assertTrue(self.permissions.halted.is_set())


if __name__=='__main__':unittest.main()
