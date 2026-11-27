@echo off
setlocal
set "APPDATA=%~dp0acceptance-user-data"
set "LOCALAPPDATA=%~dp0acceptance-user-data"
start "" "C:\Users\User1\Documents\Downloads\Proj\business_portfolio\.local\gdm-002-godot-compat\4.7.2\Godot_v4.7.2-stable_win64.exe" --path "%~dp0."
