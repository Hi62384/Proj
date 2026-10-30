"""Small native-accessibility driver for THIS app's opt-in integration tests."""
import json
import sqlite3
import time
from pathlib import Path
from assistant.storage import private_directory


class LiveApp:
    def __init__(self):
        from pywinauto import Desktop
        self.root=private_directory();self.window=Desktop(backend='uia').window(title='Codex Desktop Assistant').wrapper_object()
    def rows(self,sql,params=()):
        db=sqlite3.connect((self.root/'assistant.sqlite3').as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
        try:return [dict(r) for r in db.execute(sql,params)]
        finally:db.close()
    def idle(self):
        if self.rows("SELECT id FROM conversations WHERE status IN ('Working','Waiting for User','Waiting for Approval','Thinking','Acting')"):raise RuntimeError('An existing turn is active; the test will not interrupt it')
    def invoke(self,name,parent=None):
        parent=parent or self.window;next(c for c in parent.descendants(control_type='Button') if c.window_text()==name).invoke()
    def wait(self,predicate,timeout=30):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            result=predicate()
            if result:return result
            time.sleep(.1)
        raise TimeoutError('Native application test setup timed out')
    def new(self):
        self.idle();before={r['id'] for r in self.rows('SELECT id FROM conversations')};self.invoke('+ New Chat')
        return self.wait(lambda:next((r['id'] for r in self.rows('SELECT id FROM conversations') if r['id'] not in before),None))
    def choose(self,conversation):
        self.idle();row=self.rows('SELECT title FROM conversations WHERE id=?',(conversation,))[0]
        matches=[item for item in self.window.descendants(control_type='ListItem') if item.window_text().removeprefix('★ ')==row['title']]
        if len(matches)!=1:raise RuntimeError('Verification conversation is not uniquely available in the visible conversation list')
        self.window.set_focus();matches[0].set_focus();matches[0].select();time.sleep(.2)
        self.wait(lambda:any(c.automation_id().endswith('.conversationTitle') and c.window_text()==row['title'] for c in self.window.descendants(control_type='Text')),5)
    def send(self,conversation,text,timeout=600):
        start=time.time();composer=next(c for c in self.window.descendants(control_type='Edit') if c.automation_id().endswith('.Composer'));composer.set_edit_text(text);self.invoke('Send')
        message=self.wait(lambda:next(iter(self.rows("SELECT * FROM messages WHERE conversation=? AND role='user' AND at>=? ORDER BY at DESC",(conversation,start))),None))
        deadline=time.monotonic()+timeout;started=False
        while time.monotonic()<deadline:
            state=self.rows('SELECT status,thread FROM conversations WHERE id=?',(conversation,))[0]
            started|=state['status'] in ('Working','Thinking','Acting','Waiting for Approval','Waiting for User')
            replies=self.rows("SELECT text FROM messages WHERE conversation=? AND role='assistant' AND at>=? ORDER BY at",(conversation,start))
            if state['status'] in ('Waiting for User','Waiting for Approval'):break
            if state['status'] in ('Error','Stopped') or (state['status']=='Completed' and (started or replies)):break
            time.sleep(.25)
        return {'conversation':conversation,'state':state['status'],'saved_thread':bool(state['thread']),'report':'\n'.join(r['text'] for r in replies),'actions':self.rows('SELECT operation,state FROM actions WHERE conversation=? AND at>=?',(conversation,start))}
