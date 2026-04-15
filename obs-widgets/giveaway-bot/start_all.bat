@echo off
chcp 65001 >nul
cd /d "%~dp0"
setlocal

echo ============================================================
echo  Starting BOTH services:
echo   1) Giveaway Bot  - http://127.0.0.1:5000
echo   2) Wheel Server  - http://127.0.0.1:58971
echo ============================================================
echo.
echo Close each window with Ctrl+C when finished.
echo.

start "Giveaway Bot (5000)" /D "%~dp0giveaway_bot" cmd /k start_giveaway_bot.bat
start "Wheel Server (58971)" /D "%~dp0" cmd /k start.bat

echo Launched.
echo Giveaway admin:      http://127.0.0.1:5000
echo Wheel integration:   http://127.0.0.1:5000/wheel-integration
echo Wheel panel:         http://127.0.0.1:58971/panel.html
echo Wheel widget:        http://127.0.0.1:58971/wheel.html
echo.
pause

