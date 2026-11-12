"""Windows entry point; no public HTTP service."""
import ctypes
import argparse
import json
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).resolve().parent))


def main():
    if os.name!='nt':raise RuntimeError('Desktop control requires Windows')
    # Qt 6 establishes per-monitor v2 DPI awareness before constructing widgets.
    from PySide6.QtWidgets import QApplication,QMessageBox
    from PySide6.QtCore import QLockFile
    from assistant.storage import private_directory
    parser=argparse.ArgumentParser(description='Codex Computer Bridge — tools for official Codex')
    parser.add_argument('--data-dir',help='Private state directory outside the checkout, for isolated testing')
    parser.add_argument('--bridge',action='store_true',help='Start the computer bridge (default)')
    parser.add_argument('--bridge-only',action='store_true',help='Open the legacy dashboard for rollback or diagnostics')
    parser.add_argument('--background',action='store_true',help='Start in the system tray')
    args=parser.parse_args()
    directory=private_directory();directory.mkdir(parents=True,exist_ok=True)
    state=Path(args.data_dir).resolve() if args.data_dir else directory
    if state.is_relative_to(ROOT) or not state.is_relative_to(Path.home()):raise ValueError('State must stay in the private user profile outside the checkout')
    app=QApplication(sys.argv);app.setApplicationName('Portfolio Manager' if not args.bridge_only else 'Codex Computer Bridge');app.setStyle('Fusion');app.setQuitOnLastWindowClosed(False)
    lock=QLockFile(str(directory/'application.lock'))
    if not lock.tryLock(100):
        if args.background:return 0
        from bridge.client import ControllerClient
        try:
            client=ControllerClient(state)
            health=client.request('bridge_health')
            client.request('portfolio_open' if health.get('portfolio_manager') and not args.bridge_only else 'bridge_open_dashboard')
            if not args.bridge_only and not health.get('portfolio_manager'):
                QMessageBox.information(None,'Portfolio Manager','The older Computer Bridge is running. Quit it from its tray menu, then open Portfolio Manager again.')
            return 0
        except (OSError,ValueError,RuntimeError):
            QMessageBox.information(None,'Portfolio Manager','The controller is already running. Open it from the Windows system tray.')
            return 1
    from bridge.migration import backup_state
    backup_state(state)
    if not args.bridge_only:
        backup_state(state,milestone='before-portfolio-manager')
    from bridge.dashboard import Dashboard
    manager=None
    if not args.bridge_only:
        from portfolio_manager.integration import ManagerHost
        manager=ManagerHost(ROOT,state)
    window=Dashboard(state,manager,restore_saved=not (args.bridge and args.background))
    if not args.background:window.show()
    result=app.exec();lock.unlock();return result


if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as error:
        # Never dump auth/protocol payloads or screenshots into console logs.
        from portfolio_autopilot.codex_relay.diagnostics import sanitize
        from assistant.storage import private_directory
        message='Desktop Assistant could not start: '+type(error).__name__+': '+sanitize(error)
        directory=private_directory();directory.mkdir(parents=True,exist_ok=True)
        (directory/'startup-error.json').write_text(json.dumps({'error':message}),encoding='utf-8')
        ctypes.windll.user32.MessageBoxW(None,message,'Codex Desktop Assistant',0x10)
        raise SystemExit(1)
