"""Real current-user Windows named pipe and native host subprocess, no Chrome claim."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from assistant.chrome_bridge import ChromeBridge,private_json
from assistant.chrome_protocol import read_message,write_message


@unittest.skipUnless(os.name=='nt','Windows native pipe required')
class NativeTransportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.bridge=ChromeBridge(self.root);self.bridge.start();self.addCleanup(self.bridge.close)

    def wait(self,predicate):
        deadline=time.monotonic()+5
        while time.monotonic()<deadline:
            if predicate():return
            time.sleep(.01)
        self.fail('Native transport did not reach the expected state')

    def test_real_host_handshake_grant_and_roundtrip(self):
        identity='a'*32;settings=self.root/'chrome-host';settings.mkdir();private_json(settings/'settings.json',{'extension_id':identity})
        app=Path(__file__).resolve().parents[1]
        # Only this subprocess redirects the host's state dependency to our
        # disposable directory. Production has no message-selected state path.
        code='import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);import chrome_native_host as h;root=Path(sys.argv[2]);sys.argv=[str(Path(sys.argv[1])/"chrome_native_host.py"),sys.argv[3]];h.private_directory=lambda:root;raise SystemExit(h.main())'
        process=subprocess.Popen([sys.executable,'-I','-u','-c',code,str(app),str(self.root),'chrome-extension://'+identity+'/'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            write_message(process.stdin,{'type':'hello','version':1});hello=read_message(process.stdout)
            self.assertEqual(hello['type'],'hello');session=hello['session'];self.wait(lambda:self.bridge.status()['connected'])
            write_message(process.stdin,{'type':'event','session':session,'event':'grant','tab':{'tab':42,'window':3,'origin':'http://127.0.0.1:22704','manual':False,'frames':{'0':'http://127.0.0.1:22704'}}})
            self.wait(lambda:len(self.bridge.status()['tabs'])==1)
            acknowledgment=read_message(process.stdout);self.assertEqual(acknowledgment['type'],'grant_ack');self.assertEqual(acknowledgment['tab'],42)
            import threading
            results=[]
            thread=threading.Thread(target=lambda:results.append(self.bridge.request('list_tabs',{},timeout=3)));thread.start()
            request=read_message(process.stdout);self.assertEqual(request['operation'],'list_tabs')
            write_message(process.stdin,{'type':'response','session':session,'id':request['id'],'ok':True,'result':{'tabs':[{'tab':42}]}})
            thread.join(4);self.assertEqual(results,[{'tabs':[{'tab':42}]}]);self.assertEqual(process.poll(),None)
        finally:
            process.terminate();process.wait(timeout=5)
            for stream in (process.stdin,process.stdout,process.stderr):stream.close()
        self.wait(lambda:not self.bridge.status()['connected']);self.assertEqual(self.bridge.status()['tabs'],[])

    def test_rendezvous_acl_has_only_owner_and_system(self):
        import win32security
        sd=win32security.GetNamedSecurityInfo(str(self.root/'chrome-bridge.json'),win32security.SE_FILE_OBJECT,win32security.DACL_SECURITY_INFORMATION)
        self.assertEqual(sd.GetSecurityDescriptorDacl().GetAceCount(),2)
        self.assertTrue(sd.GetSecurityDescriptorControl()[0]&win32security.SE_DACL_PROTECTED)


if __name__=='__main__':unittest.main()
