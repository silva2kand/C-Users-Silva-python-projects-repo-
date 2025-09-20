# Smart AI IDE Services Startup Script
Write-Host "Starting Smart AI IDE Services..." -ForegroundColor Green

# Function to start a service in a new PowerShell window
function Start-ServiceInNewWindow {
    param(
        [string]$ServiceName,
        [string]$Directory,
        [string]$Command,
        [string]$Color
    )
    
    Write-Host "Starting $ServiceName..." -ForegroundColor $Color
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Directory'; $Command"
}

# Start Backend (Port 3001)
Start-ServiceInNewWindow -ServiceName "Backend Service" -Directory "C:\Users\Silva\Desktop\smart-ai-ide-integrated\backend" -Command "npm run dev" -Color "Blue"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start Frontend (Port 3000)
Start-ServiceInNewWindow -ServiceName "Frontend Service" -Directory "C:\Users\Silva\Desktop\smart-ai-ide-integrated\frontend" -Command "pnpm dev" -Color "Green"

# Wait a moment
Start-Sleep -Seconds 2

# Start Security Service (Port varies)
Start-ServiceInNewWindow -ServiceName "Security Service" -Directory "C:\Users\Silva\Desktop\smart-ai-ide-integrated\security\node" -Command "npm start" -Color "Yellow"

Write-Host "`nAll services are starting up!" -ForegroundColor Cyan
Write-Host "- Backend: http://localhost:3001" -ForegroundColor Blue
Write-Host "- Frontend: http://localhost:3000" -ForegroundColor Green  
Write-Host "- Security service is running in background" -ForegroundColor Yellow
Write-Host "`nPress any key to continue..." -ForegroundColor Gray
Read-Host