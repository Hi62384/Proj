"""Conversation, origin, approval and file boundaries for existing Chrome."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[3])]
from assistant.chrome_control import ChromeControl
from assistant.permissions import Permissions,Denied,origin
from assistant.storage import Store
from assistant.attachments import Attachments


class FakeBridge:
    def __init__(self):
        self.state={'connected':True,'session':'session-one','tabs':[{'tab':42,'window':3,'origin':origin('https://example.org'),'manual':False}]}
        self.calls=[];self.context={'source':'browser','label':'Notes','role':'Edit','tag':'TEXTAREA','editable':True,'page_url':'https://example.org/editor','form_action':'https://example.org/upload'}
        self.on_request=lambda operation,args:None
    def status(self):return copy.deepcopy(self.state)
    def request(self,operation,args,guard=None,**kwargs):
        if guard:guard()
        self.on_request(operation,args);self.calls.append((operation,copy.deepcopy(args)))
        if operation=='context':return dict(self.context)
        if operation=='inspect':return {'url':'https://example.org/editor','observation':'obs','controls':[]}
        if operation in ('list_tabs','find_tabs'):return {'tabs':self.state['tabs']}
        if operation=='open_tab':return {'tab':43,'authorized':False}
        return {'dispatched':True}
    def stop_tabs(self):self.state['tabs']=[]


class ChromeControlTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.store=Store(self.root/'state');self.addCleanup(self.store.close)
        self.conversation=self.store.new();self.p=Permissions();self.p.resume(self.conversation)
        self.approve=Mock(return_value=True);self.attachments=Attachments(self.store.directory)
        self.control=ChromeControl(self.p,self.store,self.approve,Mock(),self.attachments);self.bridge=FakeBridge();self.control.bridge=self.bridge
    def attach(self):self.control.attach(self.conversation,42,ask=False)
    def inspect(self):return self.control.call(self.conversation,'inspect',{'tab':42})
    def action(self,operation='fill',**extra):
        return self.control.call(self.conversation,'action',{'tab':42,'observation':'obs','element':0,'operation':operation,**extra})

    def test_open_background_tab_without_attached_tab(self):
        original=self.bridge.request
        def request(operation,args,**kwargs):
            if operation=='open_tab':
                kwargs['guard']();return {'tab':99,'authorized':False}
            return original(operation,args,**kwargs)
        self.bridge.request=request
        self.assertEqual(self.control.call(self.conversation,'open_tab',{'url':'https://other.example'})['tab'],99)
        self.approve.assert_not_called()
        with self.assertRaises(Denied):self.control.call(self.conversation,'inspect',{'tab':99})

    def test_unavailable_background_capture_never_requests_consent(self):
        self.attach()
        def reject(operation,args):
            if operation=='observe_check':raise Denied('Background screenshots are unavailable. Use DOM inspection.')
        self.bridge.on_request=reject
        with self.assertRaisesRegex(Denied,'Background screenshots'):self.control.call(self.conversation,'observe',{'tab':42})
        self.approve.assert_not_called()

    def test_show_is_available_to_local_ui_without_becoming_a_model_capability(self):
        from assistant.tools import CAPABILITIES
        self.attach();self.control.call(self.conversation,'show',{'tab':42})
        self.assertEqual(self.bridge.calls[-1][0],'show');self.assertNotIn('chrome.show',CAPABILITIES)

    def test_new_site_permitted_tab_attaches_without_repeated_review(self):
        original=self.bridge.request
        def request(operation,args,**kwargs):
            if operation=='open_tab':
                kwargs['guard']();self.bridge.state['tabs'].append({'tab':99,'origin':origin('https://example.org'),'manual':False})
                return {'tab':99,'authorized':True}
            return original(operation,args,**kwargs)
        self.bridge.request=request
        self.control.call(self.conversation,'open_tab',{'url':'https://example.org'})
        self.control.call(self.conversation,'inspect',{'tab':99});self.approve.assert_not_called()

    def test_clean_close_automatic_but_possible_edits_reviewed(self):
        self.attach();original=self.bridge.request
        for dirty in (False,True):
            def request(operation,args,**kwargs):
                if operation=='close_check':return {'may_lose_edits':dirty,'close_token':'checked'}
                return original(operation,args,**kwargs)
            self.bridge.request=request
            self.control.call(self.conversation,'close_tab',{'tab':42,'close_token':'forged'})
            self.assertEqual(self.bridge.calls[-1][1]['close_token'],'checked')
        self.assertEqual(self.approve.call_count,1)

    def test_explicit_popup_grant_attaches_on_requested_use_without_another_prompt(self):
        self.inspect();self.approve.assert_not_called()
        self.assertEqual(self.control.grants[42]['conversation'],self.conversation)
        with self.assertRaises(Denied):self.control.call(self.conversation,'inspect',{'tab':999})

    def test_model_attachment_requests_real_local_approval(self):
        self.control.attach(self.conversation,42);self.approve.assert_called_once()
        self.assertTrue(self.approve.call_args.args[2]['chrome_tab']);self.inspect()

    def test_deny_attachment_prevents_content_access(self):
        self.approve.return_value=False
        with self.assertRaises(Denied):self.control.attach(self.conversation,42)
        self.assertFalse(self.bridge.calls)

    def test_multiline_typing_does_not_request_approval(self):
        self.attach();self.inspect();self.action(text='First\nSecond\nPublish is ordinary text')
        self.approve.assert_not_called();self.assertEqual(self.bridge.calls[-1][0],'action')

    def test_publication_and_actual_post_form_each_need_review(self):
        self.attach()
        for context in ({'label':'Publish product','role':'Button'},{'label':'Continue','form_submission':True,'form_method':'POST','role':'Button'}):
            self.bridge.context.update(context);self.inspect();self.action('click')
        self.assertEqual(self.approve.call_count,2)

    def test_fake_model_approval_cannot_bypass_real_denial(self):
        self.attach();self.inspect();self.bridge.context.update(label='Buy now',role='Button');self.approve.return_value=False
        with self.assertRaises(Denied):self.action('click',approved=True,routine=True)
        self.assertFalse(any(op=='action' for op,_ in self.bridge.calls))

    def test_ordinary_scripted_controls_run_without_blanket_review(self):
        self.attach();self.inspect();self.bridge.context.update(label='Continue',role='Button',scripted_button=True)
        self.action('click');self.approve.assert_not_called()
        self.inspect();self.bridge.context.update(label='Publish',expands_menu=True)
        self.action('click');self.assertEqual(self.approve.call_count,1)

    def test_other_conversation_cannot_use_attached_tab(self):
        self.attach();self.p.resume('another')
        with self.assertRaises(Denied):self.control.call('another','inspect',{'tab':42})

    def test_full_scope_uses_a_fresh_tab_for_cross_domain_navigation(self):
        self.attach();self.bridge.state['full_browser']=True
        result=self.control.call(self.conversation,'navigate',{'tab':42,'url':'https://other.example/page'})
        self.assertEqual(result['tab'],43);self.assertEqual(self.bridge.calls[-1][0],'open_tab');self.approve.assert_not_called()

    def test_existing_tab_search_needs_full_scope_and_real_owner_reference(self):
        self.bridge.state['full_browser']=True;self.store.add(self.conversation,'system','Use example tab')
        with self.assertRaises(Denied):self.control.call(self.conversation,'find_tabs',{'query':'example'})
        self.store.add(self.conversation,'user','Use my example tab')
        self.control.call(self.conversation,'adopt_tab',{'tab':42,'query':'example'})
        self.approve.assert_not_called();self.assertEqual(self.control.selected,42)
        with self.assertRaises(Denied):self.control.call(self.conversation,'adopt_tab',{'tab':999,'query':'example'})
        self.bridge.state['full_browser']=False
        with self.assertRaises(Denied):self.control.call(self.conversation,'find_tabs',{'query':'example','approved':True})

    def test_navigation_cannot_expand_site_scope(self):
        self.attach()
        with self.assertRaises(Denied):self.control.call(self.conversation,'navigate',{'tab':42,'url':'https://other.example'})
        self.assertFalse(self.bridge.calls)

    def test_extension_origin_change_revokes_effective_authority(self):
        self.attach();self.bridge.state['tabs'][0]['origin']=origin('https://other.example')
        with self.assertRaises(Denied):self.inspect()

    def test_manual_control_blocks_reading_and_writing(self):
        self.attach();self.inspect();self.bridge.state['tabs'][0]['manual']=True
        for operation in ('inspect','action'):
            with self.assertRaises(Denied):self.control.call(self.conversation,operation,{'tab':42})

    def test_stop_invalidates_tab_and_stale_generation(self):
        self.attach();self.p.revoke();self.p.resume(self.conversation)
        with self.assertRaises(Denied):self.inspect()

    def test_reconnection_never_restores_attached_authority(self):
        self.attach();self.bridge.state['session']='replacement'
        with self.assertRaises(Denied):self.inspect()

    def test_changed_context_after_review_prevents_dispatch(self):
        self.attach();self.inspect();self.bridge.context.update(label='Publish',role='Button')
        self.approve.side_effect=lambda *args:(self.bridge.context.update(label='Delete account') or True)
        with self.assertRaises(Denied):self.action('click')
        self.assertFalse(any(op=='action' for op,_ in self.bridge.calls))

    def test_stop_during_review_prevents_dispatch(self):
        self.attach();self.inspect();self.bridge.context.update(label='Publish',role='Button')
        self.approve.side_effect=lambda *args:(self.p.halt() or True)
        with self.assertRaises(Denied):self.action('click')

    def test_upload_rejects_arbitrary_local_paths(self):
        self.attach();self.inspect()
        with self.assertRaises(Denied):self.action('upload',path=str(self.root/'file.txt'),approved_path='C:/Windows/secret')
        self.approve.assert_not_called()

    def test_upload_checks_file_hash_and_chunk_bytes(self):
        source=self.root/'synthetic.bin';raw=b'ordinary synthetic bytes'*15000;source.write_bytes(raw);record=self.attachments.add(source)
        self.attach();self.inspect()
        self.control.call(self.conversation,'action',{'tab':42,'observation':'obs','element':0,'operation':'upload','attachment_id':record['id']},{record['id']:record})
        import base64
        chunks=[args for op,args in self.bridge.calls if op=='upload_chunk']
        self.assertEqual(b''.join(base64.b64decode(c['data']) for c in chunks),raw)
        self.assertEqual(self.approve.call_args.args[2]['file']['name'],'synthetic.bin')
        self.assertEqual(next(a for op,a in self.bridge.calls if op=='upload_begin')['name'],'synthetic.bin')

    def test_upload_rejects_changed_attachment_and_external_destination(self):
        source=self.root/'synthetic.txt';source.write_text('original');record=self.attachments.add(source)
        self.attach();self.inspect();self.attachments.path(record).write_text('changed')
        args={'tab':42,'observation':'obs','element':0,'operation':'upload','attachment_id':record['id']}
        with self.assertRaises(Denied):self.control.call(self.conversation,'action',args,{record['id']:record})
        self.inspect();self.bridge.context['form_action']='https://other.example/upload'
        with self.assertRaises(Denied):self.control.call(self.conversation,'action',args,{record['id']:record})


if __name__=='__main__':unittest.main()
