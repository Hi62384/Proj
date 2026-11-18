import json
from urllib.error import HTTPError
from disco_sequence import navigate, request

for identity in ['911006206460575804','1568058180561403908','1274989128622280757','1567426744065986642']:
    target='/channels/@me/'+identity
    tab=navigate(target)
    before=request('state')['chat']
    ids={m['id'] for m in before['messages']}
    try:
        result=request('action',dict(action='send',tab=tab,path=target,text='https://klipy.com/gifs/billy-bucher-oi',files=[]))
    except HTTPError as exc:
        result=json.load(exc)
    after=request('state')['chat']
    matches=[m['messageId'] for m in after['messages'] if after['path']==target and m['id'] not in ids and m['authorId']==before['self'] and not m['pending'] and (m['text']=='https://klipy.com/gifs/billy-bucher-oi' or any('30ML6JApHJrM5In3.mp4' in a['url'] for a in m['assets']))]
    print(json.dumps(dict(target=target,result=result,verified=matches)),flush=True)
