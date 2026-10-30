"""Disposable authenticated local commerce adapter and real HTML storefront.

This is a synthetic acceptance platform, never a Payhip adapter or live business.
Only the host can register adapters; model-supplied URLs cannot become adapters.
"""
import base64
import hashlib
import hmac
import html
import json
import secrets
import sqlite3
import threading
import zipfile
import io
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request,urlopen


class TestStorefront:
    __test__=False
    def __init__(self,directory,port=0):
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True)
        self.key=secrets.token_urlsafe(32);self.lock=threading.RLock()
        self.db=sqlite3.connect(self.directory/'listings.sqlite3',check_same_thread=False)
        self.db.execute('CREATE TABLE IF NOT EXISTS listings(key TEXT PRIMARY KEY,body TEXT NOT NULL,archive BLOB NOT NULL)');self.db.commit()
        owner=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def send(self,status,data,kind='application/json'):
                raw=data if isinstance(data,bytes) else data.encode();self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
            def authorized(self):return hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+owner.key)
            def do_GET(self):
                if self.path.startswith('/api/listings/'):
                    if not self.authorized():return self.send(403,'{}')
                    key=self.path.rsplit('/',1)[-1]
                    with owner.lock:row=owner.db.execute('SELECT body FROM listings WHERE key=?',(key,)).fetchone()
                    return self.send(200,json.dumps(json.loads(row[0]) if row else None))
                if self.path=='/':
                    with owner.lock:rows=list(owner.db.execute('SELECT key,body FROM listings'))
                    body='<title>Disposable business test store</title><h1>Local synthetic store</h1><p>Not a real marketplace. No purchases or account details.</p>'
                    for key,raw in rows:
                        listing=json.loads(raw);body+=f'<article><h2><a href="/products/{key}">{html.escape(listing["title"])}</a></h2><p>{html.escape(listing["description"])}</p><p>{listing["price_cents"]/100:.2f} {html.escape(listing["currency"])}</p></article>'
                    return self.send(200,body,'text/html; charset=utf-8')
                parts=self.path.split('/')
                if len(parts)==4 and parts[1]=='images' and parts[3].endswith('.png'):
                    with owner.lock:row=owner.db.execute('SELECT archive FROM listings WHERE key=?',(parts[2],)).fetchone()
                    if not row:return self.send(404,'Missing')
                    with zipfile.ZipFile(io.BytesIO(row[0])) as archive:
                        if parts[3] not in archive.namelist():return self.send(404,'Missing')
                        return self.send(200,archive.read(parts[3]),'image/png')
                if len(parts)==3 and parts[1] in ('products','download'):
                    key=parts[2]
                    with owner.lock:row=owner.db.execute('SELECT body,archive FROM listings WHERE key=?',(key,)).fetchone()
                    if not row:return self.send(404,'Missing')
                    if parts[1]=='download':return self.send(200,row[1],'application/zip')
                    listing=json.loads(row[0]);body=f'<title>{html.escape(listing["title"])}</title><h1>{html.escape(listing["title"])}</h1><p>{html.escape(listing["description"])}</p><p id="price">{listing["price_cents"]/100:.2f} {html.escape(listing["currency"])}</p><p id="visibility">Published</p><a href="/download/{key}">Download synthetic delivery</a>'
                    for name in listing['images']:body+=f'<img src="/images/{key}/{html.escape(name)}" alt="{html.escape(name)}" style="max-width:600px">'
                    return self.send(200,body,'text/html; charset=utf-8')
                self.send(404,'Missing')
            def do_POST(self):
                if self.path!='/api/listings' or not self.authorized():return self.send(403,'{}')
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<40*1024*1024:return self.send(413,'{}')
                try:
                    data=json.loads(self.rfile.read(size));key=data['key'];package=data['package'];raw=base64.b64decode(data['archive'],validate=True)
                    if len(key)!=64 or any(c not in '0123456789abcdef' for c in key):raise ValueError('Invalid idempotency key')
                    if hashlib.sha256(raw).hexdigest()!=package['sha256']:raise ValueError('File hash differs')
                    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                        if set(archive.namelist())!=set(package['files']) or archive.testzip():raise ValueError('Delivery file inventory differs')
                        for name,meta in package['files'].items():
                            contents=archive.read(name)
                            if len(contents)!=meta['bytes'] or hashlib.sha256(contents).hexdigest()!=meta['sha256']:raise ValueError('Customer file bytes differ')
                    listing={**package['listing'],'key':key,'product':package['product'],'sha256':package['sha256'],'files':package['files'],'images':[name for name in package['files'] if name.endswith('.png')],'visibility':'published','url':owner.url+'/products/'+key,'download_url':owner.url+'/download/'+key}
                    with owner.lock:
                        previous=owner.db.execute('SELECT body FROM listings WHERE key=?',(key,)).fetchone()
                        if previous and json.loads(previous[0])!=listing:return self.send(409,'{"error":"Conflicting duplicate"}')
                        owner.db.execute('INSERT OR IGNORE INTO listings VALUES(?,?,?)',(key,json.dumps(listing),raw));owner.db.commit()
                    self.send(200,json.dumps(listing))
                except Exception:self.send(400,'{"error":"Invalid synthetic listing"}')
        self.server=ThreadingHTTPServer(('127.0.0.1',port),Handler);self.url='http://127.0.0.1:'+str(self.server.server_port)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True,name='synthetic-store');self.thread.start()
    def count(self):
        with self.lock:return self.db.execute('SELECT COUNT(*) FROM listings').fetchone()[0]
    def close(self):self.server.shutdown();self.server.server_close();self.thread.join(timeout=5);self.db.close()


class LocalStoreAdapter:
    def __init__(self,store):self.store=store
    def request(self,path,data=None):
        request=Request(self.store.url+path,data=json.dumps(data).encode() if data is not None else None,headers={'Authorization':'Bearer '+self.store.key,'Content-Type':'application/json'})
        with urlopen(request,timeout=15) as response:return json.loads(response.read(40*1024*1024))
    def lookup(self,key):return self.request('/api/listings/'+key)
    def publish(self,key,package,archive):return self.request('/api/listings',{'key':key,'package':package,'archive':base64.b64encode(archive.read_bytes()).decode()})
    def verify(self,listing,package):
        if not listing:raise ValueError('Listing does not exist')
        for key in ('title','description','price_cents','currency'):
            if listing.get(key)!=package['listing'][key]:raise ValueError('Published '+key+' differs')
        if listing.get('visibility')!='published' or listing.get('sha256')!=package['sha256'] or listing.get('files')!=package['files']:raise ValueError('Published visibility or delivery differs')
        if 'Cover.png' not in listing.get('images',[]) or not any(name.startswith('Preview-') for name in listing.get('images',[])):raise ValueError('Missing listing cover/preview image')
        for name in listing['images']:
            with urlopen(self.store.url+'/images/'+listing['key']+'/'+name,timeout=10) as response:raw=response.read(8*1024*1024)
            if hashlib.sha256(raw).hexdigest()!=package['files'][name]['sha256']:raise ValueError('Listing image bytes differ')
        with urlopen(listing['url'],timeout=10) as response:
            if response.status!=200:raise ValueError('Published URL unavailable')
        with urlopen(listing['download_url'],timeout=10) as response:raw=response.read(26*1024*1024)
        if hashlib.sha256(raw).hexdigest()!=package['sha256']:raise ValueError('Downloaded delivery bytes differ')
        return True
