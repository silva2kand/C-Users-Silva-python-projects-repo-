@echo off
REM PowerShell AI IDE Shortcut Launcher
REM Recreates the functionality of PowerShell AI IDE.lnk

title PowerShell AI IDE Shortcut Launcher
echo.
echo 🧠 PowerShell AI IDE Shortcut Launcher
echo ====================================
echo.

REM Check if PowerShell AI IDE directory exists
set "POWERSHELL_AI_IDE_LAUNCHER=C:\Users\Silva\ide\Launch_IDE.bat"
if not exist "%POWERSHELL_AI_IDE_LAUNCHER%" (
    echo ❌ PowerShell AI IDE launcher not found at: %POWERSHELL_AI_IDE_LAUNCHER%
    echo.
    echo Please ensure PowerShell AI IDE is installed or update the path in this script.
    echo.
    pause
    exit /b 1
)

echo ✅ Found PowerShell AI IDE launcher at: %POWERSHELL_AI_IDE_LAUNCHER%
echo.

echo 🎯 Launching PowerShell AI IDE...
echo.

REM Execute the PowerShell AI IDE launcher
call "%POWERSHELL_AI_IDE_LAUNCHER%"

echo.
echo 🏁 PowerShell AI IDE session completed.
pause