"""Installed application catalog, never a model-authored command or executable path."""
import os
import re
from pathlib import Path

BLOCK=re.compile(r'cmd|powershell|pwsh|terminal|bash|wsl|python|node|cscript|wscript|mshta|rundll|regsvr|msiexec|install|setup|uninstall|update|regedit|taskmgr|control|mmc|schtasks|runas|conhost|wt\.exe',re.I)


def catalog():
    import winreg
    roots=[Path(os.environ.get('ProgramFiles','C:/Program Files')),Path(os.environ.get('ProgramFiles(x86)','C:/Program Files (x86)')),
           Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'AppData/Local')))/'Programs',
           Path(os.environ.get('SystemRoot','C:/Windows'))]
    result={}
    def add(label,value):
        path=Path(os.path.expandvars(value.strip('"')))
        if path.suffix.lower()!='.exe' or not path.is_file() or BLOCK.search(path.name+' '+label):return
        if not any(path.resolve().is_relative_to(root.resolve()) for root in roots):return
        if path.resolve().is_relative_to(roots[-1].resolve()) and path.name.lower() not in ('notepad.exe','explorer.exe','mspaint.exe'):return
        if any(p.is_symlink() or getattr(p.lstat(),'st_file_attributes',0)&0x400 for p in (path,*path.parents)):return
        try:
            import struct
            with path.open('rb') as stream:
                if stream.read(2)!=b'MZ':return
                stream.seek(0x3c);offset=struct.unpack('<I',stream.read(4))[0]
                stream.seek(offset)
                if stream.read(4)!=b'PE\0\0':return
                stream.seek(offset+24+68)
                if struct.unpack('<H',stream.read(2))[0]!=2:return
        except (OSError,ValueError,struct.error):return
        result[label]=str(path.resolve())
    for name in ('notepad','explorer','mspaint'):
        for parent in (roots[-1],roots[-1]/'System32'):
            add(name.title(),str(parent/(name+'.exe')))
    for hive in (winreg.HKEY_LOCAL_MACHINE,winreg.HKEY_CURRENT_USER):
        for view in (winreg.KEY_WOW64_64KEY,winreg.KEY_WOW64_32KEY):
            try:
                with winreg.OpenKey(hive,r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths',0,winreg.KEY_READ|view) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        name=winreg.EnumKey(key,i)
                        try:
                            with winreg.OpenKey(key,name) as entry:add(Path(name).stem,winreg.QueryValue(entry,None))
                        except OSError:continue
            except OSError:pass
    # Start Menu shortcuts for ordinary apps such as Blender/Godot. Read only;
    # never execute a shortcut, arguments, URI, script or user download.
    try:
        import win32com.client
        shell=win32com.client.Dispatch('WScript.Shell')
        for root in (Path(os.environ['ProgramData'])/'Microsoft/Windows/Start Menu/Programs',Path(os.environ['APPDATA'])/'Microsoft/Windows/Start Menu/Programs'):
            for link in list(root.rglob('*.lnk'))[:2000]:
                shortcut=shell.CreateShortcut(str(link))
                if not shortcut.Arguments:add(link.stem,shortcut.TargetPath)
    except Exception:pass
    return dict(sorted(result.items(),key=lambda x:x[0].lower()))
