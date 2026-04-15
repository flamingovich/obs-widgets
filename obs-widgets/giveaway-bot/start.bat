@echo off
cd /d "%~dp0"
title OBS Roulette server.py
echo.
echo  ============================================================
echo   Starting server.py (API + static). Default port 58971.
echo   Old port 8787 is often used by: python -m http.server 8787
echo   That is a different server - /api/* will not work.
echo  ============================================================
echo.
python server.py
if errorlevel 1 pause
