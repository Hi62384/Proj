"""Windows UI Automation with exact live-window grants and no shell capability."""
import ctypes
import io
import os
import re
import threading
import time
import uuid
from ctypes import wintypes

from PIL import ImageGrab,ImageDraw
from .attachments import image_url
from .permissions import Denied

FORBIDDEN = re.compile(r'password|sign.in|log.in|verification|captcha|authenticator|windows security|credential|powershell|command prompt|windows terminal|task manager|registry editor|codex desktop assistant|codex computer bridge|chatgpt|security challenge|one.time code',re.I)
KEYS = {'ENTER':'{ENTER}','TAB':'{TAB}','ESC':'{ESC}','BACKSPACE':'{BACKSPACE}',
        'UP':'{UP}','DOWN':'{DOWN}','LEFT':'{LEFT}','RIGHT':'{RIGHT}',
        'CTRL+A':'^a','CTRL+C':'^c','CTRL+V':'^v','CTRL+S':'^s','HOME':'{HOME}','END':'{END}','PAGEUP':'{PGUP}','PAGEDOWN':'{PGDN}'}
TERMINAL_CLASSES={'consolewindowclass','cascadia_hosting_window_class'}


class Desktop:
    def __init__(self, permissions):
        self.permissions=permissions
        self.observations={}
        self.image_geometry={}
        self.exclusions=['password','bank','authenticator']

    @staticmethod
    def _api():
        from pywinauto import Desktop as WindowsDesktop
        return WindowsDesktop(backend='uia')

    @staticmethod
    def password(control):
        try:return bool(control.element_info.element.CurrentIsPassword)
        except AttributeError:return bool(control.element_info._element.CurrentIsPassword)

    def windows(self):
        result=[]
        for w in self._api().windows():
            try:
                title=w.window_text()
                if title and w.process_id()!=os.getpid() and w.class_name().lower() not in TERMINAL_CLASSES and w.is_visible() and not FORBIDDEN.search(title) and not any(x.lower() in title.lower() for x in self.exclusions if x):
                    result.append({'hwnd':w.handle,'pid':w.process_id(),'title':title[:200]})
            except Exception:continue
        return result[:100]

    @staticmethod
    def monitors():
        import win32api
        monitors=[tuple(rect) for _,_,rect in win32api.EnumDisplayMonitors()]
        if monitors:
            monitors.append((min(r[0] for r in monitors),min(r[1] for r in monitors),max(r[2] for r in monitors),max(r[3] for r in monitors)))
        return monitors

    def identity(self, hwnd):
        import win32api
        import win32process
        if not ctypes.windll.user32.IsWindow(int(hwnd)):raise Denied('Window no longer exists; refresh the window picker')
        try:w=self._api().window(handle=int(hwnd)).wrapper_object()
        except Exception as error:raise Denied('Window is no longer available to accessibility; inspect again') from error
        process=win32api.OpenProcess(0x1000,False,w.process_id())
        try:created=str(win32process.GetProcessTimes(process)['CreationTime'])
        finally:process.Close()
        return (w.process_id(),w.class_name(),created)

    def window(self, hwnd):
        hwnd=int(hwnd)
        grant=self.permissions.windows.get(hwnd);identity=self.identity(hwnd)
        monitor=self.permissions.desktop_mode=='Entire Monitor' and self.permissions.capture_bounds is not None
        if monitor:
            layout=tuple(self.monitors())
            if self.permissions.monitor_layout is None or layout!=tuple(self.permissions.monitor_layout):
                self.permissions.halt();raise Denied('Display configuration changed; authorize the monitor again')
            candidate=self._api().window(handle=hwnd).wrapper_object();r=candidate.rectangle()
            left,top,right,bottom=self.permissions.capture_bounds
            if r.left<left or r.top<top or r.right>right or r.bottom>bottom:raise Denied('Window leaves the authorized monitor; move it fully inside manually')
            grant=identity
        if not grant:
            owner=ctypes.windll.user32.GetAncestor(hwnd,3)
            parent_grant=self.permissions.windows.get(owner)
            if parent_grant and tuple(parent_grant)==self.identity(owner) and identity[0]==parent_grant[0] and identity[2]==parent_grant[2]:grant=identity
        if not grant or tuple(grant)!=identity:raise Denied('Window is not approved or its identity changed')
        w=self._api().window(handle=hwnd).wrapper_object()
        if (self.permissions.chrome_mode or self.permissions.chrome_protected) and w.class_name().lower().startswith('chrome_widget'):
            raise Denied('Use the authorized Chrome extension; native desktop control cannot bypass Chrome tab grants or Manual Control')
        if self.permissions.browser_manual and (w.process_id() in self.permissions.browser_pids or (not self.permissions.browser_pids and w.class_name().lower().startswith('chrome_widget'))):
            raise Denied('The dedicated browser is under Manual Control')
        if w.process_id()==os.getpid():raise Denied('The assistant cannot operate its own permission or approval UI')
        if w.class_name().lower() in TERMINAL_CLASSES:raise Denied('Terminal windows cannot be automated, even with a renamed title')
        title=w.window_text()
        if FORBIDDEN.search(title) or any(x.lower() in title.lower() for x in self.exclusions if x):
            raise Denied('Sensitive window: take over manually')
        return w

    def has_password(self,window):
        for control in window.descendants()[:180]:
            try:
                if control.is_visible() and self.password(control):return True
            except Exception:continue
        return False

    def action_context(self,window,control,args):
        """Local process/UIA evidence. Never accept an editor hint from the model."""
        from pathlib import Path
        role=control.element_info.control_type if control is not None else ''
        label=(control.element_info.name or control.window_text()) if control is not None else ''
        result={'source':'desktop','role':role,'label':label,'key':args.get('key',''),
                'window':int(window.handle),'application':window.window_text()[:150],
                'file_dialog':window.class_name().lower()=='#32770' or label.strip().lower() in ('file name','file name:','filename'),
                'filesystem_activation':window.class_name().lower() in ('cabinetwclass','explorewclass','shell_traywnd','workerw','progman') and role in ('ListItem','DataItem','TreeItem','MenuItem')}
        try:
            import win32api
            handle=win32api.OpenProcess(0x1000,False,window.process_id())
            try:
                query=ctypes.windll.kernel32.QueryFullProcessImageNameW
                query.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD)];query.restype=wintypes.BOOL
                buffer=ctypes.create_unicode_buffer(32768);length=wintypes.DWORD(len(buffer))
                if not query(int(handle),0,buffer,ctypes.byref(length)):raise OSError('Process identity unavailable')
                path=Path(buffer.value).resolve()
                roots=[Path(os.environ.get('SystemRoot','C:/Windows')).resolve(),Path(os.environ.get('ProgramFiles','C:/Program Files')).resolve(),Path(os.environ.get('ProgramFiles(x86)','C:/Program Files (x86)')).resolve()]
                result['local_editor']=path.name.lower() in ('notepad.exe','wordpad.exe','notepad++.exe') and any(path.is_relative_to(root) for root in roots)
                result['process_name']=path.name
            finally:handle.Close()
        except (OSError,AttributeError,TypeError):result['local_editor']=False
        if control is not None:
            try:result['expands_menu']=role in ('MenuItem','ComboBox') and not control.element_info.element.CurrentIsInvokePatternAvailable and control.iface_expand_collapse.CurrentExpandCollapseState in (0,1,2)
            except Exception:pass
            try:
                import win32gui,win32con
                result['multiline']=role in ('Edit','Document') and 'edit' in control.class_name().lower() and bool(win32gui.GetWindowLong(control.handle,win32con.GWL_STYLE)&4)
            except Exception:pass
        return result

    def inspect(self, hwnd):
        w=self.window(hwnd);result=[];elements={}
        for index,control in enumerate([w]+w.descendants()[:180]):
            try:
                if not control.is_visible():continue
                info=control.element_info
                password=self.password(control)
                name=(info.name or control.window_text())[:300]
                if password:name='[Password field: owner takeover required]'
                value=''
                checked=None
                if not password and info.control_type in ('Edit','Document','ComboBox'):
                    try:value=str(self.signature(control))[:20000 if info.control_type=='Document' else 1000]
                    except Exception:pass
                if info.control_type=='CheckBox':
                    try:checked=control.get_toggle_state()
                    except Exception:pass
                result.append({'element':index,'name':name,'value':value,'checked':checked,'role':info.control_type,'enabled':control.is_enabled(),'password':password})
                elements[index]=control
            except Exception:continue
        token=uuid.uuid4().hex
        signatures={i:self.signature(c) for i,c in elements.items() if c.element_info.control_type in ('Edit','Document','ComboBox','CheckBox')}
        self.observations[int(hwnd)]=(token,time.monotonic(),elements,signatures)
        r=w.rectangle()
        return {'window':int(hwnd),'title':w.window_text(),'observation':token,'bounds':[r.left,r.top,r.width(),r.height()],'controls':result}

    def capture(self, hwnd=None):
        if not self.permissions.observe:raise Denied('Screen observation is off')
        if hwnd is None:
            bounds=self.permissions.capture_bounds
            if bounds is None:raise Denied('No monitor capture scope was approved')
            if tuple(bounds) not in self.monitors():raise Denied('Monitor layout changed; review its capture scope again')
            image=ImageGrab.grab(bbox=bounds,all_screens=True)
            painter=ImageDraw.Draw(image)
            for window in self._api().windows():
                try:
                    title=window.window_text()
                    if window.is_visible() and (window.process_id()==os.getpid() or ((self.permissions.chrome_mode or self.permissions.chrome_protected) and window.class_name().lower().startswith('chrome_widget')) or (self.permissions.browser_manual and (window.process_id() in self.permissions.browser_pids or (not self.permissions.browser_pids and window.class_name().lower().startswith('chrome_widget')))) or window.class_name().lower() in TERMINAL_CLASSES or FORBIDDEN.search(title) or any(x.lower() in title.lower() for x in self.exclusions if x) or self.has_password(window)):
                        r=window.rectangle();painter.rectangle((r.left-bounds[0],r.top-bounds[1],r.right-bounds[0],r.bottom-bounds[1]),fill='black')
                except Exception:
                    raise Denied('Could not verify sensitive-window masking; use exact-window observation')
        else:
            if hwnd=='active':hwnd=ctypes.windll.user32.GetForegroundWindow()
            w=self.window(hwnd)
            if not w.is_visible():raise Denied('Selected window is not visible')
            if self.has_password(w):raise Denied('Visible password field; complete authentication manually before observation')
            image=ImageGrab.grab(window=int(hwnd))
        out=io.BytesIO();image.save(out,format='PNG')
        return out.getvalue()

    @staticmethod
    def signature(control):
        role=control.element_info.control_type
        try:
            if role=='CheckBox':return control.get_toggle_state()
            if role=='ComboBox':return str(control.selected_text())
            try:return str(control.get_value())
            except Exception:return str(control.iface_text.DocumentRange.GetText(20001))
        except Exception:return None

    def control(self,args,conversation=None,generation=None):
        coordinator=self.permissions.input_coordinator
        from contextlib import nullcontext
        shared=args.get('operation') in ('focus','move_window','keypress','right_click','double_click','move_mouse','coordinate_click','scroll','drag')
        scope=coordinator.transaction(args['window'],shared) if coordinator else nullcontext()
        with scope:
            with self.permissions.action(conversation or self.permissions.owner,generation):
                if self.permissions.manual_requests:raise Denied('Waiting for the owner to complete the requested manual step')
                result=self._control(args)
                self.window(args['window'])
                return result

    def _control(self, args):
        if self.permissions.halted.is_set() or self.permissions.desktop_suspended:raise Denied('Desktop input is paused')
        if self.permissions.cancelled():raise Denied('Originating turn ended; action cancelled')
        if args.get('operation')=='check' and type(args.get('checked')) is not bool:raise ValueError('checked must be a JSON boolean')
        if not self.permissions.desktop:raise Denied('Desktop input is off')
        hwnd=int(args['window']);w=self.window(hwnd)
        op=args['operation']
        guard=self.permissions.input_coordinator
        if guard:guard.checkpoint()
        if op=='focus':w.set_focus();return self.inspect(hwnd)
        if op=='move_window':
            values=args['bounds']
            if self.permissions.desktop_mode=='Entire Monitor':
                l,t,r,b=self.permissions.capture_bounds
                if len(values)!=4 or values[0]<l or values[1]<t or values[0]+values[2]>r or values[1]+values[3]>b:raise Denied('Move would leave the monitor scope')
            if len(values)!=4 or not all(type(v) is int and abs(v)<20000 for v in values):raise ValueError('Invalid window bounds')
            import win32gui,win32con
            win32gui.SetWindowPos(hwnd,0,*values,win32con.SWP_NOACTIVATE|win32con.SWP_NOZORDER)
            return self.inspect(hwnd)
        observation=self.observations.get(hwnd,('',0,{},{}))
        token,at,elements=observation[:3]
        for index,signature in (observation[3] if len(observation)>3 else {}).items():
            if self.signature(elements[index])!=signature:raise Denied('The owner or application changed a field after inspection. Nothing was dispatched; inspect again and preserve those edits.')
        if args.get('observation')!=token or time.monotonic()-at>45:raise Denied('Inspect this window again before acting')
        control=elements.get(int(args.get('element',-1)))
        if op not in ('move_mouse','coordinate_click','drag','scroll') and control is None:raise Denied('Select an accessible element from the latest observation')
        if control is not None:
            text_surface=control.element_info.control_type in ('Edit','Document') and self.action_context(w,control,args).get('local_editor',False)
            # A verified plain editor's content is data, not the name of an auth
            # control or a command runner. Real password flags/windows stay denied.
            if self.password(control) or (not text_surface and FORBIDDEN.search(control.element_info.name or control.window_text())):raise Denied('Authentication or sensitive control: take over')
            if not control.is_visible() or not control.is_enabled():raise Denied('Control is no longer available')
            if not text_surface and re.search(r'address|command|terminal|run dialog',control.window_text(),re.I):raise Denied('Command/address controls require manual operation')
        # Every action invalidates its observation; subsequent actions must inspect again.
        self.observations.pop(hwnd,None)
        if op=='click':
            try:control.invoke()
            except (AttributeError,NotImplementedError):
                from contextlib import nullcontext
                guard=self.permissions.input_coordinator
                with guard.transaction(hwnd,True) if guard else nullcontext():
                    if guard:guard.checkpoint()
                    control.click_input()
        elif op=='right_click':control.click_input(button='right')
        elif op=='double_click':control.double_click_input()
        elif op=='type':
            from pywinauto.uia_defines import NoPatternInterfaceError
            if control.element_info.control_type not in ('Edit','Document','ComboBox'):raise Denied('Text entry requires an editable target; typing into an activation control is unsupported')
            text=str(args['text'])[:20000]
            if control.element_info.control_type in ('Edit','Document'):
                try:control.set_edit_text(text)
                except (AttributeError,NotImplementedError,NoPatternInterfaceError):self.type_focused(w,control,text)
            else:self.type_focused(w,control,text)
        elif op=='select':
            text=str(args['text'])[:200]
            qt=control.element_info.element.CurrentFrameworkId=='Qt'
            if not qt:
                try:control.select(text)
                except (IndexError,NotImplementedError):pass
            time.sleep(.1)
            if control.selected_text()!=text:
                # Qt exposes some popup options outside the combo's UIA subtree.
                # Use focused text search, with every SendKeys metacharacter escaped.
                guard=self.permissions.input_coordinator
                from contextlib import nullcontext
                with guard.transaction(hwnd,True) if guard else nullcontext():
                    w.set_focus();control.set_focus();control.click_input()
                    foreground=ctypes.windll.user32.GetForegroundWindow()
                    if foreground!=hwnd and ctypes.windll.user32.GetAncestor(foreground,3)!=hwnd:raise Denied('Could not focus dropdown')
                    escaped=''.join('{'+c+'}' if c in '+^%{}~()' else c for c in text)
                    if guard:guard.checkpoint(hwnd)
                    control.type_keys('{HOME}'+escaped+'{ENTER}',set_foreground=False,with_spaces=True,vk_packet=False)
            deadline=time.monotonic()+1
            while control.selected_text()!=text and time.monotonic()<deadline:time.sleep(.03)
            if control.selected_text()!=text:raise RuntimeError('Dropdown selection was not verified')
        elif op=='check':
            desired=bool(args['checked'])
            if bool(control.get_toggle_state())!=desired:control.toggle()
        elif op=='keypress':
            key=args['key'].upper()
            if key=='CTRL+V':raise Denied('Pasting private clipboard content requires manual takeover')
            if key not in KEYS:raise Denied('Shortcut is not in the bounded key list')
            if guard:guard.checkpoint()
            control.set_focus()
            if guard:guard.checkpoint(hwnd)
            if ctypes.windll.user32.GetForegroundWindow()!=hwnd:raise Denied('Focus was not acquired')
            control.type_keys(KEYS[key],set_foreground=False)
        elif op in ('move_mouse','coordinate_click','drag','scroll'):
            from pywinauto import mouse
            r=w.rectangle()
            capture=self.image_geometry.get(hwnd)
            if not capture or args.get('capture')!=capture['capture'] or time.monotonic()-capture['at']>45:
                raise Denied('Observe the window again and include its current capture token for pixel input')
            if [r.left,r.top,r.width(),r.height()]!=capture['bounds']:raise Denied('Window moved, resized or changed DPI; capture it again')
            self.image_geometry.pop(hwnd,None)
            def point(key):
                x,y=args[key]
                width,height=capture['image_size']
                if not (0<=x<width and 0<=y<height):raise Denied('Coordinates leave approved capture')
                p=(r.left+int(x*r.width()/width),r.top+int(y*r.height()/height))
                under=ctypes.windll.user32.WindowFromPoint(wintypes.POINT(*p))
                root=ctypes.windll.user32.GetAncestor(under,2)
                if root!=hwnd:raise Denied('Another window occludes the approved input target')
                return p
            p=point('point')
            if guard:guard.checkpoint()
            if op=='move_mouse':mouse.move(coords=p)
            elif op=='coordinate_click':mouse.click(coords=p,button=args.get('button','left'))
            elif op=='scroll':mouse.scroll(coords=p,wheel_dist=max(-10,min(10,int(args['amount']))))
            else:
                end=point('end');epoch=self.permissions.generation;position=p;mouse.press(coords=p)
                try:
                    for step in range(1,11):
                        if self.permissions.halted.is_set() or epoch!=self.permissions.generation:break
                        if guard:guard.checkpoint()
                        position=(round(p[0]+(end[0]-p[0])*step/10),round(p[1]+(end[1]-p[1])*step/10))
                        mouse.move(coords=position);time.sleep(.015)
                finally:mouse.release(coords=position)
        else:raise ValueError('Unsupported desktop operation')
        self.image_geometry.pop(hwnd,None)
        return self.inspect(hwnd)

    def type_focused(self,window,control,text):
        from contextlib import nullcontext
        guard=self.permissions.input_coordinator
        text=text.replace('\r\n','\n').replace('\r','\n')
        if '\n' in text or '\r' in text or '\t' in text:
            context=self.action_context(window,control,{'operation':'type'})
            if not (context.get('local_editor') or context.get('multiline')):
                raise Denied('This target lacks semantic text entry and verified multiline editing. Keyboard Enter could send a form/message; use a semantic field or the dedicated browser instead.')
        if len(text)>256:raise Denied('Shared keyboard fallback is limited to 256 characters per inspected action; use semantic accessibility or dedicated browser input for longer text')
        with guard.transaction(window.handle,True) if guard else nullcontext():
            if guard:guard.checkpoint()
            window.set_focus();control.set_focus()
            for character in text:
                if self.permissions.halted.is_set() or self.permissions.cancelled():raise Denied('Typing stopped; inspect partial text before continuing')
                if guard:guard.checkpoint(window.handle)
                elif ctypes.windll.user32.GetForegroundWindow()!=window.handle:raise Denied('The approved text target lost focus')
                escaped='{'+character+'}' if character in '+^%{}~()' else character
                control.type_keys(escaped,pause=.001,set_foreground=False,with_spaces=True,with_newlines=True,with_tabs=True,vk_packet=True)

    def register_image(self,hwnd,image_size):
        w=self.window(hwnd);r=w.rectangle()
        value={'capture':uuid.uuid4().hex,'image_size':image_size,'bounds':[r.left,r.top,r.width(),r.height()],'at':time.monotonic()}
        self.image_geometry[int(hwnd)]=value
        return {key:v for key,v in value.items() if key!='at'}

    @staticmethod
    def installed_apps():
        from .applications import catalog
        return catalog()

    def open_application(self,name):
        import subprocess
        from pathlib import Path
        if self.permissions.halted.is_set() or self.permissions.desktop_suspended:raise Denied('Desktop input is paused')
        epoch=self.permissions.generation
        executable=(self.installed_apps().get(name) if self.permissions.allow_launches else None) or self.permissions.applications.get(name)
        if not executable or Path(executable).suffix.lower()!='.exe':raise Denied('Application executable was not approved locally')
        if FORBIDDEN.search(Path(executable).stem):raise Denied('Terminal and sensitive applications are unsupported')
        guard=self.permissions.input_coordinator
        if guard:guard.wait(0,True)
        if self.permissions.cancelled() or self.permissions.halted.is_set() or epoch!=self.permissions.generation or self.permissions.manual_requests:raise Denied('Launch cancelled or waiting for the owner')
        # One owner-selected existing executable; no arguments, shell or command string.
        process=subprocess.Popen([executable],cwd=str(Path(executable).parent))
        return {'started':name,'process':process.pid,'next':'New window must stay inside the approved monitor, or be selected in Desktop Access.'}


class EmergencyStop:
    """Ctrl+Alt+F12 uses its own Windows message thread, independent of inference."""
    def __init__(self, callback):
        self.callback=callback;self.thread_id=None;self.ready=threading.Event();self.registered=False
        self.thread=threading.Thread(target=self.run,daemon=True);self.thread.start()
        self.ready.wait(3)

    def run(self):
        user=ctypes.windll.user32;self.thread_id=ctypes.windll.kernel32.GetCurrentThreadId()
        self.registered=bool(user.RegisterHotKey(None,1,0x0002|0x0001|0x4000,0x7B))
        self.ready.set()
        if not self.registered:return
        message=wintypes.MSG()
        try:
            while user.GetMessageW(ctypes.byref(message),None,0,0)>0:
                if message.message==0x0312:self.callback()
        finally:user.UnregisterHotKey(None,1)

    def close(self):
        if self.thread_id:ctypes.windll.user32.PostThreadMessageW(self.thread_id,0x0012,0,0)
        self.thread.join(timeout=2)


class SessionGuard:
    """Pause on secure desktops or a sleep gap; never silently regain input authority."""
    def __init__(self,callback,desktop_check=None,clock=time.monotonic):
        self.callback=callback;self.clock=clock;self.desktop_check=desktop_check or self.default_desktop
        self.last=clock();self.allowed=True;self.lock=threading.Lock();self.stopped=threading.Event()
        self.thread=threading.Thread(target=self.run,daemon=True);self.thread.start()

    @staticmethod
    def default_desktop():
        user=ctypes.windll.user32
        user.OpenInputDesktop.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];user.OpenInputDesktop.restype=wintypes.HANDLE
        user.GetUserObjectInformationW.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(wintypes.DWORD)]
        user.CloseDesktop.argtypes=[wintypes.HANDLE]
        handle=user.OpenInputDesktop(0,False,1)
        if not handle:return False
        try:
            name=ctypes.create_unicode_buffer(256);needed=wintypes.DWORD()
            return bool(user.GetUserObjectInformationW(handle,2,name,ctypes.sizeof(name),ctypes.byref(needed))) and name.value.lower()=='default'
        finally:user.CloseDesktop(handle)

    def check(self):
        with self.lock:
            now=self.clock();gap=now-self.last;self.last=now
            try:current=bool(self.desktop_check())
            except Exception:current=False
            pause=gap>3 or (self.allowed and not current)
            self.allowed=current
        if pause:self.callback()
        return current and gap<=3

    def run(self):
        while not self.stopped.wait(.2):self.check()

    def close(self):
        self.stopped.set();self.thread.join(timeout=2)

