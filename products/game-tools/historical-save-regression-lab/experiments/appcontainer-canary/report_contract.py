"""Synthetic player report validation; this does not authenticate worker honesty."""
import hashlib,json

FIELDS={'status':str,'path':str,'outsideWriteBlocked':bool,'outsideWriteError':str,'loopbackConnected':bool,'loopbackResult':str,'childStarted':bool,'childExit':int,'childError':str,'childJobKnown':bool,'childInJob':bool,'childTokenKnown':bool,'childAppContainer':bool,'inheritedHandleMatched':bool,'inheritedHandleWrite':bool,'inheritedHandleError':int}
ALLOWED_PATHS={'inventory.shield','quests.complete','inventory.potions'}
def no_duplicates(pairs):
 result={}
 for key,value in pairs:
  if key in result:raise ValueError('duplicate field')
  result[key]=value
 return result
def validate(raw,exit_code,fixture_bytes,expected_hash,fixture_id,*,trusted_worker=False):
 """Return redacted status. `trusted_worker` is an explicit trust assertion, not proof.

 A worker can fabricate any syntactically valid state. Refuse to label its
 self-reported success as verified when the caller has not accepted that trust.
 """
 if type(trusted_worker) is not bool or type(exit_code) is not int:raise ValueError('invalid trust or exit code')
 if not isinstance(raw,bytes) or len(raw)>65536:raise ValueError('invalid report size')
 if not isinstance(fixture_bytes,bytes) or not isinstance(expected_hash,str) or len(expected_hash)!=64:raise ValueError('invalid fixture identity')
 if hashlib.sha256(fixture_bytes).hexdigest()!=expected_hash.lower():raise ValueError('fixture hash mismatch')
 if not isinstance(fixture_id,str) or not fixture_id or len(fixture_id)>128:raise ValueError('invalid fixture id')
 report=json.loads(raw.decode('utf-8-sig'),object_pairs_hook=no_duplicates,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite')))
 if not isinstance(report,dict) or set(report)!=set(FIELDS):raise ValueError('invalid report fields')
 if any(type(report[k]) is not typ for k,typ in FIELDS.items()):raise ValueError('invalid report types')
 status,path=report['status'],report['path']
 if status=='pass':
  if path!='' or exit_code!=0:raise ValueError('inconsistent pass')
 elif status=='regression':
  if path not in ALLOWED_PATHS or exit_code!=1:raise ValueError('inconsistent regression')
 else:raise ValueError('unknown status')
 if not trusted_worker:return {'fixture_id':fixture_id,'status':'untrusted_worker','path':''}
 return {'fixture_id':fixture_id,'status':status,'path':path}
