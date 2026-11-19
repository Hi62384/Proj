import hashlib,json,unittest
from pathlib import Path
from report_contract import validate,FIELDS
class ContractTests(unittest.TestCase):
 def setUp(self):
  self.fixture=b'synthetic';self.hash=hashlib.sha256(self.fixture).hexdigest()
  self.result={k:(False if t is bool else 0 if t is int else '') for k,t in FIELDS.items()};self.result['status']='pass'
 def raw(self):return json.dumps(self.result).encode()
 def check(self,raw=None,code=0,trusted=True):return validate(self.raw() if raw is None else raw,code,self.fixture,self.hash,'fixture',trusted_worker=trusted)
 def test_valid_but_untrusted_never_becomes_pass(self):
  self.assertEqual(self.check(trusted=False)['status'],'untrusted_worker');self.assertEqual(self.check()['status'],'pass')
 def test_trusted_report_is_not_proof_of_restore(self):
  # Structurally valid invented data is indistinguishable from honest data.
  self.assertEqual(self.check()['status'],'pass');self.assertEqual(self.check(trusted=False)['status'],'untrusted_worker')
 def test_detects_tampering_and_inconsistent_exit(self):
  with self.assertRaises(ValueError):self.check(code=1)
  with self.assertRaises(ValueError):validate(self.raw(),0,b'changed',self.hash,'fixture',trusted_worker=True)
  with self.assertRaises(ValueError):self.check(raw=b'{"status":"pass","status":"pass"}')
  self.result['unexpected']='secret'
  with self.assertRaises(ValueError):self.check()
 def test_actual_forged_report_is_never_authenticated_by_structure(self):
  experiments=Path(__file__).resolve().parent.parent
  forged=json.loads((experiments/'standalone-probe-build-v13'/'forgery-observation.json').read_text(encoding='utf-8'))
  fixture=(experiments.parent/'SampleProject'/'Assets'/'Tests'/'Fixtures'/'v1.json').read_bytes()
  digest='462a55994a843bf1eaa4bf350a533d2a498edf01b5726f5820e4b2e68dcd22bc'
  raw=json.dumps(forged['payload']).encode()
  self.assertEqual(validate(raw,forged['exit_code'],fixture,digest,'v1.json')['status'],'untrusted_worker')
  self.assertEqual(validate(raw,forged['exit_code'],fixture,digest,'v1.json',trusted_worker=True)['status'],'pass')
 def test_trust_and_exit_must_have_exact_types(self):
  with self.assertRaises(ValueError):self.check(trusted='yes')
  with self.assertRaises(ValueError):self.check(code=False)
 def test_regression_path_and_redaction(self):
  self.result['status']='regression';self.result['path']='quests.complete';self.result['outsideWriteError']='sensitive diagnostic'
  self.assertEqual(self.check(code=1),{'fixture_id':'fixture','status':'regression','path':'quests.complete'})
  self.result['path']='unrecognized'
  with self.assertRaises(ValueError):self.check(code=1)
if __name__=='__main__':unittest.main(verbosity=2)
