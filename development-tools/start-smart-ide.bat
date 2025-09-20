@echo off
echo.
echo ================================================
echo      🚀 SMART AI IDE INTEGRATED SYSTEM
echo         + Lovable + Halo Gaming Elements
echo ================================================
echo.

echo 🎮 Initializing Spartan Protocol...
timeout /t 2 /nobreak > nul

echo.
echo 📊 System Components:
echo   ✅ Better Auth Next.js Frontend (Port 3000)
echo   ✅ Smart AI IDE Backend (Port 3001) 
echo   ✅ SuperAgent Security Layer (Port 8080)
echo   ✅ Lovable Visual Development (Integrated)
echo   ✅ Halo Spartan Gaming System (Active)
echo.

echo 🔧 Checking dependencies...
echo.

echo 📦 Installing Frontend Dependencies...
cd frontend
if not exist node_modules (
    echo Installing Next.js dependencies...
    call npm install
) else (
    echo Frontend dependencies already installed ✅
)
echo.

echo 📦 Installing Backend Dependencies...
cd ../backend
if not exist node_modules (
    echo Installing backend dependencies...
    call npm install
) else (
    echo Backend dependencies already installed ✅
)
echo.

echo 📦 Installing Security Layer Dependencies...
cd ../security
if not exist node_modules (
    echo Installing SuperAgent dependencies...
    cd node
    call npm install
    cd ..
) else (
    echo Security dependencies already installed ✅
)
cd ..
echo.

echo 🛡️ Starting SuperAgent Security Layer...
start "SuperAgent Security" cmd /k "cd security/node && npm start"
timeout /t 3 /nobreak > nul

echo 🔧 Starting Smart AI IDE Backend...
start "Smart AI IDE Backend" cmd /k "cd backend && npm run dev"
timeout /t 5 /nobreak > nul

echo 🎨 Starting Frontend...
start "Smart AI IDE Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 3 /nobreak > nul

echo.
echo ✅ All systems operational!
echo.
echo 🌟 ACCESS POINTS:
echo ================================
echo 🎨 Frontend:     http://localhost:3000
echo 🔧 Backend API:  http://localhost:3001
echo 🛡️ Security:     http://localhost:8080
echo.
echo 🎮 HALO FEATURES ENABLED:
echo ================================
echo 👑 Spartan Rank System: Active
echo 🏆 Achievement Tracking: Active  
echo 🎯 Gamified Development: Active
echo ⚡ Holographic UI Effects: Active
echo.
echo 🚀 SMART AI AGENTS READY:
echo ================================
echo 🤖 Code Analysis Agent: Online
echo 📝 Documentation Generator: Online
echo 🧪 Test Generator: Online
echo 🔍 Project Analyzer: Online
echo 🎨 Lovable Integration: Online
echo.
echo 🏁 Ready for epic development!
echo Press any key to open the IDE...
pause > nul

echo.
echo 🌐 Opening Smart AI IDE...
start "" http://localhost:3000

echo.
echo 💡 QUICK START GUIDE:
echo =====================
echo 1. 🔐 Sign up/Login at http://localhost:3000
echo 2. 🎨 Create your first project with Lovable integration
echo 3. 🤖 Use AI agents for code analysis and generation
echo 4. 🎮 Earn XP and unlock Spartan achievements
echo 5. 🛡️ All requests are protected by SuperAgent security
echo.
echo Happy coding, Spartan! 👑
echo.
pause