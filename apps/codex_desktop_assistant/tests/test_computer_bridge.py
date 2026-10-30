"""MCP metadata and local policy boundaries; not official-client acceptance."""
import asyncio
import json
import sys
import tempfile
import threading
import time
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import Mock
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[3])]
from bridge import server
from bridge.runtime import Runtime
from bridge.migration import backup_state,migrate_projects
from assistant.permissions import Permissions,Denied
from assistant.storage import Store


class ComputerBridgeTests(unittest.TestCase):
    def runtime(self):
        runtime=Runtime.__new__(Runtime);runtime.clients={};runtime.inflight={};runtime.lock=threading.RLock();runtime.permissions=Permissions();runtime.owner='host-owner';runtime.permissions.resume(runtime.owner);runtime.broker=Mock();runtime.active=None;runtime.closed=threading.Event();runtime.requests=[];runtime.latest='Ready'
        return runtime

    def test_tool_metadata_is_valid_and_unique(self):
        import jsonschema
        tools=asyncio.run(server.list_tools());self.assertGreater(len(tools),50);self.assertEqual(len(tools),len({t.name for t in tools}))
        for tool in tools:
            jsonschema.Draft202012Validator.check_schema(tool.inputSchema)
            self.assertLess(len(tool.description),2000)
        self.assertNotIn('execute_shell',server.OPERATIONS);self.assertNotIn('evaluate_javascript',server.OPERATIONS)

    def test_model_cannot_override_tool_identity_or_owner(self):
        runtime=self.runtime();runtime.broker.call.return_value=[]
        runtime.call('a'*32,'files.create',{'capability':'desktop.action','approved':True})
        args=runtime.broker.call.call_args.args
        self.assertEqual(args[0],'host-owner');self.assertEqual(args[1]['capability'],'files.create')

    def test_stop_cannot_be_resumed_by_mcp(self):
        runtime=self.runtime();runtime.permissions.halt()
        for operation in ('bridge_resume','permissions_allow','files.create','chrome.action'):
            with self.subTest(operation=operation),self.assertRaises(Denied):runtime.call('a'*32,operation,{})
        runtime.broker.call.assert_not_called()

    def test_broker_denial_propagates_without_alternate_file_route(self):
        runtime=self.runtime();runtime.broker.call.side_effect=Denied('Explicit file policy denies create')
        for operation in ('files.create','files.write','files.write_approved'):
            with self.subTest(operation=operation),self.assertRaisesRegex(Denied,'Explicit file policy'):runtime.call('a'*32,operation,{'path':'C:/test/file.txt'})
        self.assertIsNone(runtime.active)

    def test_diagnostics_do_not_turn_on_desktop(self):
        runtime=self.runtime();runtime.status=lambda:{'desktop_authorized':runtime.permissions.desktop}
        for operation in ('bridge_status','bridge_health','bridge_start_services'):
            self.assertFalse(runtime.call('a'*32,operation,{})['desktop_authorized'])

    def test_client_id_and_message_object_are_bounded(self):
        runtime=self.runtime()
        for identity,args in (('a'*33,{}),('a'*32,[])):
            with self.assertRaises(Denied):runtime.call(identity,'bridge_status',args)

    def test_cancel_is_scoped_to_the_originating_client(self):
        runtime=self.runtime();event=threading.Event();runtime.inflight[('a'*32,'c'*32)]=event
        runtime.call('b'*32,'bridge_cancel_call',{'request':'c'*32});self.assertFalse(event.is_set())
        runtime.call('a'*32,'bridge_cancel_call',{'request':'c'*32});self.assertTrue(event.is_set())

    def test_disconnect_cancels_own_inflight_actions(self):
        runtime=self.runtime();own=threading.Event();other=threading.Event();runtime.inflight={('a'*32,'c'*32):own,('b'*32,'d'*32):other}
        runtime.call('a'*32,'bridge_detach',{});self.assertTrue(own.is_set());self.assertFalse(other.is_set())

    def test_consistent_backup_preserves_history_and_is_idempotent(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp);store=Store(directory);conversation=store.new('Keep me');store.add(conversation,'user','Preserve this history')
            result=backup_state(directory)
            with closing(sqlite3.connect(result/'assistant.sqlite3')) as db:self.assertEqual(db.execute('SELECT title FROM conversations').fetchone()[0],'Keep me')
            self.assertEqual(backup_state(directory),result);self.assertEqual(store.conversation(conversation)['title'],'Keep me');store.close()

    def test_legacy_project_migration_preserves_results_and_revokes_launch_scope(self):
        from assistant.projects import ProjectQueue
        with tempfile.TemporaryDirectory() as tmp:
            queue=ProjectQueue(Path(tmp));project=queue.create('old-chat','Keep the completed local product')['project']
            with queue.lock:
                queue.db.execute("UPDATE projects SET state='completed' WHERE id=?",(project,));queue.db.execute('INSERT INTO scopes VALUES(?,?,?,?,?,0)',('old-scope',project,'old-store','{}',time.time()+3600));queue.db.commit()
            self.assertEqual(migrate_projects(queue,'official-owner'),1)
            self.assertEqual(queue.owned(project,'official-owner')['state'],'completed')
            self.assertEqual(queue.rows('SELECT revoked FROM scopes')[0]['revoked'],1)
            self.assertEqual(migrate_projects(queue,'official-owner'),0)
            self.assertTrue(list((Path(tmp)/'state-backups/before-bridge-project-migration').glob('*.sqlite3')));queue.close()

    def test_reasoning_requires_running_owned_project_and_completed_dependencies(self):
        from assistant.projects import ProjectQueue
        with tempfile.TemporaryDirectory() as tmp:
            queue=ProjectQueue(Path(tmp))
            runtime=self.runtime();runtime.broker.projects.queue=queue
            runtime.broker.chrome.status.return_value={'connected':False}
            runtime.broker.chrome.grants={};runtime.broker.chrome.selected=None
            project=queue.create(runtime.owner,'Dependency readiness')['project']
            queue.add(project,runtime.owner,[{'key':'first','kind':'reason','payload':{}},{'key':'last','kind':'reason','payload':{},'needs':['first']}])
            jobs={row['key']:row for row in queue.rows('SELECT * FROM jobs')}
            self.assertEqual(runtime.status()['waiting_for_codex'],[])
            queue.db.execute("UPDATE projects SET state='running'");queue.db.commit()
            self.assertEqual([row['id'] for row in runtime.status()['waiting_for_codex']],[jobs['first']['id']])
            with self.assertRaisesRegex(Denied,'prerequisites'):
                runtime.call('a'*32,'bridge_reason_result',{'job':jobs['last']['id'],'result':{'ok':True}})
            runtime.call('a'*32,'bridge_reason_result',{'job':jobs['first']['id'],'result':{'ok':True}})
            self.assertEqual([row['id'] for row in runtime.status()['waiting_for_codex']],[jobs['last']['id']])
            queue.db.execute("UPDATE projects SET state='paused'");queue.db.commit()
            self.assertEqual(runtime.status()['waiting_for_codex'],[])
            queue.close()


if __name__=='__main__':unittest.main()
