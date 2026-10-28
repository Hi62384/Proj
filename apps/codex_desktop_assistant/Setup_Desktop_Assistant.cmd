@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -m pip install -r requirements.lock.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m playwright install chromium
if errorlevel 1 goto failed
echo Desktop Assistant is ready. Open Start_Desktop_Assistant.cmd.
exit /b 0
:failed
echo Setup failed. Review the error above; existing chats and Relay were not changed.
pause
exit /b 1
