@echo off
cd /d "%~dp0"
if not exist "requirements.txt" (
  echo Нет requirements.txt в папке: %~dp0
  pause
  exit /b 1
)
python -m pip install -r requirements.txt
python likes_bridge.py
pause
