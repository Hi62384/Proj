@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -m pip install -r requirements.lock.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" tools\setup_computer_bridge.py install
if errorlevel 1 goto failed
echo Computer Bridge is ready. Give tasks in official Codex.
exit /b 0
:failed
echo Setup failed. Review the error above; existing chats and Relay were not changed.
pause
exit /b 1
