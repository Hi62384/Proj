@echo off
setlocal
cd /d "%~dp0.."
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -m portfolio_autopilot.codex_relay serve %*
    goto finished
)
where python >nul 2>nul
if not errorlevel 1 (
    python -m portfolio_autopilot.codex_relay serve %*
    goto finished
)
echo Python 3.11 or later is required. Install Python from python.org.
:finished
if errorlevel 1 (
    echo.
    echo Relay stopped with an error. Review the message above.
    pause
)
endlocal
