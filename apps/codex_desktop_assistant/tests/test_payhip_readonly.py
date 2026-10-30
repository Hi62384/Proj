"""Read-only reconciliation never renews account-write authority."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bridge.payhip_verification import verify_saved
from assistant.permissions import Denied


class SavedReadOnlyTests(unittest.TestCase):
    def runtime(self):
        r=Mock();r.owner='owner';r.permissions.generation=1
        q=r.broker.projects.queue
        q.result.return_value={'result':{'sha256':'a'*64}}
        q.rows.return_value=[{'manifest':json.dumps({'sha256':'a'*64,'visibility':'invisible','title':'Test','price_cents':1900,'currency':'CAD'})}]
        r.approve.return_value=True
        chrome=r.broker.chrome
        chrome.call.return_value={'observation':'fresh','controls':[{'name':'p_name','value':'Test'},{'name':'p_price','value':'19.00'},{'name':'product_status','value':'invisible','checked':True},{'element':3,'href':'https://payhip.com/product/download/Observed'}]}
        def request(owner,operation,args,*rest,**kw):
            if operation=='find_tabs':return {'tabs':[{'tab':1,'url':args['query']}]}
            if operation=='adopt_tab':return {}
            if operation=='asset_digest':return {'bytes':273,'sha256':'b'*64}
            raise AssertionError('Not read-only: '+operation)
        chrome.request.side_effect=request
        return r

    def test_new_read_permission_does_not_renew_old_write_scope(self):
        r=self.runtime()
        with self.assertRaisesRegex(Denied,'did not match approved ZIP'):verify_saved(r)
        r.broker.projects.queue.approve_scope.assert_not_called()
        r.broker.projects.queue.db.execute.assert_not_called()
        self.assertEqual({call.args[1] for call in r.broker.chrome.call.call_args_list},{'inspect'})

    def test_denied_read_approval_prevents_download_and_tab_attachment(self):
        r=self.runtime();r.approve.return_value=False
        with self.assertRaisesRegex(Denied,'not approved'):verify_saved(r)
        r.broker.chrome.request.assert_not_called()

    def test_missing_existing_tab_never_creates_one(self):
        r=self.runtime();r.broker.chrome.request.side_effect=None;r.broker.chrome.request.return_value={'tabs':[]}
        with self.assertRaisesRegex(Denied,'no new tab created'):verify_saved(r)
        r.broker.chrome.call.assert_not_called()


if __name__=='__main__':unittest.main()
