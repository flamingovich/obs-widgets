@echo off
chcp 65001 >nul
setlocal

echo ===============================================
echo  Stopping services on ports 5000 and 58971
echo ===============================================
echo.

for %%P in (5000 58971) do (
  for /f "tokens=5" %%A in ('netstat -ano ^| findstr ":%%P" ^| findstr "LISTENING"') do (
    echo Stopping PID %%A on port %%P...
    taskkill /PID %%A /F >nul 2>&1
  )
)

echo Done.
echo If any window is still open, close it with Ctrl+C.
echo.
pause
