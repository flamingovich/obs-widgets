@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist "giveaway-bot" (
  echo [ERROR] Folder not found: giveaway-bot
  goto :fail
)
if not exist "random-slot-roulette" (
  echo [ERROR] Folder not found: random-slot-roulette
  goto :fail
)
if not exist "wallet-dep-withdraw" (
  echo [ERROR] Folder not found: wallet-dep-withdraw
  goto :fail
)

:menu
cls
echo ============================================================
echo                    OBS Widgets Launcher
echo ============================================================
echo.
echo   [1] Start Giveaway Bot
echo   [2] Start Random Slot Roulette
echo   [3] Start Wallet Bridge
echo   [4] Start all
echo   [0] Exit
echo.
set /p CHOICE=Choose option and press Enter: 
set "CHOICE=%CHOICE: =%"

if "%CHOICE%"=="1" goto :run_giveaway
if "%CHOICE%"=="2" goto :run_roulette
if "%CHOICE%"=="3" goto :run_wallet
if "%CHOICE%"=="4" goto :run_all
if "%CHOICE%"=="0" goto :eof

echo.
echo [WARN] Invalid choice: "%CHOICE%"
timeout /t 2 >nul
goto :menu

:run_giveaway
echo.
echo Starting Giveaway Bot...
if exist "giveaway-bot\start_local_server.bat" (
  start "Giveaway Bot (5000)" cmd /k "cd /d ""%~dp0giveaway-bot"" && call start_local_server.bat"
) else (
  echo [ERROR] File not found: giveaway-bot\start_local_server.bat
)
goto :done_single

:run_roulette
echo.
echo Starting Random Slot Roulette...
if exist "random-slot-roulette\start.bat" (
  start "Random Slot Roulette (8765)" cmd /k "cd /d ""%~dp0random-slot-roulette"" && call start.bat"
) else (
  echo [ERROR] File not found: random-slot-roulette\start.bat
)
goto :done_single

:run_wallet
echo.
echo Starting Wallet Bridge...
if exist "wallet-dep-withdraw\run_bridge.bat" (
  start "Wallet Bridge (8766)" cmd /k "cd /d ""%~dp0wallet-dep-withdraw"" && call run_bridge.bat"
) else (
  echo [ERROR] File not found: wallet-dep-withdraw\run_bridge.bat
)
goto :done_single

:run_all
echo.
echo Starting all services...
echo.
if exist "giveaway-bot\start_local_server.bat" (
  start "Giveaway Bot (5000)" cmd /k "cd /d ""%~dp0giveaway-bot"" && call start_local_server.bat"
) else (
  echo [ERROR] File not found: giveaway-bot\start_local_server.bat
)

if exist "random-slot-roulette\start.bat" (
  start "Random Slot Roulette (8765)" cmd /k "cd /d ""%~dp0random-slot-roulette"" && call start.bat"
) else (
  echo [ERROR] File not found: random-slot-roulette\start.bat
)

if exist "wallet-dep-withdraw\run_bridge.bat" (
  start "Wallet Bridge (8766)" cmd /k "cd /d ""%~dp0wallet-dep-withdraw"" && call run_bridge.bat"
) else (
  echo [ERROR] File not found: wallet-dep-withdraw\run_bridge.bat
)

echo.
echo [OK] No port conflict by default:
echo      Roulette  -> 8765
echo      Wallet    -> 8766
goto :done_single

:done_single
echo.
echo Done. Press any key to return to menu...
pause >nul
goto :menu

:fail
echo.
echo Press any key to exit...
pause >nul
exit /b 1
