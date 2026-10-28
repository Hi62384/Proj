"""Durable local messages and checkpoints; never automatically replay interrupted work."""
import json
import os
import sqlite3
import threading
import time
import uuid
from pathlib import Path


def private_directory():
    return Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexDesktopAssistant'


class Store:
    def __init__(self, directory=None):
        self.directory = Path(directory or private_directory())
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(self.directory / 'assistant.sqlite3', check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        # One consistent pre-upgrade backup; includes WAL through SQLite backup.
        if self.db.execute("SELECT name FROM sqlite_master WHERE name='settings'").fetchone() and not self.db.execute("SELECT value FROM settings WHERE key='overhaul_backup'").fetchone():
            backups=self.directory/'state-backups';backups.mkdir(exist_ok=True)
            target=backups/('before-overhaul-'+time.strftime('%Y%m%d-%H%M%S')+'.sqlite3')
            backup=sqlite3.connect(target)
            try:self.db.backup(backup)
            finally:backup.close()
            self.db.execute("INSERT INTO settings(key,value) VALUES('overhaul_backup',?)",(json.dumps(str(target)),));self.db.commit()
        self.db.executescript('''PRAGMA journal_mode=WAL;
        PRAGMA foreign_keys=ON;
        CREATE TABLE IF NOT EXISTS conversations(id TEXT PRIMARY KEY,title TEXT,thread TEXT,status TEXT,pinned INTEGER DEFAULT 0,archived INTEGER DEFAULT 0,updated REAL);
        CREATE TABLE IF NOT EXISTS messages(id TEXT PRIMARY KEY,conversation TEXT REFERENCES conversations(id) ON DELETE CASCADE,role TEXT,text TEXT,state TEXT,attachments TEXT,at REAL);
        CREATE TABLE IF NOT EXISTS actions(id TEXT PRIMARY KEY,conversation TEXT,operation TEXT,state TEXT,at REAL);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
        ''')
        self.db.execute("UPDATE conversations SET status='Review after interruption' WHERE status IN ('Thinking','Acting','Waiting for approval')")
        self.db.execute("UPDATE messages SET state='Review after interruption' WHERE state IN ('queued','sending','streaming')")
        self.db.commit()

    def execute(self, sql, args=(), one=False):
        with self.lock:
            cursor = self.db.execute(sql, args)
            rows = [dict(row) for row in cursor.fetchall()] if cursor.description else []
            self.db.commit()
            return (rows[0] if rows else None) if one else rows

    def new(self, title='New conversation'):
        ident = uuid.uuid4().hex
        self.execute('INSERT INTO conversations(id,title,status,updated) VALUES(?,?,?,?)', (ident,title,'Ready',time.time()))
        return ident

    def conversation(self, ident):
        return self.execute('SELECT * FROM conversations WHERE id=?', (ident,), True)

    def conversations(self, query='', archived=False):
        return self.execute('SELECT * FROM conversations WHERE archived=? AND title LIKE ? ORDER BY pinned DESC,updated DESC', (int(archived),'%'+query+'%'))

    def update(self, ident, **fields):
        if not fields or not set(fields) <= {'title','thread','status','pinned','archived'}:
            raise ValueError('Invalid conversation update')
        fields['updated'] = time.time()
        self.execute('UPDATE conversations SET '+','.join(key+'=?' for key in fields)+' WHERE id=?', (*fields.values(), ident))

    def add(self, conversation, role, text, state='saved', attachments=None):
        ident = uuid.uuid4().hex
        self.execute('INSERT INTO messages VALUES(?,?,?,?,?,?,?)', (ident,conversation,role,text,state,json.dumps(attachments or []),time.time()))
        return ident

    def message(self, ident, **fields):
        if not fields or not set(fields) <= {'text','state','attachments'}:
            raise ValueError('Invalid message update')
        self.execute('UPDATE messages SET '+','.join(key+'=?' for key in fields)+' WHERE id=?', (*fields.values(),ident))

    def messages(self, conversation):
        return self.execute('SELECT * FROM messages WHERE conversation=? ORDER BY at,rowid', (conversation,))

    def action(self, conversation, operation, state):
        # Text typed, captured images and tool-returned private content never enter action logs.
        self.execute('INSERT INTO actions VALUES(?,?,?,?,?)', (uuid.uuid4().hex,conversation,operation,state,time.time()))

    def settings(self):
        return {row['key']:json.loads(row['value']) for row in self.execute('SELECT * FROM settings')}

    def setting(self, key, value):
        self.execute('INSERT OR REPLACE INTO settings VALUES(?,?)', (key,json.dumps(value)))

    def selection(self,model,effort):
        with self.lock:
            self.db.executemany('INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)',[(key,json.dumps(value)) for key,value in [('model',model),('effort',effort)]])
            self.db.commit()

    def close(self):
        with self.lock:
            self.db.close()

    def delete(self,conversation):
        with self.lock:
            self.db.execute('DELETE FROM actions WHERE conversation=?',(conversation,))
            self.db.execute('DELETE FROM conversations WHERE id=?',(conversation,))
            self.db.commit()

    def prune(self,days):
        if not days:return []
        if days not in (7,30,90,365):raise ValueError('Unsupported history retention')
        cutoff=time.time()-days*86400
        old=self.execute('SELECT id FROM conversations WHERE updated<?',(cutoff,))
        attachments=[]
        for conversation in old:
            for message in self.messages(conversation['id']):attachments.extend(json.loads(message['attachments']))
            self.delete(conversation['id'])
        return attachments
