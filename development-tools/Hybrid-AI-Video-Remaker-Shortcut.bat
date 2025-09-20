@echo off
REM Hybrid AI Video Remaker Shortcut Launcher
REM Recreates the functionality of Hybrid AI Video Remaker.lnk

title Hybrid AI Video Remaker Shortcut Launcher
color 0D
echo.
echo 🎬 Hybrid AI Video Remaker Shortcut Launcher
echo ==========================================
echo.

REM Check if Hybrid AI Video Remaker directory exists
set "VIDEO_AI_LAUNCHER=C:\Users\Silva\hybrid_ai_video_remaker\Launch_Video_AI.ps1"
if not exist "%VIDEO_AI_LAUNCHER%" (
    echo ❌ Hybrid AI Video Remaker launcher not found at: %VIDEO_AI_LAUNCHER%
    echo.
    echo Please ensure Hybrid AI Video Remaker is installed or update the path in this script.
    echo.
    pause
    exit /b 1
)

echo ✅ Found Hybrid AI Video Remaker launcher at: %VIDEO_AI_LAUNCHER%
echo.

echo 🎯 Launching Hybrid AI Video Remaker...
echo.

REM Execute the Hybrid AI Video Remaker launcher (with execution policy bypass)
powershell -ExecutionPolicy Bypass -File "%VIDEO_AI_LAUNCHER%"

echo.
echo 🏁 Hybrid AI Video Remaker session completed.
pause