@echo off
setlocal
cd /d "%~dp0\.."
echo Starting the local-only Portfolio Autopilot. No paid services or external accounts are used.
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -m portfolio_autopilot.factory.cli init
    if errorlevel 1 goto failed
    py -3 -m portfolio_autopilot.factory.cli serve
) else (
    where python >nul 2>nul
    if errorlevel 1 goto missing
    python -m portfolio_autopilot.factory.cli init
    if errorlevel 1 goto failed
    python -m portfolio_autopilot.factory.cli serve
)
if errorlevel 1 goto failed
exit /b 0
:missing
echo Python 3.10 or newer is required. Install Python from the official python.org website if necessary.
pause
exit /b 1
:failed
echo Portfolio Autopilot did not start. Review the message above.
pause
exit /b 1
