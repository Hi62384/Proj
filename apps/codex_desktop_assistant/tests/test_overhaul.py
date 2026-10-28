"""Actual Windows file operations plus policy/state regression coverage."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[3])]
from assistant.files import Files
from assistant.file_policy import FilePolicy,ACTIONS
from assistant.permissions import Permissions,Denied
from assistant.storage import Store
from assistant.desktop import Desktop


class FileTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.store=Store(self.root/'private');self.addCleanup(self.store.close)
        self.permissions=Permissions();self.permissions.resume('owner');self.approve=Mock(return_value=True)
        self.files=Files(self.permissions,self.store,self.approve);self.path=self.root/'sample.txt';self.path.write_text('before')

    def rule(self,action,decision,path=None,scope='file'):
        self.permissions.file_policy.rules=[FilePolicy.rule(path or self.path,scope,{action:decision})]

    def call(self,action,path=None,**args):
        return self.files.call('owner',{'path':str(path or self.path),**args},action)

    def test_default_asks_each_action(self):
        for action in ACTIONS:self.assertEqual(self.permissions.file_policy.decision(self.path,action),'ask')

    def test_allow_ask_deny_all_four_actions(self):
        for action in ACTIONS:
            for decision in ('allow','ask','deny'):
                with self.subTest(action=action,decision=decision):
                    p=self.root/(action+decision+'.txt')
                    if action!='create':p.write_text('before')
                    self.rule(action,decision,p);self.approve.reset_mock()
                    args={'content':'after','sha256':hashlib.sha256(b'before').hexdigest(),'reason':'Synthetic test'}
                    if decision=='deny':
                        with self.assertRaises(Denied):self.call(action,p,**args)
                        self.approve.assert_not_called()
                    else:
                        result=self.call(action,p,**args)
                        self.assertEqual(self.approve.call_count,int(decision=='ask'))
                        if action=='delete':self.assertFalse(p.exists());self.assertEqual(Path(result['recovery']).read_bytes(),b'before')
                        elif action in ('write','create'):self.assertEqual(p.read_text(),'after')

    def test_denial_prevents_mutation(self):
        self.approve.return_value=False
        with self.assertRaises(Denied):self.call('delete',sha256=hashlib.sha256(b'before').hexdigest())
        self.assertEqual(self.path.read_text(),'before')

    def test_allow_once_does_not_grant_future_access(self):
        self.call('read');self.call('read');self.assertEqual(self.approve.call_count,2)
        self.assertEqual(self.permissions.file_policy.session,[])

    def test_session_exact_action_and_target_then_expires(self):
        self.permissions.file_policy.session.append(FilePolicy.rule(self.path,'file',{'read':'allow'}))
        self.call('read');self.approve.assert_not_called()
        self.assertEqual(self.permissions.file_policy.decision(self.path,'delete'),'ask')
        self.assertEqual(self.permissions.file_policy.decision(self.root/'other','read'),'ask')
        self.permissions.revoke();self.assertEqual(self.permissions.file_policy.session,[])

    def test_folder_nonrecursive_and_recursive(self):
        child=self.root/'sub'/'x.txt'
        self.rule('read','allow',self.root,'folder')
        self.assertEqual(self.permissions.file_policy.decision(self.path,'read'),'allow')
        self.assertEqual(self.permissions.file_policy.decision(child,'read'),'ask')
        self.rule('read','allow',self.root,'recursive');self.assertEqual(self.permissions.file_policy.decision(child,'read'),'allow')

    def test_deny_cannot_be_overridden_by_session_grant(self):
        self.rule('read','deny',self.root,'recursive')
        self.permissions.file_policy.session.append(FilePolicy.rule(self.path,'file',{'read':'allow'}))
        with self.assertRaises(Denied):self.call('read')
        self.approve.assert_not_called()

    def test_changed_target_during_approval(self):
        def change(*args):self.path.write_text('human change');return True
        self.approve.side_effect=change
        with self.assertRaises(Denied):self.call('write',content='after',sha256=hashlib.sha256(b'before').hexdigest())
        self.assertEqual(self.path.read_text(),'human change')

    def test_revoked_during_approval(self):
        def revoke(*args):self.permissions.halt();return True
        self.approve.side_effect=revoke
        with self.assertRaises(Denied):self.call('delete',sha256=hashlib.sha256(b'before').hexdigest())
        self.assertTrue(self.path.exists())

    def test_protected_paths_cannot_be_allowed(self):
        for path in (self.store.directory/'secret.txt',Path.home()/'.ssh/id_rsa',Path('C:/Windows/win.ini'),Path.home()/'AppData/Local/Google/Chrome/User Data/Default/Cookies'):
            with self.subTest(path=path):
                self.rule('read','allow',path)
                with self.assertRaises(Denied):self.call('read',path)
        self.approve.assert_not_called()

    def test_traversal_and_alternate_streams(self):
        for path in (str(self.root/'sub'/'..'/'sample.txt'),str(self.path)+':secret'):
            with self.assertRaises(Denied):self.files.validate(path)

    def test_hardlink_escape(self):
        import os
        link=self.root/'hard.txt';os.link(self.path,link)
        with self.assertRaises(Denied):self.call('read',link)

    def test_empty_folder_create_delete_and_nonempty_denied(self):
        folder=self.root/'output';self.call('create',folder,kind='folder')
        (folder/'x.txt').write_text('x')
        with self.assertRaises(Denied):self.call('delete',folder,sha256='empty-folder')
        listing=self.call('list',folder);self.assertEqual(listing['entries'][0]['name'],'x.txt')
        (folder/'x.txt').unlink();self.call('delete',folder,sha256='empty-folder');self.assertFalse(folder.exists())

    def test_create_never_overwrites_and_write_hash_required(self):
        with self.assertRaises(Denied):self.call('create',content='after')
        with self.assertRaises(Denied):self.call('write',content='after',sha256='wrong')
        self.assertEqual(self.path.read_text(),'before')

    def test_write_recovery_bytes_and_verified_hash(self):
        result=self.call('write',content='after',sha256=hashlib.sha256(b'before').hexdigest())
        self.assertEqual(Path(result['recovery']).read_bytes(),b'before');self.assertEqual(result['sha256'],hashlib.sha256(b'after').hexdigest())

    def test_binary_file_hash_allows_real_recoverable_deletion(self):
        raw=b'PK\x03\x04\x00\xffbinary fixture';self.path.write_bytes(raw)
        result=self.call('read');self.assertTrue(result['binary'])
        deleted=self.call('delete',sha256=result['sha256'])
        self.assertFalse(self.path.exists());self.assertEqual(Path(deleted['recovery']).read_bytes(),raw)

    def test_deny_checked_before_reading_bytes(self):
        from unittest.mock import patch
        self.rule('read','deny')
        with patch.object(Path,'read_bytes',side_effect=AssertionError('Unapproved bytes read')):
            with self.assertRaises(Denied):self.call('read')

    def test_ask_read_does_not_open_content_until_owner_approves(self):
        from unittest.mock import patch
        original=Path.read_bytes;approved=[False]
        def check(path):
            self.assertTrue(approved[0]);return original(path)
        def allow(*args):approved[0]=True;return True
        self.approve.side_effect=allow
        with patch.object(Path,'read_bytes',check):self.assertEqual(self.call('read')['content'],'before')

    def test_legacy_saved_tool_alias_uses_current_file_policy(self):
        from assistant.tools import Broker
        broker=Broker(self.permissions,Mock(),Mock(),Mock(),self.store,Mock(),self.approve)
        self.rule('read','deny')
        with self.assertRaises(Denied):broker.call('owner',{'capability':'files.read_approved','arguments':json.dumps({'operation':'read','path':str(self.path)})})
        self.rule('read','ask')
        result=broker.call('owner',{'capability':'files.read_approved','arguments':json.dumps({'operation':'read','path':str(self.path)})})
        self.assertEqual(json.loads(result[0]['text'])['content'],'before');self.approve.assert_called_once()

    def test_preferences_persist_without_desktop_authority(self):
        self.store.setting('file_rules',[FilePolicy.rule(self.root,'recursive',{'read':'allow'})]);self.store.selection('actual-model','high')
        other=Store(self.store.directory)
        try:
            self.assertEqual(other.settings()['model'],'actual-model');self.assertEqual(other.settings()['effort'],'high')
            self.assertTrue(Path(other.settings()['overhaul_backup']).exists())
            self.assertTrue(Permissions().halted.is_set());self.assertEqual(Permissions().file_policy.session,[])
        finally:other.close()


class DesktopTests(unittest.TestCase):
    def test_physical_input_signal_closes_gate_even_before_focus_poll(self):
        import threading
        from assistant.attention import InputGuard
        p=Permissions();p.desktop=True;p.resume('owner');event=threading.Event()
        guard=InputGuard(p,lambda:True,lambda reason:event.set())
        try:
            guard.armed=False;guard.automation=True;guard.physical()
            self.assertTrue(p.desktop_suspended);self.assertTrue(event.wait(1))
        finally:guard.close()

    def test_monitor_scope_dynamically_accepts_ordinary_windows_only_inside(self):
        p=Permissions();p.desktop_mode='Entire Monitor';p.capture_bounds=(0,0,1000,800);p.monitor_layout=((0,0,1000,800),)
        desktop=Desktop(p);desktop.monitors=Mock(return_value=[(0,0,1000,800)]);desktop.identity=Mock(return_value=(99,'Fixture','created'))
        wrapper=Mock();wrapper.process_id.return_value=99;wrapper.class_name.return_value='Fixture';wrapper.window_text.return_value='Synthetic editor'
        rect=Mock(left=10,top=10,right=500,bottom=500);wrapper.rectangle.return_value=rect
        desktop._api=Mock();desktop._api.return_value.window.return_value.wrapper_object.return_value=wrapper
        self.assertIs(desktop.window(123),wrapper);self.assertEqual(p.windows,{})
        rect.right=1100
        with self.assertRaises(Denied):desktop.window(123)
        rect.right=500;desktop.monitors.return_value=[(0,0,1200,800)]
        with self.assertRaises(Denied):desktop.window(123)
        self.assertTrue(p.halted.is_set())

    def test_suspended_desktop_cannot_act(self):
        p=Permissions();p.resume('owner');p.desktop=True;p.desktop_suspended=True
        with self.assertRaises(Denied):Desktop(p).control({'window':1,'operation':'focus'})

    def test_installed_catalog_has_no_shell_or_download_target(self):
        from assistant.applications import catalog,BLOCK
        for label,path in catalog().items():
            self.assertEqual(Path(path).suffix.lower(),'.exe');self.assertIsNone(BLOCK.search(Path(path).name+' '+label))


if __name__=='__main__':unittest.main()
