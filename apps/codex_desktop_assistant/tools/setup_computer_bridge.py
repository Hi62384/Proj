"""Register only this named MCP server; preserve unrelated Codex and Chrome setup."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(APP.parents[1])]
from bridge.migration import backup_state
from assistant.storage import private_directory


def codex_binary():
    candidates=sorted((Path(os.environ['LOCALAPPDATA'])/'OpenAI/Codex/bin').glob('*/codex.exe'),key=lambda p:p.stat().st_mtime,reverse=True)
    if candidates:return str(candidates[0])
    value=shutil.which('codex.exe') or shutil.which('codex.cmd')
    if not value:raise RuntimeError('Install official Codex before registering the bridge')
    return value


def main():
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=['install','uninstall','health']);parser.add_argument('--trust-local-tools',action='store_true',help='Only after the owner explicitly approves trusting this local integration');args=parser.parse_args();binary=codex_binary()
    config=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'config.toml'
    if args.operation in ('install','uninstall'):
        backup_state(private_directory())
        if config.is_file():shutil.copy2(config,config.with_name('config.before-computer-bridge-'+time.strftime('%Y%m%d-%H%M%S')+'.toml'))
    if args.operation=='install':
        subprocess.run([binary,'mcp','add','codex_computer_bridge','--',str(APP/'.venv/Scripts/python.exe'),str(APP/'bridge/server.py')],check=True)
        # Trust only this server's dispatch, whose owner-controlled local policy
        # still reviews sensitive actions. Avoid a second Codex approval for each
        # harmless click; do not change shell sandbox or other MCP policies.
        import re,tomllib
        text=config.read_text(encoding='utf-8');header='[mcp_servers.codex_computer_bridge]'
        start=text.index(header)+len(header);end=text.find('\n[',start)
        if end<0:end=len(text)
        section=text[start:end]
        if args.trust_local_tools:section=re.sub(r'^default_tools_approval_mode\s*=.*\n?','',section,flags=re.M)
        section=re.sub(r'^startup_timeout_sec\s*=.*\n?','',section,flags=re.M)
        section=re.sub(r'^tool_timeout_sec\s*=.*\n?','',section,flags=re.M)
        section=re.sub(r'^required\s*=.*\n?','',section,flags=re.M)
        trust='default_tools_approval_mode = "approve"\n' if args.trust_local_tools else ''
        text=text[:start]+'\n'+trust+'required = true\nstartup_timeout_sec = 35\ntool_timeout_sec = 360\n'+section.lstrip('\n')+text[end:]
        tomllib.loads(text);config.write_text(text,encoding='utf-8')
        # Existing extension key, identity and per-user native-host registration
        # remain intact. Setup_Chrome is only needed on a first installation.
        if not (private_directory()/'chrome-host/settings.json').is_file():
            subprocess.run([sys.executable,str(APP/'tools/setup_chrome.py'),'install'],check=True)
        print('Registered Codex Computer Bridge. Official Codex starts it automatically for new connections. Existing configuration and history were backed up.')
    elif args.operation=='uninstall':
        subprocess.run([binary,'mcp','remove','codex_computer_bridge'],check=True)
        print('Removed only the bridge MCP registration. Quit the bridge from its tray menu. History, generated files, Chrome sign-ins, extension and other servers were preserved.')
    else:
        subprocess.run([binary,'mcp','get','codex_computer_bridge'],check=True)
        from bridge.client import ControllerClient
        print(json.dumps(ControllerClient().ensure(),indent=2))


if __name__=='__main__':main()
