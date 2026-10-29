@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call Setup_Desktop_Assistant.cmd
if not exist ".venv\Scripts\python.exe" exit /b 1
".venv\Scripts\python.exe" "tools\setup_chrome.py" install
endlocal
