"""First real account writes stay Invisible, exact, revocable and unreplayed."""
import sys
import time
import json
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from assistant.payhip import PayhipBrowserAdapter
from assistant.permissions import Denied
from assistant.action_policy import Review


class PayhipSafetyTests(unittest.TestCase):
    def setUp(self):
        self.chrome=Mock();self.adapter=PayhipBrowserAdapter(self.chrome,'owner',Mock(),Mock())
        self.adapter.probe_result={'new_product_url':'https://payhip.com/product/add/digital'}
        self.package={'sha256':'a'*64,'product':'inventory-test','listing':{'title':'Inventory test','price_cents':1900}}
        self.scope={'expires':time.time()+3600,'visibility':'invisible','max_new_products':1,'spending_limit_cents':0,'sha256':'a'*64,'title':'Inventory test','price_cents':1900,'currency':'CAD','assets':{'delivery.zip':{'sha256':'a'*64}},'save_urls':['https://payhip.com/product/add/digital']}
        self.adapter.authorize(self.scope);self.adapter.pending=self.package

    def test_public_unlisted_spending_and_multiple_products_rejected(self):
        for change in ({'visibility':'visible'},{'visibility':'unlisted'},{'spending_limit_cents':1},{'max_new_products':2}):
            with self.subTest(change=change),self.assertRaises(Denied):self.adapter.authorize({**self.scope,**change})

    def test_expired_changed_hash_price_title_rejected(self):
        for change in ({'expires':time.time()-1},{'sha256':'b'*64},{'price_cents':2900},{'title':'Other'}):
            self.adapter.scope={**self.scope,**change}
            with self.subTest(change=change),self.assertRaises(Denied):self.adapter.guard(self.package)

    def test_revocation_stops_account_work(self):
        self.adapter.queue=Mock();self.adapter.queue.rows.return_value=[]
        with self.assertRaises(Denied):self.adapter.guard(self.package)

    def test_only_exact_invisible_upload_bypasses_submission_review(self):
        args={'observation':'fresh','element':3,'action':'upload'};self.adapter.expected=dict(args)
        context={'page_url':'https://payhip.com/product/add/digital','type':'file','form_visibility':'invisible'}
        review=Review('Upload exact file','submission')
        self.assertTrue(self.adapter.review('owner',args,context,{'sha256':'a'*64},review))
        for changed in ({'form_visibility':'visible'},{'page_url':'https://other.example/product/add'}):
            self.assertFalse(self.adapter.review('owner',args,{**context,**changed},{'sha256':'a'*64},review))
        self.assertFalse(self.adapter.review('other',args,context,{'sha256':'a'*64},review))
        self.assertFalse(self.adapter.review('owner',args,context,{'sha256':'b'*64},review))
        self.assertFalse(self.adapter.review('owner',args,context,{'sha256':'a'*64},Review('Publish','publication')))

    def test_fields_must_have_exact_title_price_and_invisible(self):
        controls=[{'name':'p_name','value':'Inventory test'},{'name':'p_price','value':'19.00'},{'name':'product_status','value':'invisible','checked':True}]
        self.assertTrue(self.adapter.verify_fields({'controls':controls}))
        controls[-1]['checked']=False
        self.assertFalse(self.adapter.verify_fields({'controls':controls}))

    def test_incomplete_saved_file_verification_cannot_complete_job(self):
        self.adapter.prepare=Mock(return_value={'files_verified':False,'reason':'Saved bytes unavailable'})
        with self.assertRaisesRegex(Denied,'Saved bytes unavailable'):
            self.adapter.prepare_hidden(self.package,Path('unused'),Mock(),lambda:None)

    def test_account_security_payment_and_publication_routes_rejected(self):
        for path in ('settings','payment','checkout','delete','publish','auth'):
            with self.subTest(path=path),self.assertRaises(Denied):self.adapter.url('https://payhip.com/'+path)

    def recovery_fixture(self):
        self.adapter.scope.update(archive_name='delivery.zip',upload_receivers=['https://pe56d.s3.amazonaws.com/'],max_blocked_transfer_retries=1)
        self.adapter.probe_result={'new_product_url':'https://payhip.com/product/add/digital'};self.adapter.verify_fields=Mock(return_value=True);self.adapter.checkpoint=Mock()
        snapshot={'url':'https://payhip.com/product/add/digital','text':'delivery.zip Uploading...','commerce':{'upload_receiver':'https://pe56d.s3.amazonaws.com/','digital_files_state':'valid','digital_files':[]}}
        self.adapter.inspect=Mock(return_value=snapshot)
        prior={'phase':'asset_selected','name':'delivery.zip','tab':42,'recovery_attempts':0}
        return snapshot,{'fingerprint':'a'*64,'result':json.dumps(prior)},prior

    def test_controlled_retry_requires_empty_valid_receipts_and_original_editor(self):
        snapshot,effect,prior=self.recovery_fixture();snapshot['commerce']['digital_files']=[{'name':'delivery.zip','receipt':True}]
        with self.assertRaisesRegex(Denied,'receipt state changed'):self.adapter.reconcile_blocked_transfer(effect,self.package)
        self.adapter.checkpoint.assert_not_called()

    def test_recovery_cannot_repeat_an_already_consumed_retry(self):
        snapshot,effect,prior=self.recovery_fixture();prior['recovery_attempts']=1;effect['result']=json.dumps(prior)
        with self.assertRaises(Denied):self.adapter.reconcile_blocked_transfer(effect,self.package)
        self.adapter.checkpoint.assert_not_called()

    def test_controlled_retry_consumes_a_durable_single_attempt_before_upload(self):
        snapshot,effect,prior=self.recovery_fixture();self.adapter.reconcile_blocked_transfer(effect,self.package)
        self.assertEqual(self.adapter.recovery_attempts,1);self.adapter.checkpoint.assert_called_once()

    def test_arbitrary_cloud_bucket_cannot_be_authorized(self):
        with self.assertRaises(Denied):self.adapter.authorize({**self.scope,'upload_receivers':['https://other.s3.amazonaws.com/']})

    def test_loading_products_page_is_not_missing_account_or_product(self):
        from unittest.mock import patch
        old={'label':'Original calculator','href':'https://payhip.com/b/old'}
        self.adapter.scope.update(baseline={'calculator_controls':[old]},title='Inventory Reorder Planner - Private Integration Test')
        self.adapter.products_tab=1
        snapshot={'controls':[{**old,'nearby':'Original calculator HIDDEN CAD29.00'},
            {'label':'Inventory Reorder Planner - Private Integration ...','href':'https://payhip.com/b/new','nearby':'HIDDEN CAD19.00'},
            {'label':'Edit','href':'https://payhip.com/product/edit/new'}]}
        self.adapter.inspect=Mock(side_effect=[{'controls':[]},snapshot])
        with patch('assistant.payhip.time.sleep'):
            found=self.adapter.lookup(None)
        self.assertEqual(found['edit_url'],'https://payhip.com/product/edit/new')
        self.assertNotIn('files_verified',found)

    def test_truncated_candidate_never_skips_full_saved_field_verification(self):
        self.adapter.open=Mock(return_value={'controls':[]})
        self.adapter.inspect=Mock(return_value={'controls':[]})
        listing={'visibility':'invisible','title':'Inventory test','edit_url':'https://payhip.com/product/edit/new'}
        from unittest.mock import patch
        with patch('assistant.payhip.time.sleep'),self.assertRaisesRegex(Denied,'Reopened Payhip'):
            self.adapter.verify(listing,self.package)


if __name__=='__main__':unittest.main()
