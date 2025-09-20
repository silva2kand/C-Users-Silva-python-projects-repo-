@echo off
REM Smart AI IDE Shortcut Launcher
REM Recreates the functionality of Smart AI IDE.lnk

title Smart AI IDE Shortcut Launcher
echo.
echo 🚀 Smart AI IDE Shortcut Launcher
echo ================================
echo.

REM Check if Smart AI IDE directory exists
set "SMART_AI_IDE_DIR=C:\Users\Silva\Documents\smart-ai-ide"
if not exist "%SMART_AI_IDE_DIR%" (
    echo ❌ Smart AI IDE directory not found at: %SMART_AI_IDE_DIR%
    echo.
    echo Please ensure Smart AI IDE is installed or update the path in this script.
    echo.
    pause
    exit /b 1
)

echo ✅ Found Smart AI IDE at: %SMART_AI_IDE_DIR%
echo.

REM Change to Smart AI IDE directory
cd /d "%SMART_AI_IDE_DIR%"

echo 🎯 Launching Smart AI IDE Fast Launcher...
echo.

REM Execute the Smart AI IDE fast launcher
call "%SMART_AI_IDE_DIR%\Smart-AI-IDE-FAST.bat"

echo.
echo 🏁 Smart AI IDE session completed.
pause