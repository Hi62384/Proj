"""Windows attention and foreground monitoring, independent of the inference worker."""
import ctypes
import os
import threading
import time
from ctypes import wintypes
from PySide6.QtCore import QObject,Signal
from PySide6.QtGui import QIcon,QPixmap,QColor
from PySide6.QtWidgets import QApplication,QSystemTrayIcon


class Attention(QObject):
    def __init__(self,window):
        super().__init__(window);self.window=window;self.seen=set();self.unread=0
        pixmap=QPixmap(32,32);pixmap.fill(QColor('#708294'))
        self.tray=QSystemTrayIcon(QIcon(pixmap),self)
        self.tray.setToolTip('Codex Desktop Assistant');self.tray.messageClicked.connect(self.open)
        self.tray.activated.connect(lambda reason:self.open() if reason==QSystemTrayIcon.Trigger else None)
        if QSystemTrayIcon.isSystemTrayAvailable():self.tray.show()

    def open(self):
        self.window.showNormal();self.window.raise_();self.window.activateWindow()
        self.unread=0;self.window.attention_button.setText('Requests')
        if self.window.requests:
            request=next((r for r in reversed(self.window.requests) if not r['event'].is_set()),None)
            if request:self.window.choose(request['conversation'])

    def notify(self,category,key,operation=None):
        if key in self.seen:return
        self.seen.add(key)
        if not self.window.store.settings().get('notify_'+category,category!='info'):return
        self.unread+=1;self.window.attention_button.setText(f'Requests · {self.unread}')
        # Never expose model text, filenames, website/account details or document content.
        safe_reason={'manual_step':'A manual step needs your attention. Open the assistant for the specific instructions.',
                     'manual_captcha':'A website needs you to complete a CAPTCHA. Open the assistant for instructions.',
                     'manual_mfa':'A sign-in needs your two-factor verification. Complete it privately, then choose Done in the assistant.',
                     'manual_verification':'Account verification requires your help. Open the assistant for the exact next step.',
                     'manual_signin':'A sign-in requires your help. Open the assistant for instructions; do not send passwords in chat.',
                     'read':'Permission to read a file is waiting for your decision.',
                     'write':'Permission to replace file content is waiting for your decision.',
                     'create':'Permission to create a file or folder is waiting for your decision.',
                     'delete':'Permission to delete a file or folder is waiting for your decision.',
                     'decision':'A task decision is waiting for your answer.'}.get(operation)
        text={'input':'Your input is needed. Open the assistant to review the pending request.',
              'error':'A task needs attention. Open the assistant to review it.',
              'info':'Your task has finished.'}[category]
        if category=='input' and safe_reason:text=safe_reason
        QApplication.alert(self.window,0)
        if self.tray.isVisible() and self.tray.supportsMessages():
            self.tray.showMessage('Codex Desktop Assistant',text,QSystemTrayIcon.Warning if category!='info' else QSystemTrayIcon.Information,10000)
        self.window.notice.setText(text)


class InputGuard:
    """Action-level input coordinator. Observes input; never pauses a Codex turn.

    Only shared-pointer/focus actions wait for global quiet. Background accessibility
    actions wait only for activity in their target. No keyboard content is retained.
    """
    def __init__(self,permissions,active=None,callback=None,clock=time.monotonic):
        self.permissions=permissions;self.clock=clock;self.closed=threading.Event()
        self.lock=threading.RLock();self.transaction_lock=threading.RLock();self.local=threading.local()
        self.keys_at=self.mouse_at=self.motion_at=0;self.targets={};self.foreground=0
        self.held_keys={key for key in range(8,255) if ctypes.windll.user32.GetAsyncKeyState(key)&0x8000}
        self.held_buttons=set()
        self.last=self.tick();self.automation=False;self.hooks_ready=False
        self.waiting=lambda message:None
        self.thread=threading.Thread(target=self.run,daemon=True);self.thread.start()
        self.hook_thread=threading.Thread(target=self.hooks,daemon=True);self.hook_thread.start()

    @staticmethod
    def tick():
        class LASTINPUTINFO(ctypes.Structure):_fields_=[('cbSize',wintypes.UINT),('dwTime',wintypes.DWORD)]
        value=LASTINPUTINFO();value.cbSize=ctypes.sizeof(value)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(value));return value.dwTime

    @staticmethod
    def own_foreground():
        pid=wintypes.DWORD();hwnd=ctypes.windll.user32.GetForegroundWindow()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd,ctypes.byref(pid));return pid.value==os.getpid()

    def physical(self,kind='keyboard',hwnd=None,held=None):
        hwnd=int(hwnd or ctypes.windll.user32.GetForegroundWindow());now=self.clock()
        with self.lock:
            if kind=='keyboard':self.keys_at=now
            elif kind=='motion':self.motion_at=now
            else:self.mouse_at=now
            if held:
                collection=self.held_keys if kind=='keyboard' else self.held_buttons
                if held[1]:collection.add(held[0])
                else:collection.discard(held[0])
            # Motion by itself cannot alter a field and need not invalidate typing.
            if kind!='motion':
                previous=self.targets.get(hwnd,(0,0));self.targets[hwnd]=(now,previous[1]+1)
            if len(self.targets)>256:self.targets={hwnd:self.targets.get(hwnd,(now,0))}

    def revision(self,hwnd):
        with self.lock:return self.targets.get(int(hwnd),(0,0))[1]

    def check(self):
        generation=getattr(self.permissions.execution_context,'generation',self.permissions.generation)
        return generation==self.permissions.generation and not self.closed.is_set() and not self.permissions.halted.is_set() and not self.permissions.cancelled()

    def busy(self,hwnd,shared=False):
        with self.lock:
            now=self.clock();target_at=self.targets.get(int(hwnd),(0,0))[0]
            return now-target_at<.65 or (shared and (bool(getattr(self,'held_keys',set()) or getattr(self,'held_buttons',set())) or now-self.keys_at<.8 or now-self.mouse_at<.35 or now-self.motion_at<.18))

    def wait(self,hwnd,shared=False,timeout=5):
        from .permissions import Denied
        deadline=self.clock()+timeout;announced=False
        while self.busy(hwnd,shared):
            if not self.check():raise Denied('Stopped or permission revoked before input dispatch')
            if self.clock()>=deadline:raise Denied('Input access is busy in the target application. No action was dispatched; inspect again or use independent browser/accessibility operations.')
            if not announced:self.waiting('Waiting for input access');announced=True
            self.closed.wait(.03)
        if announced:self.waiting('')
        if not self.check():raise Denied('Stopped or permission revoked before input dispatch')

    def begin(self):return self.check()  # compatibility; never changes task state
    def end(self):self.last=self.tick()

    def run(self):
        while not self.closed.wait(.05):
            self.foreground=ctypes.windll.user32.GetForegroundWindow()
            with self.lock:
                self.held_keys={key for key in self.held_keys if ctypes.windll.user32.GetAsyncKeyState(key)&0x8000}
            current=self.tick()
            if not self.hooks_ready and current!=self.last and not self.automation:
                self.physical('keyboard',self.foreground)
            self.last=current

    def checkpoint(self,window=None):
        from .permissions import Denied
        state=getattr(self.local,'state',None)
        if not self.check():raise Denied('Stopped during input; inspect partial state before continuing')
        if state:
            if self.clock()-state['started']>2:raise Denied('Input transaction time limit; inspect partial state before continuing')
            with self.lock:
                changed=(self.keys_at>state['at'] or self.mouse_at>state['at']) if state['shared'] else self.revision(state['window'])!=state['revision']
            if changed:raise Denied('Human input took priority during this action. Completion may be partial; inspect and preserve changes. The action will not be replayed.')
        if window is not None and ctypes.windll.user32.GetForegroundWindow()!=int(window):raise Denied('Target lost keyboard focus; no further typing was sent. Inspect partial state.')

    def transaction(self,hwnd,shared=False):
        from contextlib import contextmanager
        from .permissions import Denied
        @contextmanager
        def scope():
            while not self.transaction_lock.acquire(timeout=.05):
                if not self.check():raise Denied('Stopped while waiting for input access')
            try:
                self.wait(hwnd,shared)
                if shared and not self.hooks_ready:raise Denied('Physical input monitoring is unavailable. Shared mouse/keyboard input is disabled; use background accessibility or the dedicated browser.')
                previous=getattr(self.local,'state',None)
                self.local.state={'started':self.clock(),'at':self.clock(),'window':int(hwnd),'shared':shared,'revision':self.revision(hwnd)}
                self.automation=True
                try:yield
                finally:self.local.state=previous;self.automation=False
            finally:self.transaction_lock.release()
        return scope()

    def hooks(self):
        # Observe only. Always CallNextHookEx: physical input is never swallowed.
        user=ctypes.windll.user32;kernel=ctypes.windll.kernel32
        pointer=ctypes.c_ssize_t
        callback_type=ctypes.WINFUNCTYPE(pointer,ctypes.c_int,wintypes.WPARAM,wintypes.LPARAM)
        user.SetWindowsHookExW.argtypes=[ctypes.c_int,callback_type,ctypes.c_void_p,wintypes.DWORD];user.SetWindowsHookExW.restype=ctypes.c_void_p
        user.CallNextHookEx.argtypes=[ctypes.c_void_p,ctypes.c_int,wintypes.WPARAM,wintypes.LPARAM];user.CallNextHookEx.restype=pointer
        user.UnhookWindowsHookEx.argtypes=[ctypes.c_void_p]
        class Keyboard(ctypes.Structure):_fields_=[('vk',wintypes.DWORD),('scan',wintypes.DWORD),('flags',wintypes.DWORD),('time',wintypes.DWORD),('extra',ctypes.c_size_t)]
        class Mouse(ctypes.Structure):_fields_=[('point',wintypes.POINT),('data',wintypes.DWORD),('flags',wintypes.DWORD),('time',wintypes.DWORD),('extra',ctypes.c_size_t)]
        def keyboard(code,wparam,lparam):
            if code>=0:
                value=ctypes.cast(lparam,ctypes.POINTER(Keyboard)).contents
                if not value.flags&0x10:self.physical('keyboard',held=(value.vk,wparam in (0x100,0x104)))
            return user.CallNextHookEx(None,code,wparam,lparam)
        def mouse(code,wparam,lparam):
            if code>=0:
                value=ctypes.cast(lparam,ctypes.POINTER(Mouse)).contents
                if not value.flags&1:
                    hwnd=user.WindowFromPoint(value.point);hwnd=user.GetAncestor(hwnd,2) or hwnd
                    buttons={0x201:('left',True),0x202:('left',False),0x204:('right',True),0x205:('right',False),0x207:('middle',True),0x208:('middle',False)}
                    self.physical('motion' if wparam==0x200 else 'mouse',hwnd,buttons.get(wparam))
            return user.CallNextHookEx(None,code,wparam,lparam)
        self.callbacks=(callback_type(keyboard),callback_type(mouse))
        handles=[user.SetWindowsHookExW(kind,callback,None,0) for kind,callback in zip((13,14),self.callbacks)]
        self.hooks_ready=all(handles)
        try:
            message=wintypes.MSG()
            while not self.closed.wait(.005):
                while user.PeekMessageW(ctypes.byref(message),None,0,0,1):user.TranslateMessage(ctypes.byref(message));user.DispatchMessageW(ctypes.byref(message))
        finally:
            for handle in handles:
                if handle:user.UnhookWindowsHookEx(handle)

    def close(self):
        self.closed.set();self.thread.join(timeout=1);self.hook_thread.join(timeout=1)
