"""Website grants and network classification do not trust model permission hints."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from assistant.permissions import Permissions,Denied,origin
from assistant.web_policy import WebsiteAccess,network_intent,public_url,safe_text
from assistant.action_policy import classify


class WebsiteTests(unittest.TestCase):
    def setUp(self):
        self.p=Permissions();self.p.resume('test');self.ask=Mock(return_value=True)
        self.access=WebsiteAccess(self.p,self.ask,resolver=lambda url:True)

    def test_once_visit_and_independent_tabs(self):
        self.access.authorize('https://one.example/a',0,'Research')
        self.access.authorize('https://one.example/b',0,'Research')
        self.ask.assert_called_once();self.assertFalse(self.access.full('https://one.example',1))
        self.access.leave(0);self.assertFalse(self.access.full('https://one.example',0))

    def test_session_origin_is_exact(self):
        self.p.origins.add(origin('https://one.example'))
        self.access.authorize('https://one.example/a',5,'Read');self.ask.assert_not_called()
        self.assertFalse(self.access.full('https://sub.one.example',5))

    def test_deny_is_not_repeated(self):
        self.ask.return_value=False
        for _ in range(3):
            with self.assertRaises(Denied):self.access.authorize('https://one.example',0,'Read')
        self.ask.assert_called_once()

    def test_stop_clears_visit_and_resource_grants(self):
        self.access.authorize('https://one.example',0,'Read');self.access.rendering('https://cdn.example',0)
        self.p.revoke();self.p.resume('test')
        self.assertFalse(self.access.full('https://one.example',0));self.assertEqual(self.access.resources,{})

    def test_stop_during_approval_cannot_grant(self):
        self.ask.side_effect=lambda *args:(self.p.halt() or True)
        with self.assertRaises(Denied):self.access.authorize('https://one.example',0,'Read')
        self.assertFalse(self.access.full('https://one.example',0))

    def test_public_mode_requires_separate_account_authority(self):
        self.p.public_browsing=True
        self.access.authorize('https://one.example/news',0,'Read');self.ask.assert_not_called()
        self.assertFalse(self.access.full('https://one.example/news',0))
        self.access.authorize('https://one.example/dashboard',0,'Account work');self.ask.assert_called_once()

    def test_rendering_grants_do_not_grant_site_or_data_access(self):
        self.assertTrue(self.access.rendering('https://cdn.example/a.js',0))
        self.assertFalse(self.access.available('https://cdn.example',0));self.assertFalse(self.access.data_pairs)

    def test_private_network_is_not_public(self):
        for url in ('http://localhost','http://127.0.0.1','http://10.0.0.2','http://[::1]','file:///c:/secret','https://user:pass@example.org'):
            self.assertFalse(public_url(url),url)
        self.assertTrue(public_url('https://8.8.8.8'))

    def test_network_intents(self):
        cases=[('POST','/api',{'operationName':'SearchProducts','variables':{'query':'leaf'}},'read'),
               ('POST','/graphql',{'query':'query Products { name }'},'read'),
               ('POST','/graphql',{'query':'mutation Update { name }'},'unknown'),
               ('POST','/api',{'operationName':'PublishProduct'},'consequential'),
               ('DELETE','/item/1',{},'consequential'),
               ('POST','/drafts/1',{'title':'draft'},'draft'),
               ('POST','/api',{'variables':{'password':'synthetic'}},'credentials'),
               ('POST','/api',{'grant_type':'refresh_token','refresh_token':'synthetic'},'refresh'),
               ('POST','/api',{'type':'connection_init'},'read'),
               ('POST','/graphql',{'type':'subscribe','payload':{'query':'subscription Events { event }'}},'read'),
               ('POST','/api',{'variables':{'delete':'item'}},'unknown'),
               ('POST','/api',{'type':'authenticate','payload':'opaque'},'unknown'),
               ('POST','/api',{'unexpected':'data'},'unknown')]
        for method,path,payload,kind in cases:
            with self.subTest(payload=payload):self.assertEqual(network_intent(method,'https://one.example'+path,json.dumps(payload),'application/json').kind,kind)

    def test_secrets_are_redacted_in_errors_and_page_text(self):
        for value,secret in [('Authorization: Bearer ABCDEFGHIJ','ABCDEFGHIJ'),('"password":"hidden-value"','hidden-value'),('https://example.org/callback?code=private#token','private'),('verification code: 123456','123456')]:
            self.assertNotIn(secret,safe_text(value))

    def test_browser_navigation_controls_are_routine(self):
        for op in ('tabs','close_tab','back','forward','reload','wait'):
            self.assertFalse(classify(op,{'source':'browser'}).required)


if __name__=='__main__':unittest.main()
