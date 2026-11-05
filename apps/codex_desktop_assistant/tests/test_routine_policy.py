"""Routine automation never becomes a blanket approval or a new file grant."""
import sys,tempfile,threading,unittest
from pathlib import Path
from unittest.mock import Mock
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[3])]
from assistant.file_policy import FilePolicy
from assistant.permissions import Permissions,origin
from assistant.storage import Store
from bridge.routine_policy import routine_reason,PROJECT_ROOT
from bridge.runtime import Runtime


class RoutinePolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'project';self.root.mkdir();self.path=self.root/'release.zip';self.path.write_bytes(b'PKfixture')
        self.policy=FilePolicy();self.site=origin('https://payhip.com')
    def reason(self,details):return routine_reason(details,file_policy=self.policy,roots=[self.root],authorized_origins={self.site})
    def read(self,**changes):return {'file_permission':True,'operation':'read','path':str(self.path),'expected':{'kind':'file'},**changes}
    def draft(self,**changes):
        context={'source':'browser','credential_form':False,'form_submission':True,'form_visibility':'invisible','form_method':'POST','form_id':'addproduct','page_url':'https://payhip.com/product/edit/Existing123','form_action':'https://payhip.com/product/editit','label':'Save Changes',**changes}
        return {'operation':'click','approval_category':'submission','target_context':context}
    def test_project_read_only_with_no_explicit_rule(self):
        self.assertTrue(self.reason(self.read()))
        self.assertIsNone(self.reason(self.read(path=str(self.root.parent/'private.txt'))))
        for action in ['write','create','delete']:self.assertIsNone(self.reason(self.read(operation=action)))
        self.assertTrue(self.reason(self.read(expected={'kind':'folder'},path=str(self.root))))
        self.assertIsNone(self.reason(self.read(expected={'kind':'missing'})))
    def test_explicit_ask_and_deny_and_session_rules_still_win(self):
        for scope in ['file','folder','recursive']:
            for decision in ['ask','deny']:
                self.policy.rules=[FilePolicy.rule(self.path if scope=='file' else self.root,scope,{'read':decision})]
                self.assertIsNone(self.reason(self.read()),(scope,decision))
        self.policy.rules=[];self.policy.session=[FilePolicy.rule(self.path,'file',{'read':'ask'})]
        self.assertIsNone(self.reason(self.read()))
    def test_deny_not_overridden_by_a_more_specific_allow(self):
        self.policy.rules=[FilePolicy.rule(self.root,'recursive',{'read':'deny'}),FilePolicy.rule(self.path,'file',{'read':'allow'})]
        self.assertIsNone(self.reason(self.read()))
    def test_existing_url_is_limited_to_current_authorized_site(self):
        self.assertTrue(self.reason({'operation':'existing_tab_reference','query':'https://payhip.com/product/edit/id'}))
        for query in ['Payhip','https://bank.example/private','https://user:password@payhip.com/private','javascript:alert(1)']:
            self.assertIsNone(self.reason({'operation':'existing_tab_reference','query':query}))
    def test_screenshots_and_attachment_do_not_expand_sites(self):
        self.assertTrue(self.reason({'operation':'chrome_screenshot','target_context':{'origin':self.site}}))
        self.assertIsNone(self.reason({'operation':'chrome_screenshot','target_context':{'origin':'https://bank.example:443'}}))
        self.assertTrue(self.reason({'operation':'website_access','chrome_tab':True,'origin':self.site}))
        self.assertIsNone(self.reason({'operation':'website_access','origin':self.site}))
    def test_only_known_existing_invisible_product_save_is_routine(self):
        self.assertTrue(self.reason(self.draft()))
        for change in [{'form_visibility':'visible'},{'form_visibility':'unlisted'},{'form_method':'GET'},{'form_submission':False},{'credential_form':True},{'page_url':'https://bank.example/product/edit/id'},{'page_url':'https://payhip.com/product/add'},{'form_action':'https://evil.example/save'},{'form_id':'account'},{'label':'Publish'}]:
            self.assertIsNone(self.reason(self.draft(**change)),change)
    def test_upload_and_sensitive_categories_and_unknown_requests_ask(self):
        for category in ['payment','publication','security','destructive','filesystem','unverified_target']:
            self.assertIsNone(self.reason({**self.draft(),'approval_category':category}))
        self.assertIsNone(self.reason({**self.draft(),'operation':'upload'}))
        self.assertIsNone(self.reason({'operation':'manual_step','manual_step':True}))
        self.assertIsNone(self.reason({'operation':'decision','approved':True,'routine':True}))


class RuntimeRoutineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.r=Runtime.__new__(Runtime);r=self.r;r.store=Store(Path(self.tmp.name));self.addCleanup(r.store.close)
        r.owner=r.store.new();r.permissions=Permissions();r.permissions.resume(r.owner);r.store.setting('routine_approvals',True)
        r.broker=Mock();r.broker.chrome.status.return_value={'attached':[{'origin':origin('https://payhip.com'),'conversation':r.owner}]}
        r.emit=Mock();r.requests=[];r.closed=threading.Event();r.latest='Ready'
    def test_routine_action_is_audited_and_does_not_create_an_approval_card(self):
        self.assertTrue(self.r.approve(self.r.owner,'Use exact tab',{'operation':'existing_tab_reference','query':'https://payhip.com/products'}))
        self.assertFalse(self.r.requests);self.r.emit.assert_called_once();self.assertEqual(self.r.emit.call_args.args[0],'auto_approved')
    def test_stop_and_other_owner_are_not_overridden(self):
        details={'operation':'existing_tab_reference','query':'https://payhip.com/products'}
        self.assertFalse(self.r.approve('different-owner','No',details));self.r.permissions.halt()
        self.assertFalse(self.r.approve(self.r.owner,'No',details));self.r.emit.assert_not_called()
    def test_explicit_read_ask_still_uses_the_genuine_request(self):
        path=PROJECT_ROOT/'outputs/fixture.zip';self.r.permissions.file_policy.rules=[FilePolicy.rule(path,'file',{'read':'ask'})]
        def deny(kind,conversation,request):
            if kind=='request':request['event'].set()
        self.r.emit.side_effect=deny
        self.assertFalse(self.r.approve(self.r.owner,'Read fixture',{'file_permission':True,'operation':'read','path':str(path),'expected':{'kind':'file'}}))
        self.assertEqual(len(self.r.requests),1)


if __name__=='__main__':unittest.main()
