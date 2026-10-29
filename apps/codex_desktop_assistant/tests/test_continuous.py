"""Input scheduling and asynchronous tool lifecycle fault tests; no model claims."""
import json
import sys
import threading
import time
import unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[3])]
from assistant.attention import InputGuard
from assistant.permissions import Permissions,Denied
import test_engine as engine_fixtures


def coordinator():
    guard=InputGuard.__new__(InputGuard);guard.permissions=Permissions();guard.permissions.resume('owner')
    now=[100.0];guard.clock=lambda:now[0];guard.closed=threading.Event()
    guard.lock=threading.RLock();guard.transaction_lock=threading.RLock();guard.local=threading.local()
    guard.keys_at=guard.mouse_at=guard.motion_at=0;guard.targets={};guard.held_keys=set();guard.held_buttons=set();guard.waiting=lambda value:None;guard.hooks_ready=True;guard.automation=False
    return guard,now


class CoordinationTests(unittest.TestCase):
    def test_all_ordinary_input_is_telemetry_not_interruption(self):
        guard,now=coordinator();epoch=guard.permissions.generation
        for kind in ('motion','mouse','keyboard'):
            guard.physical(kind,123);self.assertTrue(guard.check())
        self.assertFalse(guard.permissions.halted.is_set());self.assertFalse(guard.permissions.desktop_suspended)
        self.assertEqual(guard.permissions.generation,epoch)

    def test_foreign_typing_only_defers_shared_channel(self):
        guard,now=coordinator();guard.physical('keyboard',111)
        self.assertFalse(guard.busy(222,False));self.assertTrue(guard.busy(222,True));self.assertTrue(guard.busy(111,False))

    def test_minor_motion_does_not_invalidate_semantic_edits(self):
        guard,now=coordinator();before=guard.revision(111);guard.physical('motion',111)
        self.assertEqual(guard.revision(111),before);self.assertFalse(guard.busy(111,False));self.assertTrue(guard.busy(111,True))

    def test_safe_deferred_action_runs_once_after_quiet(self):
        guard,now=coordinator();guard.physical('keyboard',111);notices=[];guard.waiting=notices.append;calls=[]
        timer=threading.Timer(.05,lambda:now.__setitem__(0,101.0));timer.start()
        with guard.transaction(222,True):calls.append('dispatched')
        timer.join();self.assertEqual(calls,['dispatched']);self.assertIn('Waiting for input access',notices)
        self.assertFalse(guard.permissions.halted.is_set())

    def test_stop_cancels_a_deferred_action_before_dispatch(self):
        guard,now=coordinator();guard.physical('keyboard',111)
        timer=threading.Timer(.05,guard.permissions.halt);timer.start()
        with self.assertRaises(Denied):
            with guard.transaction(222,True):self.fail('Dispatched after Stop')
        timer.join()

    def test_partial_input_is_never_automatically_replayed(self):
        guard,now=coordinator();calls=[]
        with self.assertRaises(Denied):
            with guard.transaction(222,True):
                calls.append('first character');now[0]+=.01;guard.physical('keyboard',111);guard.checkpoint(222)
        self.assertEqual(calls,['first character']);self.assertFalse(guard.permissions.halted.is_set())

    def test_target_only_semantic_action_ignores_foreign_input(self):
        guard,now=coordinator()
        with guard.transaction(222,False):
            now[0]+=.01;guard.physical('keyboard',111);guard.checkpoint()

    def test_held_modifier_prevents_shared_typing_until_released(self):
        guard,now=coordinator();guard.physical('keyboard',111,held=(0x11,True));now[0]+=10
        self.assertTrue(guard.busy(222,True));self.assertFalse(guard.busy(222,False))
        guard.physical('keyboard',111,held=(0x11,False));now[0]+=1;self.assertFalse(guard.busy(222,True))

    def test_queued_operation_cannot_reuse_replacement_authority(self):
        from unittest.mock import Mock
        from assistant.tools import Broker
        guard,now=coordinator();p=guard.permissions;old=p.generation;p.halt();p.resume('owner')
        desktop=Mock();broker=Broker(p,desktop,Mock(),Mock(),Mock(),Mock(),Mock())
        with self.assertRaises(Denied):broker.call('owner',{'capability':'desktop.action','arguments':'{}'},authority_generation=old)
        desktop.control.assert_not_called();self.assertFalse(hasattr(p.execution_context,'generation'))


class ContinuousEngineTests(unittest.TestCase):
    setUp=engine_fixtures.EngineTests.setUp
    wait=engine_fixtures.EngineTests.wait

    def tool(self,ident,cap):
        self.protocol.events.put({'id':ident,'method':'item/tool/call','params':{'threadId':'thread-one','turnId':'1','tool':'assistant_control','arguments':{'capability':cap,'arguments':'{}'}}})

    def test_waiting_host_action_keeps_browser_and_steering_responsive(self):
        entered=threading.Event();release=threading.Event();self.addCleanup(release.set)
        def call(conversation,args,cancel_event=None,**kwargs):
            if args['capability']=='desktop.action':
                entered.set()
                while not release.wait(.01):
                    if cancel_event.is_set():raise Denied('Cancelled')
            return [{'type':'inputText','text':'verified'}]
        self.broker.call.side_effect=call;self.protocol.hold=True
        original=self.protocol.request
        def request(method,params,**kwargs):
            if method=='turn/steer':self.protocol.calls.append((method,params));return {}
            return original(method,params,**kwargs)
        self.protocol.request=request
        self.engine.submit(self.conversation,'Work');self.wait(lambda:self.engine.turn is not None)
        self.tool(101,'desktop.action');self.assertTrue(entered.wait(2))
        self.tool(102,'browser.inspect');self.engine.submit(self.conversation,'Use navy and teal.')
        self.wait(lambda:any(r.get('id')==102 for r in self.protocol.replies));self.wait(lambda:any(e[0]=='steered' for e in self.events))
        self.assertFalse(any(r.get('id')==101 for r in self.protocol.replies));self.assertEqual(self.engine.turn,'1')
        self.assertFalse(any(m=='turn/interrupt' for m,p in self.protocol.calls))
        release.set();self.wait(lambda:any(r.get('id')==101 for r in self.protocol.replies))
        self.protocol.finish('Done');self.wait(lambda:self.engine.active is None)

    def test_explicit_stop_cancels_host_work_without_replay(self):
        entered=threading.Event();cancelled=threading.Event()
        def call(conversation,args,cancel_event=None,**kwargs):
            entered.set();cancel_event.wait(2);cancelled.set();raise Denied('Stopped before dispatch')
        self.broker.call.side_effect=call;self.protocol.hold=True
        self.engine.submit(self.conversation,'Work');self.wait(lambda:self.engine.turn is not None)
        self.tool(101,'desktop.action');self.assertTrue(entered.wait(2));self.engine.pause()
        self.assertTrue(cancelled.wait(2));self.wait(lambda:self.engine.active is None)
        self.assertEqual(self.store.conversation(self.conversation)['status'],'Stopped')
        self.assertEqual(self.broker.call.call_count,1);self.assertEqual(self.protocol.turns,1)

    def test_waiting_user_state_does_not_interrupt_model(self):
        self.protocol.hold=True;self.engine.submit(self.conversation,'Work');self.wait(lambda:self.engine.turn is not None)
        self.engine.waiting(self.conversation,1);self.assertEqual(self.store.conversation(self.conversation)['status'],'Waiting for User')
        self.engine.waiting(self.conversation,-1);self.assertEqual(self.store.conversation(self.conversation)['status'],'Working')
        self.assertFalse(self.engine.interrupt.is_set());self.protocol.finish('Done');self.wait(lambda:self.engine.active is None)
        self.assertEqual(self.store.conversation(self.conversation)['status'],'Completed')

    def test_definitively_rejected_late_correction_is_queued_on_same_thread(self):
        from portfolio_autopilot.codex_relay.diagnostics import RelayError
        self.protocol.hold=True;original=self.protocol.request
        def request(method,params,**kwargs):
            if method=='turn/steer':raise RelayError('protocol.compatibility','turn/steer','Rejected','No active turn')
            return original(method,params,**kwargs)
        self.protocol.request=request
        self.engine.submit(self.conversation,'First');self.wait(lambda:self.engine.turn is not None)
        correction=self.engine.submit(self.conversation,'Use navy and teal.')
        self.wait(lambda:sum(e[0]=='queued' for e in self.events)>=3)
        self.protocol.hold=False;self.protocol.finish('First finished')
        self.wait(lambda:self.protocol.turns==2 and self.engine.active is None)
        second=[p for m,p in self.protocol.calls if m=='turn/start'][-1]
        self.assertEqual(second['threadId'],'thread-one');self.assertEqual(second['input'][0]['text'],'Use navy and teal.')
        self.assertEqual(next(x['state'] for x in self.store.messages(self.conversation) if x['id']==correction),'sent')


if __name__=='__main__':unittest.main()
