@echo off
setlocal
cd /d "%~dp0.."
echo This installs the official Linux Codex runtime and Ubuntu sandbox packages in WSL2.
echo GitHub credentials and the Relay database stay on Windows.
echo The existing ChatGPT login will be reused in a private Linux directory.
choice /C YN /N /M "Approve WSL2 runtime setup? [Y/N] "
if errorlevel 2 exit /b 0
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -m portfolio_autopilot.codex_relay.wsl_setup --approve-installation
    goto finished
)
python -m portfolio_autopilot.codex_relay.wsl_setup --approve-installation
:finished
pause
endlocal
