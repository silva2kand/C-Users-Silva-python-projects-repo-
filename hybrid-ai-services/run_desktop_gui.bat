@echo off
echo Starting Hybrid AI Video Remaker Desktop GUI...
echo Make sure the Docker container is running on http://localhost:8000
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
    echo Please start the container first with:
    echo docker run -d -p 8000:8000 --name lightweight-ai-container lightweight-ai
    echo.
    echo Continuing anyway...
)

REM Start the desktop GUI
echo Starting Desktop GUI...
python desktop_gui.py

pause