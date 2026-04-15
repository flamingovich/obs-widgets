@echo off
cd /d "%~dp0"
set "BRIDGE_PORT=8766"
if not exist "requirements.txt" (
  echo Нет requirements.txt в папке: %~dp0
  pause
  exit /b 1
)
python -m pip install -r requirements.txt
echo Starting likes bridge on http://127.0.0.1:%BRIDGE_PORT%
python likes_bridge.py --port %BRIDGE_PORT%
pause
