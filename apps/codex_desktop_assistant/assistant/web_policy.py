"""Browser site authority, bounded network intent and safe model-facing text."""
import ipaddress
import json
import re
import socket
from dataclasses import dataclass
from urllib.parse import urlsplit,parse_qs
from .permissions import Denied,origin
from .action_policy import request_review,commit_label

PRIVATE_PATH=re.compile(r'/(?:account|dashboard|admin|manage|billing|settings|editor)(?:/|$)',re.I)
SECRET_KEY=re.compile(r'password|passwd|secret|access.?token|refresh.?token|id.?token|authorization|api.?key|one.?time|captcha|card.?number|cvv|cvc',re.I)


def public_url(url,resolver=socket.getaddrinfo):
    p=urlsplit(url)
    if p.scheme not in ('http','https') or not p.hostname or p.username or p.password:return False
    host=p.hostname.rstrip('.').lower()
    if host in ('localhost','localhost.localdomain') or host.endswith(('.local','.localhost','.internal')):return False
    try:addresses=[ipaddress.ip_address(host)]
    except ValueError:
        try:addresses=[ipaddress.ip_address(x[4][0]) for x in resolver(host,p.port or (443 if p.scheme=='https' else 80),type=socket.SOCK_STREAM)]
        except (OSError,ValueError):return False
    return bool(addresses) and all(x.is_global for x in addresses)


def safe_text(value):
    text=str(value)
    # Strip URL query/fragment secrets from errors as well as inspected URLs.
    text=re.sub(r'https?://[^\s<>"\']+',lambda m:m.group(0).split('?',1)[0].split('#',1)[0],text)
    text=re.sub(r'(?i)\b(?:sk-|gh[pousr]_|github_pat_)[a-z0-9_-]{12,}', '[private token]',text)
    text=re.sub(r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+','[private token]',text)
    text=re.sub(r'(?i)\bBearer\s+[a-z0-9_.~+/-]+=*','Bearer [private]',text)
    text=re.sub(r'(?i)((?:access[_ -]?token|refresh[_ -]?token|id[_ -]?token|api[_ -]?key|authorization|password|cookie)["\']?\s*[=:]\s*["\']?)[^\s,;<>"\']{4,}',r'\1[private]',text)
    text=re.sub(r'(?i)((?:verification|security|one.time) code\s*:?\s*)\d{4,8}',r'\1[private]',text)
    return text


@dataclass(frozen=True)
class Intent:
    kind:str
    reason:str=''


def network_intent(method,url,body=None,content_type=''):
    decision=request_review(method,url)
    if decision.required:return Intent('consequential',decision.reason)
    if method.upper() in ('GET','HEAD','OPTIONS'):return Intent('read')
    value={}
    if body:
        if isinstance(body,bytes):
            try:body=body.decode('utf-8')
            except UnicodeError:return Intent('unknown','The request carries binary data whose purpose cannot be verified.')
        if len(body)>120000:return Intent('unknown','The request body is too large to classify safely.')
        try:value=json.loads(body) if 'json' in content_type or body.lstrip().startswith(('{','[')) else {k:v[0] for k,v in parse_qs(body).items()}
        except (ValueError,TypeError):return Intent('unknown','The request format cannot be classified safely.')
    if not isinstance(value,dict):return Intent('unknown','The request contains a batch or opaque operation.')
    def field_keys(item):
        if isinstance(item,dict):return [str(k) for k in item]+[k for child in item.values() for k in field_keys(child)]
        if isinstance(item,list):return [k for child in item for k in field_keys(child)]
        return []
    keys=[str(k) for k in value]
    # Browser-managed token refresh is session maintenance, not permission to
    # enter credentials or change account security. It stays on approved sites.
    if value.get('grant_type')=='refresh_token':return Intent('refresh')
    if any(SECRET_KEY.search(k) for k in field_keys(value)):return Intent('credentials','This request contains authentication or payment fields and needs a manual step.')
    operation=next((str(value[k]) for k in ('operationName','action','operation','command','intent','type') if isinstance(value.get(k),str)),'')
    words=re.sub(r'([a-z])([A-Z])',r'\1 \2',operation).replace('_',' ').replace('-',' ').strip()
    # A GraphQL websocket subscription observes events. It is distinct from
    # activating a newsletter/payment subscription control.
    payload=value.get('payload')
    if operation=='subscribe' and isinstance(payload,dict) and isinstance(payload.get('query'),str):
        query=re.sub(r'#[^\n]*','',payload['query']).lstrip()
        if query.startswith('{') or re.match(r'(?:query|subscription)\b',query):return Intent('read')
    decision=commit_label(words)
    if decision.required:return Intent('consequential',decision.reason)
    if re.search(r'(?i)\b(?:change|update|set|disable|enable)\b.*\b(?:password|security|permission|role|billing|payment|mfa)\b',words):return Intent('consequential','This operation changes account security, billing or permissions.')
    query=value.get('query')
    if isinstance(query,str):
        cleaned=re.sub(r'#[^\n]*','',query).lstrip()
        if cleaned.startswith('{') or re.match(r'query\b',cleaned):return Intent('read')
        if re.match(r'mutation\b',cleaned) and not re.search(r'(?i)\bdraft\b',words):return Intent('unknown','A GraphQL mutation needs owner review.')
    if re.fullmatch(r'(?i)(?:ping|pong|heartbeat|connection init)',words):return Intent('read')
    if re.match(r'(?i)^(?:search|query|list|get|fetch|read|load|watch)\b',words):return Intent('read')
    if re.match(r'(?i)^(?:auto ?save|save|update|edit|create)\s+(?:a\s+)?draft\b',words) or any(x in urlsplit(url).path.lower().split('/') for x in ('draft','drafts','autosave','save-draft')):
        return Intent('draft')
    if keys and set(k.lower() for k in keys)<={'q','query','search','filter','filters','page','limit','offset','sort','order','language','locale','variables','extensions','operationname'} and any(k.lower() in ('q','query','search','filter','filters','page') for k in keys):return Intent('read')
    return Intent('unknown','This background request may change data; its purpose is not established.')


class WebsiteAccess:
    def __init__(self,permissions,ask=None,resolver=public_url):
        self.permissions=permissions;self.ask=ask;self.is_public=resolver
        self.once={};self.resources={};self.denied=set();self.data_pairs=set()
        self.epoch=permissions.generation

    def sync(self):
        if self.epoch!=self.permissions.generation:
            self.once.clear();self.resources.clear();self.denied.clear();self.data_pairs.clear();self.epoch=self.permissions.generation

    def full(self,url,tab):
        self.sync()
        key=origin(url)
        return key in self.permissions.origins or key in self.once.get(tab,set())

    def available(self,url,tab,public=True):
        return self.full(url,tab) or (public and self.permissions.public_browsing and not PRIVATE_PATH.search(urlsplit(url).path) and self.is_public(url))

    def authorize(self,url,tab,reason,force=False):
        self.sync()
        key=origin(url)
        if self.full(url,tab) or (not force and self.available(url,tab)):return
        if (tab,key) in self.denied:raise Denied('Website access was denied for this visit: '+key)
        if not self.ask:raise Denied('Website origin has not been approved locally: '+key)
        details={'website_access':True,'operation':'website_access','origin':key,'reason':reason,
                 'public_address':self.is_public(url),'duration':'This visit or this app session',
                 'note':'Access may use this dedicated profile’s signed-in session. Purchases, publication, external messages and security changes remain separately reviewed.'}
        if not self.ask('Allow website '+key,details):
            self.denied.add((tab,key));raise Denied('Owner denied website access: '+key)
        if self.permissions.halted.is_set() or self.permissions.cancelled() or self.epoch!=self.permissions.generation:raise Denied('Website authorization expired before dispatch')
        # The local UI records session grants. Otherwise this is one visit.
        if key not in self.permissions.origins:self.once.setdefault(tab,set()).add(key)
        self.permissions.browser=True

    def leave(self,tab,keep_denials=False):
        self.once.pop(tab,None);self.resources.pop(tab,None)
        if not keep_denials:self.denied={x for x in self.denied if x[0]!=tab}
        self.data_pairs={x for x in self.data_pairs if x[0]!=tab}

    def rendering(self,url,tab):
        self.sync()
        key=origin(url)
        if key in self.resources.get(tab,set()):return True
        if not self.is_public(url):return False
        self.resources.setdefault(tab,set()).add(key);return True
