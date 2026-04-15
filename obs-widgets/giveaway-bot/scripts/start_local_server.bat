@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo ===============================================
echo  Local server started for OBS Hybrid Roulette
echo  Folder: %CD%
echo  URL for wheel: http://localhost:58971/wheel.html
echo  URL for panel: http://localhost:58971/panel.html
echo  Stop server: Ctrl+C
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
