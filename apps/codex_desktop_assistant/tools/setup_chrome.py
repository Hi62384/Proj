"""Per-user Chrome Native Messaging installer. Never modifies Chrome profiles."""
import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from assistant.storage import private_directory
from assistant.chrome_bridge import private_json
HOST='com.codex.desktop_assistant'


def der(tag,value):
    length=len(value);raw=length.to_bytes(max(1,(length.bit_length()+7)//8),'big')
    return bytes([tag])+(bytes([length]) if length<128 else bytes([128+len(raw)])+raw)+value


def prepare():
    directory=APP/'chrome_extension';manifest_path=directory/'manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    if not manifest.get('key'):
        script='$r=[System.Security.Cryptography.RSA]::Create(); $r.KeySize=2048; $p=$r.ExportParameters($false); @{modulus=[Convert]::ToBase64String($p.Modulus); exponent=[Convert]::ToBase64String($p.Exponent)} | ConvertTo-Json -Compress; $r.Dispose()'
        result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',script],capture_output=True,text=True,check=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        values=json.loads(result.stdout)
        def integer(value):
            value=base64.b64decode(value).lstrip(b'\0') or b'\0'
            return der(2,(b'\0' if value[0]&128 else b'')+value)
        rsa=der(48,integer(values['modulus'])+integer(values['exponent']))
        spki=der(48,bytes.fromhex('300d06092a864886f70d0101010500')+der(3,b'\0'+rsa))
        manifest['key']=base64.b64encode(spki).decode();manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    digest=hashlib.sha256(base64.b64decode(manifest['key'])).hexdigest()[:32]
    extension_id=''.join(chr(ord('a')+int(c,16)) for c in digest)
    from PIL import Image,ImageDraw
    for size in (16,32,128):
        path=directory/f'icon{size}.png'
        if path.exists():continue
        image=Image.new('RGBA',(size,size),(17,24,39,255));draw=ImageDraw.Draw(image);scale=size/128
        points=[(92,30),(45,30),(24,64),(45,98),(92,98)]
        draw.line([(int(x*scale),int(y*scale)) for x,y in points],fill=(45,212,191),width=max(2,int(12*scale)))
        draw.line([(int(65*scale),int(64*scale)),(int(106*scale),int(64*scale))],fill='white',width=max(2,int(9*scale)));image.save(path)
    return extension_id


def install():
    import winreg
    extension_id=prepare();directory=private_directory()/'chrome-host';directory.mkdir(parents=True,exist_ok=True)
    python=APP/'.venv/Scripts/python.exe'
    if not python.is_file():raise RuntimeError('Run Setup Desktop Assistant first')
    wrapper=directory/'native_host.cmd'
    wrapper.write_text('@echo off\r\n"'+str(python)+'" -I -u "'+str(APP/'chrome_native_host.py')+'" %*\r\n',encoding='utf-8')
    manifest={'name':HOST,'description':'Codex Desktop Assistant authorized Chrome tabs','path':str(wrapper),'type':'stdio','allowed_origins':['chrome-extension://'+extension_id+'/']}
    target=directory/(HOST+'.json');private_json(target,manifest);private_json(directory/'settings.json',{'extension_id':extension_id,'version':1})
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER,'Software\\Google\\Chrome\\NativeMessagingHosts\\'+HOST) as key:winreg.SetValueEx(key,'',0,winreg.REG_SZ,str(target))
    return {'extension_id':extension_id,'extension_folder':str(APP/'chrome_extension'),'native_host_registered':True,'chrome_installation_required':True}


def health():
    import winreg
    result={'extension_folder':str(APP/'chrome_extension'),'chrome_installed':any((Path(root)/'Google/Chrome/Application/chrome.exe').is_file() for root in (os.environ.get('ProgramFiles',''),os.environ.get('ProgramFiles(x86)',''),os.environ.get('LOCALAPPDATA','')))}
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,'Software\\Google\\Chrome\\NativeMessagingHosts\\'+HOST) as key:path=Path(winreg.QueryValueEx(key,'')[0])
        manifest=json.loads(path.read_text());result['native_host_registered']=Path(manifest['path']).is_file();result['allowed_origins']=manifest['allowed_origins']
    except (OSError,ValueError,KeyError):result['native_host_registered']=False
    result['note']='Installation preparation is not proof Chrome loaded the extension. Use Check Connection in the assistant for a real round trip.'
    return result


def uninstall():
    import winreg
    try:winreg.DeleteKey(winreg.HKEY_CURRENT_USER,'Software\\Google\\Chrome\\NativeMessagingHosts\\'+HOST)
    except FileNotFoundError:pass
    # Keep identity/settings for reversible reinstall. Remove extension in Chrome.
    return {'native_host_unregistered':True,'next':'Remove the extension at chrome://extensions. Browser profiles and conversations were preserved.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=['prepare','install','health','uninstall']);args=parser.parse_args()
    try:print(json.dumps({'prepare':prepare,'install':install,'health':health,'uninstall':uninstall}[args.operation](),ensure_ascii=True,indent=2))
    except Exception as error:print(json.dumps({'error':type(error).__name__+': '+str(error)}));raise SystemExit(1)

