@echo off
title Smart AI IDE - All-in-One Launcher
color 0B

echo.
echo  ████████╗ ███╗   ███╗ █████╗ ██████╗ ████████╗     █████╗ ██╗    ██╗██████╗ ██╗
echo  ╚══██╔══╝ ████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝    ██╔══██╗██║    ██║██╔══██╗██║
echo     ██║    ██╔████╔██║███████║██████╔╝   ██║       ███████║██║    ██║██║  ██║██║
echo     ██║    ██║╚██╔╝██║██╔══██║██╔══██╗   ██║       ██╔══██║██║    ██║██║  ██║██║
echo     ██║    ██║ ╚═╝ ██║██║  ██║██║  ██║   ██║       ██║  ██║██║    ██║██████╔╝██║
echo     ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═╝  ╚═╝╚═╝    ╚═╝╚═════╝ ╚═╝
echo.
echo                    🤖 SMART AI IDE - NATURAL LANGUAGE DEVELOPMENT 🤖
echo                    ====================================================
echo.

cd /d "%~dp0"

echo [1/4] 🔧 Checking system requirements...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found! Please install Node.js first.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version 2^>nul') do set NODE_VERSION=%%i
echo     ✅ Node.js detected: %NODE_VERSION%

if not exist "package.json" (
    echo ❌ package.json not found! Please run from project directory.
    pause
    exit /b 1
)

echo     ✅ Project directory validated

echo.
echo [2/4] 📦 Installing dependencies (if needed)...
if not exist "node_modules" (
    echo     Installing npm packages...
    call npm install --silent
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo     ✅ Dependencies installed successfully
) else (
    echo     ✅ Dependencies already installed
)

echo.
echo [3/4] 🚀 Starting Smart AI IDE services...

rem Kill any existing processes on our ports
echo     Cleaning up any existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3001 "') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173 "') do taskkill /f /pid %%a >nul 2>&1

echo     ✅ Ports cleared

rem Start backend server in background
echo     🔗 Starting backend server (port 3001)...
start /b "AI-Backend" cmd /c "npm run dev:backend >backend.log 2>&1"

rem Wait for backend
timeout /t 5 /nobreak >nul
echo     ✅ Backend server started

rem Start frontend server in background  
echo     🎨 Starting frontend server (port 5173)...
start /b "AI-Frontend" cmd /c "npm run dev:frontend >frontend.log 2>&1"

rem Wait for frontend
timeout /t 8 /nobreak >nul
echo     ✅ Frontend server started

rem Start AI Agent in background
echo     🤖 Starting AI Development Agent...
if exist "ai-developer.js" (
    start /b "AI-Agent" cmd /c "node ai-developer.js >ai-agent.log 2>&1"
    echo     ✅ AI Agent started
) else (
    echo     ⚠️  AI Agent file not found, continuing without it
)

echo.
echo [4/4] 💻 Launching Desktop GUI...

rem Get full path to HTML file
set "htmlFile=%~dp0desktop-ai-ide.html"

rem Try different browsers in order of preference
echo     Trying Microsoft Edge (app mode)...
start "" "msedge" "--app=file:///%htmlFile%" --window-size=1400,900 --disable-web-security >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✅ Launched in Microsoft Edge
    goto :success
)

echo     Trying Google Chrome (app mode)...
start "" "chrome" "--app=file:///%htmlFile%" --window-size=1400,900 --disable-web-security >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✅ Launched in Google Chrome
    goto :success
)

echo     Trying default browser...
start "" "%htmlFile%" >nul 2>&1
echo     ✅ Launched in default browser

:success
echo.
echo  ███████╗██╗   ██╗ ██████╗ ██████╗███████╗███████╗███████╗██╗
echo  ██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝██║
echo  ███████╗██║   ██║██║     ██║     █████╗  ███████╗███████╗██║
echo  ╚════██║██║   ██║██║     ██║     ██╔══╝  ╚════██║╚════██║╚═╝
echo  ███████║╚██████╔╝╚██████╗╚██████╗███████╗███████║███████║██╗
echo  ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝╚═╝
echo.
echo  🎉 SMART AI IDE IS NOW RUNNING!
echo  ===============================
echo.
echo  📍 Services Status:
echo     • Backend API:      http://localhost:3001  ✅
echo     • Frontend App:     http://localhost:5173  ✅  
echo     • AI Agent:         Ready for commands     🤖
echo     • Desktop GUI:      Launched              💻
echo.
echo  💡 What you can do now:
echo     • Use natural language commands in the desktop GUI
echo     • "Create a login system with authentication"
echo     • "Build a REST API for products"
echo     • "Generate a React dashboard"
echo     • "Add comprehensive tests"
echo.
echo  ⚠️  IMPORTANT: Keep this window open to maintain services
echo     Press any key to shutdown all services...

pause >nul

echo.
echo 🧹 Shutting down Smart AI IDE services...

rem Kill the background processes
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im npm.exe >nul 2>&1

rem Clean up port processes
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3001 "') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173 "') do taskkill /f /pid %%a >nul 2>&1

echo ✅ All services stopped
echo 👋 Smart AI IDE shutdown complete!
timeout /t 3 /nobreak >nul