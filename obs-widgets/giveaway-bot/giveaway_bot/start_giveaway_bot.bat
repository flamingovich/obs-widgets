@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Giveaway Bot server.py

echo.
echo ===============================================
echo  Starting Giveaway Bot (Flask)
echo  Folder: %CD%
echo  URL: http://127.0.0.1:5000
echo  Stop: Ctrl+C
echo ===============================================
echo.

where python >nul 2>&1
if %errorlevel% equ 0 (
  python server.py
  goto :end
)

where py >nul 2>&1
if %errorlevel% equ 0 (
  py -3 server.py
  goto :end
)

echo [ERROR] Python not found. Install from https://www.python.org/
echo         During setup, enable "Add python.exe to PATH".
pause

:end
