@echo off
echo 🎬 Hybrid AI Video Remaker Pro v2.0
echo ====================================
echo Starting desktop GUI...
echo.

cd /d "%~dp0"

if exist desktop_video_remaker.py (
    python desktop_video_remaker.py
) else (
    echo Error: desktop_video_remaker.py not found!
    echo Please ensure the file is in the same directory as this script.
    pause
)