@echo off
setlocal
set "PORTFOLIO_PYTHON=%~dp0apps\codex_desktop_assistant\.venv\Scripts\python.exe"
if not exist "%PORTFOLIO_PYTHON%" (
  echo Portfolio Manager's Python environment was not found.
  pause
  exit /b 1
)
"%PORTFOLIO_PYTHON%" "%~dp0portfolio_manager\setup_session_hook.py" --install
set "PORTFOLIO_SETUP_RESULT=%ERRORLEVEL%"
pause
exit /b %PORTFOLIO_SETUP_RESULT%
