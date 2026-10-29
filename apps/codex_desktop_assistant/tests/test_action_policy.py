"""Approval regression: data entry versus real target activation."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[3])]
from assistant.action_policy import classify,request_review
from assistant.permissions import Permissions,Denied
from assistant.tools import Broker
from assistant.storage import Store


class ClassificationTests(unittest.TestCase):
    def context(self,**kwargs):return {'source':'desktop','role':'Button','label':'Continue',**kwargs}

    def test_multiline_notepad_text_is_data_even_with_commit_words(self):
        for role in ('Edit','Document'):
            for label in ('Text Editor','Send\nPublish\nBuy now','Submission notes'):
                self.assertFalse(classify('type',self.context(role=role,label=label,local_editor=True)).required)

    def test_enter_in_verified_notepad_inserts_newline(self):
        self.assertFalse(classify('keypress',self.context(role='Document',key='ENTER',local_editor=True)).required)
        self.assertTrue(classify('keypress',self.context(role='Edit',key='ENTER',local_editor=False)).required)

    def test_enter_does_not_bypass_notepad_save_button_or_file_dialog(self):
        self.assertTrue(classify('keypress',self.context(role='Button',label='Save',key='ENTER',local_editor=True)).required)
        self.assertTrue(classify('keypress',self.context(role='Edit',label='File name',key='ENTER',local_editor=True,file_dialog=True)).required)

    def test_typing_space_into_button_is_not_editor_text_entry(self):
        self.assertTrue(classify('type',self.context(role='Button',label='Buy now')).required)

    def test_forged_edit_role_does_not_hide_actual_form_submission(self):
        self.assertTrue(classify('click',self.context(source='browser',role='Edit',label='Continue',form_submission=True,form_method='POST')).required)

    def test_normal_buttons_not_ambiguous_substrings(self):
        for label in ('Display','Sender','Submitter details','Publisher','Publication settings','Purchase history','Payment options','Remove formatting','Previous','Apply draft','Next','Open panel'):
            with self.subTest(label=label):self.assertFalse(classify('click',self.context(label=label)).required)

    def test_edit_field_focus_does_not_activate_its_label(self):
        for label in ('Publish','Pay now','Delete account'):
            self.assertFalse(classify('click',self.context(role='Edit',label=label)).required)

    def test_routine_navigation_and_edit_commands(self):
        for operation in ('focus','scroll','move_mouse','move_window','type','select','check','navigate','new_tab','switch_tab'):
            self.assertFalse(classify(operation,self.context(role='Edit' if operation=='type' else 'Button',label='Payment details')).required)
        for key in ('CTRL+A','BACKSPACE','TAB','ESC','HOME','DOWN'):
            self.assertFalse(classify('keypress',self.context(key=key)).required)

    def test_browser_multiline_fill_is_not_submission(self):
        self.assertFalse(classify('fill',self.context(source='browser',role='Edit',tag='TEXTAREA',label='Send message',form_method='POST')).required)

    def test_actual_form_submission_needs_review(self):
        decision=classify('click',self.context(source='browser',form_submission=True,form_method='POST',label='Continue'))
        self.assertTrue(decision.required);self.assertIn('form submission',decision.reason)

    def test_search_get_form_is_routine(self):
        self.assertFalse(classify('click',self.context(source='browser',form_submission=True,form_method='GET',label='Search')).required)
        self.assertFalse(classify('press',self.context(source='browser',role='Edit',key='Enter',form_submission=True,form_method='GET')).required)

    def test_textarea_enter_versus_enter_to_send(self):
        self.assertFalse(classify('press',self.context(source='browser',tag='TEXTAREA',role='Edit',key='Enter')).required)
        self.assertTrue(classify('press',self.context(source='browser',tag='TEXTAREA',role='Edit',key='Enter',enter_submits=True)).required)

    def test_purchase_publication_security_and_destructive_controls(self):
        for label in ('Buy now','Pay $20','Purchase','Place order','Confirm payment','Publish product','Save & Publish','Make public','Deploy','Delete file','Remove account','Remove','Change password','Transfer funds','Run macro'):
            with self.subTest(label=label):self.assertTrue(classify('click',self.context(label=label)).required)

    def test_publication_and_credential_context_override_get_form(self):
        self.assertTrue(classify('click',self.context(source='browser',label='Publish',form_method='GET',form_submission=True)).required)
        self.assertTrue(classify('click',self.context(source='browser',label='Save',credential_form=True)).required)

    def test_submenu_is_navigation_not_commit(self):
        self.assertFalse(classify('click',self.context(role='MenuItem',label='Publish',expands_menu=True)).required)
        self.assertTrue(classify('keypress',self.context(role='MenuItem',label='File',key='CTRL+S',expands_menu=True)).required)

    def test_editor_delete_selection_is_not_filesystem_delete(self):
        self.assertFalse(classify('click',self.context(role='MenuItem',local_editor=True,label='Delete')).required)
        self.assertTrue(classify('click',self.context(label='Delete')).required)

    def test_pixel_unknown_and_native_save_still_reviewed(self):
        self.assertTrue(classify('coordinate_click',self.context()).required)
        self.assertTrue(classify('keypress',self.context(local_editor=True,key='CTRL+S')).required)

    def test_shell_navigation_is_separate_from_file_activation(self):
        context=self.context(filesystem_activation=True,role='ListItem',label='example.exe')
        self.assertFalse(classify('right_click',context).required)
        self.assertFalse(classify('keypress',{**context,'key':'DOWN'}).required)
        self.assertTrue(classify('double_click',context).required)

    def test_network_backstop_matches_operations_not_substrings(self):
        for url in ('https://example.org/publication/settings','https://example.org/purchase-history','https://example.org/draft/autosave'):
            self.assertFalse(request_review('POST',url).required)
        for method,url in [('POST','https://example.org/api/publish'),('POST','https://example.org/api/sendMessage'),('POST','https://example.org/api/publish-product'),('DELETE','https://example.org/item/1'),('GET','https://example.org/?action=delete')]:
            self.assertTrue(request_review(method,url).required)


class BrokerApprovalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.store=Store(Path(self.tmp.name)/'private');self.addCleanup(self.store.close);self.conversation=self.store.new()
        self.p=Permissions();self.p.desktop=True;self.p.desktop_mode='Entire Monitor';self.p.resume(self.conversation)
        self.desktop=Mock();self.browser=Mock();self.approve=Mock(return_value=True)
        self.broker=Broker(self.p,self.desktop,self.browser,Mock(),self.store,Mock(),self.approve)
        self.control=Mock();self.control.element_info.name='Text Editor';self.control.window_text.return_value='Text Editor'
        self.desktop.observations={123:('token',0,{1:self.control})};self.desktop.control.return_value={}
        self.desktop.window.return_value.window_text.return_value='Synthetic Notepad'
        self.desktop.action_context.return_value={'source':'desktop','role':'Document','label':'Text Editor','local_editor':True}

    def call(self,cap,args):return self.broker.call(self.conversation,{'capability':cap,'arguments':json.dumps(args)})

    def test_repeated_multiline_notepad_editing_asks_zero_times(self):
        for text in ('First line\nSecond line','Publish a note\r\nBuy milk','Edited first\nEdited second'):
            self.call('desktop.action',{'window':123,'observation':'token','element':1,'operation':'type','text':text})
        self.approve.assert_not_called();self.assertEqual(self.desktop.control.call_count,3)

    def test_model_supplied_routine_hint_cannot_hide_publication(self):
        self.desktop.action_context.return_value={'source':'desktop','role':'Button','label':'Publish product'}
        self.call('desktop.action',{'window':123,'element':1,'operation':'click','local_editor':True,'routine':True,'approved':True})
        self.approve.assert_called_once();details=self.approve.call_args.args[2]
        self.assertEqual(details['approval_category'],'publication');self.assertIn('public',details['approval_reason'])

    def test_deny_prevents_actual_commit(self):
        self.desktop.action_context.return_value={'source':'desktop','role':'Button','label':'Pay now'};self.approve.return_value=False
        with self.assertRaises(Denied):self.call('desktop.action',{'window':123,'element':1,'operation':'click'})
        self.desktop.control.assert_not_called()

    def test_routine_label_allowlist_cannot_override_real_commit(self):
        self.p.routine_labels.add('publish product')
        self.broker._review(self.conversation,'Publish product',{'operation':'click'},self.p.generation)
        self.approve.assert_called_once()

    def test_entire_monitor_does_not_grant_file_access(self):
        path=Path(self.tmp.name)/'ordinary.txt';path.write_text('original')
        self.p.file_policy.rules=[{'path':str(path),'scope':'file','decisions':{'read':'deny','write':'deny','create':'deny','delete':'deny'}}]
        for action in ('read','write','delete'):
            with self.subTest(action=action),self.assertRaises(Denied):self.call('files.'+action,{'path':str(path)})
        self.assertEqual(path.read_text(),'original');self.approve.assert_not_called()


if __name__=='__main__':unittest.main()
