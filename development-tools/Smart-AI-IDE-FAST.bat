@echo off
title Smart AI IDE - FAST LAUNCHER
color 0B

echo.
echo  ████████╗ ███╗   ███╗ █████╗ ██████╗ ████████╗     █████╗ ██╗
echo  ╚══██╔══╝ ████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝    ██╔══██╗██║
echo     ██║    ██╔████╔██║███████║██████╔╝   ██║       ███████║██║
echo     ██║    ██║╚██╔╝██║██╔══██║██╔══██╗   ██║       ██╔══██║██║
echo     ██║    ██║ ╚═╝ ██║██║  ██║██║  ██║   ██║       ██║  ██║██║
echo     ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═╝  ╚═╝╚═╝
echo.
echo                🚀 SMART AI IDE - FAST LAUNCHER 🚀
echo                =====================================
echo.

cd /d "%~dp0"

echo ⚡ FAST MODE - Skipping dependency checks...
echo.

echo [1/2] 🧹 Cleaning up ports...
rem Kill any processes on our ports
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":3001 "') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":5173 "') do taskkill /f /pid %%a >nul 2>&1
echo     ✅ Ports cleared

echo.
echo [2/2] 🚀 Launching Smart AI IDE...

rem Start Multi-API AI Agent immediately 
echo     🤖 Starting Multi-API AI Development Agent...
if exist "ai-agent-multi-api.js" (
    start /min "Multi-API-Agent" cmd /c "node ai-agent-multi-api.js"
    echo     ✅ Multi-API Agent started (5 APIs available)
) else if exist "ai-developer.js" (
    start /min "AI-Agent" cmd /c "node ai-developer.js"
    echo     ✅ Basic AI Agent started
) else (
    echo     ⚠️  AI Agent files not found, continuing...
)

rem Launch Conversational AI Desktop GUI immediately
echo     💻 Launching Conversational AI Assistant...
set "htmlFile=%~dp0conversational-ai-ide.html"

rem Try Edge first (fastest)
start "" "msedge" "--app=file:///%htmlFile%" --window-size=1400,900 >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✅ Desktop GUI launched in Microsoft Edge
) else (
    rem Try Chrome backup
    start "" "chrome" "--app=file:///%htmlFile%" --window-size=1400,900 >nul 2>&1
    if %errorlevel% equ 0 (
        echo     ✅ Desktop GUI launched in Chrome
    ) else (
        rem Use default browser
        start "" "%htmlFile%"
        echo     ✅ Desktop GUI launched in default browser
    )
)

echo.
echo  ███████╗ █████╗ ███████╗████████╗    ██╗      █████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗
echo  ██╔════╝██╔══██╗██╔════╝╚══██╔══╝    ██║     ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║
echo  █████╗  ███████║███████╗   ██║       ██║     ███████║██║   ██║██╔██╗ ██║██║     ███████║
echo  ██╔══╝  ██╔══██║╚════██║   ██║       ██║     ██╔══██║██║   ██║██║╚██╗██║██║     ██╔══██║
echo  ██║     ██║  ██║███████║   ██║       ███████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║
echo  ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝       ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝
echo.
echo  🎉 SMART AI IDE LAUNCHED IN FAST MODE!
echo  =====================================
echo.
echo  💬 Conversational AI: Chat naturally and speak with voice!
echo  🤖 Multi-API Agent: 5 free tier APIs with auto-switching!
echo  🔍 Auto-Fix Agent: Validates and fixes code until 100%% perfect!
echo.
echo  💡 Try these commands in the GUI:
echo     • "Create a login system with authentication"
echo     • "Build a REST API for products"  
echo     • "Generate a React dashboard"
echo     • "Add comprehensive tests"
echo.
echo  ✨ NEW FEATURES:
echo     • Auto-switches between 5 free AI APIs
echo     • Automatically validates and fixes all generated code
echo     • Ensures 100%% working, production-ready files
echo     • Never get stuck with broken code again!
echo.
echo  ⚡ FAST MODE: Backend/frontend servers are optional
echo     The desktop GUI works standalone with AI simulation
echo.
echo  🔧 Want full servers? Run: npm run dev
echo.
echo  Press any key to exit...
pause >nul

echo.
echo 🧹 Cleaning up...
taskkill /f /im node.exe >nul 2>&1
echo ✅ Fast launcher complete!
timeout /t 2 /nobreak >nul