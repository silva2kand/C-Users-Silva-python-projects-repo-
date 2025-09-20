@echo off
REM AI Assistant VBScript Launcher Shortcut
REM Recreates the functionality of AI_Assistant_Launcher.vbs

title AI Assistant Launcher
echo.
echo 🤖 AI Assistant Launcher
echo =====================
echo.

REM Check if AI Assistant files exist
set "AI_ASSISTANT_BAT=C:\Users\Silva\Desktop\Start_AI_Assistant.bat"
set "AI_ASSISTANT_PYTHON=C:\Users\Silva\Documents\desktop_ai_assistant_final.py"

if not exist "%AI_ASSISTANT_BAT%" (
    echo ❌ AI Assistant batch file not found at: %AI_ASSISTANT_BAT%
    echo.
    echo Trying to run Python file directly...
    
    if not exist "%AI_ASSISTANT_PYTHON%" (
        echo ❌ AI Assistant Python file not found at: %AI_ASSISTANT_PYTHON%
        echo.
        echo Please ensure AI Assistant is installed or update the paths in this script.
        echo.
        pause
        exit /b 1
    )
    
    echo ✅ Found AI Assistant Python file at: %AI_ASSISTANT_PYTHON%
    echo.
    echo 🎯 Launching AI Assistant directly...
    python "%AI_ASSISTANT_PYTHON%"
    
) else (
    echo ✅ Found AI Assistant batch launcher at: %AI_ASSISTANT_BAT%
    echo.
    echo 🎯 Launching AI Assistant via batch file...
    call "%AI_ASSISTANT_BAT%"
)

echo.
echo 🏁 AI Assistant session completed.
pause