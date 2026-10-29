"""Bounded host filesystem operations with local approval and recoverable originals.

Windows directory handles deny ancestor renames; file handles deny concurrent writes
and deletes. Revalidate after approval, never automatically retry a mutation.
"""
import ctypes
import hashlib
import os
import uuid
from contextlib import contextmanager,ExitStack
from pathlib import Path
from .permissions import Denied


def digest(raw):return hashlib.sha256(raw).hexdigest()


class Files:
    def __init__(self,permissions,store,approve):
        self.permissions,self.store,self.approve=permissions,store,approve

    def validate(self,value):
        path=Path(value)
        if not path.is_absolute() or '..' in path.parts or ':' in str(path)[3:] or str(path).startswith(('\\\\','//')):
            raise Denied('Use an absolute local path without traversal or alternate streams')
        for part in (path,*path.parents):
            if part.is_symlink() or (part.exists() and getattr(part.lstat(),'st_file_attributes',0)&0x400):raise Denied('Linked paths are unsupported')
        path=path.resolve();app=Path(__file__).resolve().parents[1]
        roots=[app,app.parents[1]/'portfolio_autopilot/codex_relay',self.store.directory,
               Path.home()/'.codex',Path.home()/'.ssh',Path.home()/'.aws',
               Path.home()/'AppData/Local/Google/Chrome',Path.home()/'AppData/Local/Microsoft/Edge',Path.home()/'AppData/Roaming/Mozilla',
               Path.home()/'AppData/Local/Microsoft/Credentials',Path.home()/'AppData/Roaming/Microsoft/Credentials',Path.home()/'AppData/Local/Microsoft/Vault',Path.home()/'AppData/Roaming/Microsoft/Vault',
               Path.home()/'AppData/Local/Packages',
               Path.home()/'AppData/Local/Programs',Path.home()/'AppData/Roaming/Microsoft/Windows/Start Menu',
               Path(os.environ.get('SystemRoot','C:/Windows')),Path('C:/ProgramData'),Path('C:/Program Files'),Path('C:/Program Files (x86)')]
        if any(path==r.resolve() or path.is_relative_to(r.resolve()) for r in roots):raise Denied('Protected system, application or private security location')
        if any(p.lower() in ('.git','.agents','.codex','.ssh','.aws','.azure','.gnupg') for p in path.parts) or path.name.lower() in ('auth.json','credentials','credentials.json','.env','.wslconfig','ntuser.dat','sam','security','system'):
            raise Denied('Credentials and security files require manual management')
        if path.suffix.lower() in ('.pem','.key','.pfx','.p12','.kdbx') or path.name.lower() in ('login data','cookies','key4.db','logins.json','id_rsa','id_ed25519'):raise Denied('Credential material requires manual management')
        if path.exists() and path.is_file() and path.stat().st_nlink>1:raise Denied('Hard-linked files are unsupported')
        return path

    @contextmanager
    def handle(self,path,write=False,delete=False,directory=False):
        import win32file,win32con
        access=win32con.GENERIC_READ | (win32con.GENERIC_WRITE if write else 0) | (0x10000 if delete else 0)
        # Parents permit ordinary file activity, but cannot be renamed/deleted.
        share=win32con.FILE_SHARE_READ
        h=win32file.CreateFile(str(path),access,share,None,win32con.OPEN_EXISTING,
            0x00200000 | (win32con.FILE_FLAG_BACKUP_SEMANTICS if directory else win32con.FILE_ATTRIBUTE_NORMAL),None)
        try:
            info=win32file.GetFileInformationByHandle(h)
            if info[0]&0x400 or (not directory and info[7]>1):raise Denied('Reparse or hard-linked target changed before access')
            yield h
        finally:h.Close()

    def snapshot(self,path,empty=True,read=True):
        if not path.exists():return {'kind':'missing','sha256':'new'}
        if path.is_dir():
            if empty and any(path.iterdir()):raise Denied('Directory operations are limited to empty folders; inspect and handle files individually')
            return {'kind':'folder','identity':(path.stat().st_ino,path.stat().st_mtime_ns)}
        if path.stat().st_size>500000:raise Denied('Text file operations are limited to 500 KB')
        info=path.stat();result={'kind':'file','identity':(info.st_ino,info.st_mtime_ns),'bytes':info.st_size}
        if read:result['sha256']=digest(path.read_bytes())
        return result

    def call(self,conversation,args,action):
        path=self.validate(args['path']);listing=action=='list';action='read' if listing else action
        epoch=getattr(self.permissions.execution_context,'generation',self.permissions.generation)
        with self.permissions.lock:
            decision=self.permissions.file_policy.decision(path,action)
            legacy=self.permissions.files.get(str(path))
            if decision=='ask' and legacy and (action=='read' or action=='write' and legacy=='write'):decision='allow'
        if decision=='deny':raise Denied('Explicit file policy denies '+action)
        pre_read=action!='read' or decision=='allow'
        before=self.snapshot(path,empty=action!='read',read=pre_read)
        if action in ('read','write','delete') and before['kind']=='missing':raise Denied('Target does not exist; use create for a new file')
        if action=='create' and before['kind']!='missing':raise Denied('Create cannot overwrite an existing target')
        if action in ('read','write') and before['kind']!='file' and not (listing and before['kind']=='folder'):raise Denied('This operation requires a text file')
        content=args.get('content','')
        if not isinstance(content,str) or len(content.encode('utf-8'))>500000:raise Denied('Content must be bounded text')
        if action in ('write','delete') and args.get('sha256')!=before.get('sha256', 'empty-folder'):
            raise Denied('Inspect first and provide the exact current sha256 (empty-folder for an empty folder)')
        if decision=='ask':
            preview=''
            if action=='write':
                import difflib
                preview=''.join(difflib.unified_diff(path.read_text(encoding='utf-8').splitlines(True),content.splitlines(True),fromfile='existing',tofile='proposed'))[:12000]
            details={'file_permission':True,'operation':action,'path':str(path),'reason':str(args.get('reason','Requested by the current task'))[:1000],
                     'reversible':action in ('write','delete'),'preview':preview,'expected':before}
            if not self.approve(conversation,'Permission to '+action+' '+path.name,details):raise Denied('Owner denied or interrupted the file operation')
        with self.permissions.action(conversation,epoch), ExitStack() as stack:
            if self.permissions.file_policy.decision(path,action)=='deny':raise Denied('Permission revoked while waiting')
            # Lock every existing ancestor against replacement before revalidation.
            for parent in reversed(path.parents):stack.enter_context(self.handle(parent,directory=True))
            self.validate(path)
            if self.snapshot(path,empty=action!='read',read=pre_read)!=before:raise Denied('Target changed during review; inspect again')
            if listing:
                return {'entries':[{'name':x.name,'kind':'folder' if x.is_dir() else 'file'} for x in list(path.iterdir())[:500]],'limit':500}
            expected_hash=before.get('sha256')
            if before['kind']=='file' and expected_hash is None:expected_hash=digest(path.read_bytes())
            backup=None
            if action in ('read','write','delete'):
                import win32file
                h=stack.enter_context(self.handle(path,write=action=='write',delete=action=='delete',directory=before['kind']=='folder'))
                info=win32file.GetFileInformationByHandle(h)
                if (info[8]<<32|info[9]) != before['identity'][0]&((1<<64)-1):raise Denied('Target identity changed before exclusive access')
                if before['kind']=='file':
                    raw=win32file.ReadFile(h,500001)[1]
                    if digest(raw)!=expected_hash:raise Denied('Target changed before exclusive access')
                if action=='read':
                    try:
                        text=raw.decode('utf-8')
                        if '\0' in text:raise UnicodeError('Binary file')
                        return {'content':text,'sha256':digest(raw)}
                    except UnicodeError:return {'binary':True,'bytes':len(raw),'sha256':digest(raw),'note':'Use an attachment for binary content; this hash can authorize recoverable deletion.'}
                backups=self.store.directory/'file-backups';backups.mkdir(exist_ok=True)
                backup=backups/(uuid.uuid4().hex+'.bak')
                if before['kind']=='file':backup.write_bytes(raw)
                else:backup.mkdir()
                if action=='write':
                    win32file.SetFilePointer(h,0,0);win32file.WriteFile(h,content.encode('utf-8'));win32file.SetEndOfFile(h);win32file.FlushFileBuffers(h)
                    win32file.SetFilePointer(h,0,0)
                    if win32file.ReadFile(h,500001)[1]!=content.encode('utf-8'):raise RuntimeError('Write verification failed; original is in recovery')
                else:
                    flag=ctypes.c_ubyte(1)
                    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
                    kernel.SetFileInformationByHandle.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_ulong]
                    if not kernel.SetFileInformationByHandle(int(h),4,ctypes.byref(flag),1):raise ctypes.WinError(ctypes.get_last_error())
            elif action=='create':
                if args.get('kind','file')=='folder':path.mkdir()
                elif args.get('kind','file')=='file':
                    with path.open('xb') as f:f.write(content.encode('utf-8'));f.flush();os.fsync(f.fileno())
                    if path.read_bytes()!=content.encode('utf-8'):raise RuntimeError('Creation could not be verified')
                else:raise Denied('Unknown target kind')
        if action=='delete' and path.exists():raise RuntimeError('Deletion incomplete; do not retry automatically')
        return {'operation':action,'path':str(path),'verified':True,'sha256':digest(content.encode('utf-8')) if action in ('write','create') else None,
                'recovery':str(backup) if backup else None,'note':'Private recovery copy; recovery is not guaranteed against disk failure.' if backup else ''}
