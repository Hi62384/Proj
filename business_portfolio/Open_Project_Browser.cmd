@echo off
setlocal
cd /d "%~dp0"
if errorlevel 1 goto directory_error
where python.exe >nul 2>nul
if not errorlevel 1 goto use_python
where py.exe >nul 2>nul
if not errorlevel 1 goto use_py
echo Python 3.10 or newer is required. No software was installed.
set "portfolio_exit=1"
goto finished
:use_python
python.exe "%~dp0tools\launch_browser.py"
set "portfolio_exit=%errorlevel%"
goto finished
:use_py
py.exe -3 "%~dp0tools\launch_browser.py"
set "portfolio_exit=%errorlevel%"
goto finished
:directory_error
echo The Business Portfolio folder could not be opened.
set "portfolio_exit=1"
:finished
if "%portfolio_exit%"=="0" goto success
echo.
echo Business Portfolio could not start. Read the error above.
echo Startup log, when available: "%~dp0.local\browser-startup.log"
pause
:success
exit /b %portfolio_exit%
