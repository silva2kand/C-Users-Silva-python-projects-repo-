@echo off
echo Starting Hybrid AI Video Remaker Web GUI...
echo.

cd /d %~dp0

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Install/update requirements
echo Installing/updating dependencies...
pip install -r requirements.txt

REM Check if Docker container is running
docker ps | findstr "lightweight-ai-container" >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Docker container 'lightweight-ai-container' not found running
    echo The web GUI will still work but AI chat features may be limited
    echo.
)

REM Start the web GUI
echo Starting Web GUI...
echo 🌐 Open your browser to: http://localhost:8001
echo 📱 Access the web interface for video processing!
python web_gui.py

pause