@echo off
setlocal
cd /d "%~dp0"

where node >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Node.js не найден в PATH.
  echo Установите Node.js и попробуйте снова.
  pause
  exit /b 1
)

echo Запуск roulette-сервера...
start "OBS Roulette Server" cmd /k "cd /d ""%~dp0"" && node server.mjs"

echo.
echo Сервер запущен.
echo В OBS используйте:
echo - Док-панель: http://127.0.0.1:8765/dock.html
echo - Browser Source: http://127.0.0.1:8765/overlay.html
echo.
echo Для остановки закройте окно "OBS Roulette Server".
pause
