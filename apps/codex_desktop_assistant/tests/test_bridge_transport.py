"""Real isolated Windows IPC tests. No actual computer actions or Codex-client claim."""
import concurrent.futures
import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[3])]
from bridge.runtime import Runtime
from bridge.client import ControllerClient


@unittest.skipUnless(os.name=='nt','Windows named pipe required')
class BridgeTransportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.runtime=Runtime.__new__(Runtime);self.runtime.store=SimpleNamespace(directory=self.root);self.runtime.closed=threading.Event();self.runtime.clients={};self.runtime.inflight={};self.runtime.status=lambda:{'controller_ready':True,'independent_ai_engine':False};self.runtime.start_pipe()
    def tearDown(self):
        self.runtime.closed.set();self.runtime.listener.close();self.tmp.cleanup()

    def test_real_json_pipe_roundtrip_and_repeated_clients(self):
        for _ in range(4):
            client=ControllerClient(self.root);self.assertTrue(client.request('bridge_status')['controller_ready']);client.close()

    def test_readonly_diagnostics_do_not_claim_an_initialized_mcp_client(self):
        client=ControllerClient(self.root);client.request('bridge_health');self.assertEqual(self.runtime.clients,{})
        client.request('bridge_mcp_connected');self.assertIn(client.identity,self.runtime.clients)
        client.close();self.assertNotIn(client.identity,self.runtime.clients)

    def test_unapproved_client_key_cannot_connect(self):
        from multiprocessing.connection import Client,AuthenticationError
        info=json.loads((self.root/'computer-bridge.json').read_text())
        with self.assertRaises(AuthenticationError):Client(info['address'],family='AF_PIPE',authkey=b'wrong-key')
        import time
        time.sleep(.15)
        self.assertTrue(ControllerClient(self.root).request('bridge_health')['controller_ready'])

    def test_rendezvous_acl_is_private(self):
        import win32security,win32api,win32con
        sd=win32security.GetNamedSecurityInfo(str(self.root/'computer-bridge.json'),win32security.SE_FILE_OBJECT,win32security.DACL_SECURITY_INFORMATION);acl=sd.GetSecurityDescriptorDacl()
        token=win32security.OpenProcessToken(win32api.GetCurrentProcess(),win32con.TOKEN_QUERY)
        try:owner=win32security.GetTokenInformation(token,win32security.TokenUser)[0]
        finally:token.Close()
        allowed={win32security.ConvertSidToStringSid(owner),'S-1-5-18'}
        self.assertEqual({win32security.ConvertSidToStringSid(acl.GetAce(i)[2]) for i in range(acl.GetAceCount())},allowed)


if __name__=='__main__':unittest.main()
