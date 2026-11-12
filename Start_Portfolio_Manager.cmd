@echo off
setlocal
cd /d "%~dp0"
set "PM_APP=%~dp0apps\codex_desktop_assistant"
if not exist "%PM_APP%\.venv\Scripts\pythonw.exe" (
  echo Portfolio Manager needs the existing Computer Bridge environment.
  echo Run apps\codex_desktop_assistant\Setup_Desktop_Assistant.cmd, then try again.
  pause
  exit /b 1
)
start "" /b "%PM_APP%\.venv\Scripts\pythonw.exe" "%PM_APP%\run.py" %*
