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

    def notify(self,category,key):
        if key in self.seen:return
        self.seen.add(key)
        if not self.window.store.settings().get('notify_'+category,category!='info'):return
        self.unread+=1;self.window.attention_button.setText(f'Requests · {self.unread}')
        # Never expose model text, filenames, website/account details or document content.
        text={'input':'Your input is needed. Open the assistant to review the pending request.',
              'error':'A task needs attention. Open the assistant to review it.',
              'info':'Your task has finished.'}[category]
        QApplication.alert(self.window,0)
        if self.tray.isVisible() and self.tray.supportsMessages():
            self.tray.showMessage('Codex Desktop Assistant',text,QSystemTrayIcon.Warning if category!='info' else QSystemTrayIcon.Information,10000)
        self.window.notice.setText(text)


class InputGuard:
    """Poll foreground ownership and physical input. Never blocks physical input.

    GetLastInputInfo excludes no injected input, so sample immediately after each
    host action as a baseline. A changed input tick between actions yields to owner.
    """
    def __init__(self,permissions,active,callback):
        self.permissions,self.active,self.callback=permissions,active,callback
        self.closed=threading.Event();self.armed=False;self.foreground=False
        self.last=self.tick();self.automation=False
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
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
        return pid.value==os.getpid()

    def check(self):
        current=self.tick()
        if self.armed and not self.automation and current!=self.last:
            self.last=current;self.pause('Paused — Your Input');return False
        self.last=current
        return not self.permissions.halted.is_set()

    def begin(self):
        if not self.check():return False
        self.automation=True;return True

    def end(self):self.last=self.tick();self.automation=False

    def pause(self,reason):
        self.armed=False;self.callback(reason)

    def run(self):
        while not self.closed.wait(.05):
            own=self.own_foreground();active=self.active()
            if active and self.permissions.desktop and not self.permissions.halted.is_set() and not self.permissions.desktop_suspended:
                if not own:self.armed=True
                if own and not self.foreground and self.armed:self.pause('Paused — Chat Open')
                elif self.armed and not own and not self.automation:self.check()
            else:self.armed=False;self.last=self.tick()
            self.foreground=own

    def physical(self):
        if self.active() and self.permissions.desktop and not self.permissions.halted.is_set() and not self.permissions.desktop_suspended:
            self.armed=False;self.permissions.desktop_suspended=True
            # Low-level hooks must return promptly; durable task interruption is
            # dispatched elsewhere after immediately closing the desktop gate.
            threading.Thread(target=self.callback,args=('Paused — Your Input',),daemon=True).start()

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
            if code>=0 and not ctypes.cast(lparam,ctypes.POINTER(Keyboard)).contents.flags&0x10:self.physical()
            return user.CallNextHookEx(None,code,wparam,lparam)
        def mouse(code,wparam,lparam):
            if code>=0 and not ctypes.cast(lparam,ctypes.POINTER(Mouse)).contents.flags&1:self.physical()
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
