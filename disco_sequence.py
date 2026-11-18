"""Destination-bound Disco commands; never substitute a cached path for the recipient."""
import argparse
import json
import time
from urllib.error import HTTPError
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(r'C:\Users\User1\Documents\Downloads\Disco\disco_desktop')

def request(route, data=None):
    config = json.loads((ROOT / '.disco-connection.json').read_text(encoding='utf-8'))
    headers = {'X-Disco-Token': config['token'], 'Origin': config['origin'], 'Content-Type': 'application/json'}
    body = None if data is None else json.dumps(data).encode()
    with urlopen(Request(config['origin'] + '/api/' + route, data=body, headers=headers), timeout=55) as response:
        return json.load(response)

def navigate(target):
    state = request('state')
    tab = state['selected']
    if state['chat']['path'] != target:
        request('action', dict(action='navigate', tab=tab, path=state['chat']['path'], target=target))
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        state = request('state')
        if state['selected'] != tab:
            raise RuntimeError('Selected tab changed; no message sent')
        chat = state.get('chat') or {}
        if chat.get('path') == target and chat.get('canSend'):
            return tab
        time.sleep(.3)
    raise RuntimeError('Destination did not become ready; no message sent')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--send-test', action='store_true')
    parser.add_argument('--oi', action='store_true')
    args = parser.parse_args()
    paths = ['1566940304127557643','911006206460575804','1568058180561403908','1274989128622280757','1567426744065986642']
    for identity in paths:
        target = '/channels/@me/' + identity
        tab = navigate(target)
        print(json.dumps({'navigation': 'verified', 'target': target}), flush=True)
        if args.oi:
            before = request('state')['chat']
            if before['path'] != target:
                raise RuntimeError('Destination changed before send')
            started = int(time.time()*1000)
            link = 'https://klipy.com/gifs/billy-bucher-oi'
            try:
                result = request('action', dict(action='send', tab=tab, path=target, text=link, files=[]))
            except HTTPError as error:
                if error.code != 409 or json.load(error).get('delivery') != 'unknown':
                    raise
                import sys
                sys.path.insert(0, str(ROOT))
                from bridge import confirmed
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    mid = confirmed(before, request('state')['chat'], link, [], started)
                    if mid:
                        result = dict(status='sent', messageId=mid)
                        break
                    time.sleep(.4)
                else:
                    raise RuntimeError('Could not verify GIF delivery in '+target)
            print(json.dumps({'target': target, 'delivery': result}), flush=True)
    if args.send_test:
        target = '/channels/@me/' + paths[0]
        tab = navigate(target)
        print(json.dumps(request('action', dict(action='send', tab=tab, path=target, text='Disco bridge test', files=[]))), flush=True)

if __name__ == '__main__':
    main()
