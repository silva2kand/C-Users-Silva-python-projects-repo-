# Smart AI IDE Desktop Launcher
# Integrates natural language AI development with backend services

param(
    [switch]$ForceRestart,
    [switch]$NoAI
)

Write-Host "🤖 Smart AI IDE - Natural Language Development Platform" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$projectPath = $PSScriptRoot
$backendPort = 3001
$frontendPort = 5173
$aiAgentPath = Join-Path $projectPath "ai-developer.js"
$desktopGuiPath = Join-Path $projectPath "desktop-ai-ide.html"

# Function to check if port is in use
function Test-Port($port) {
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
        return $connection.TcpTestSucceeded
    } catch {
        return $false
    }
}

# Function to kill processes on specific ports
function Stop-ProcessOnPort($port) {
    try {
        $processes = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | 
                    Select-Object OwningProcess | 
                    ForEach-Object { Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue }
        
        foreach ($process in $processes) {
            Write-Host "Stopping process $($process.Name) (PID: $($process.Id)) on port $port" -ForegroundColor Yellow
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 2
    } catch {
        Write-Host "Could not stop processes on port $port" -ForegroundColor Red
    }
}

# Function to start backend server
function Start-BackendServer {
    Write-Host "🚀 Starting backend server..." -ForegroundColor Green
    
    if (Test-Port $backendPort) {
        if ($ForceRestart) {
            Write-Host "Restarting backend server on port $backendPort..." -ForegroundColor Yellow
            Stop-ProcessOnPort $backendPort
        } else {
            Write-Host "✅ Backend server already running on port $backendPort" -ForegroundColor Green
            return $true
        }
    }
    
    try {
        # Start the backend server
        $backendJob = Start-Job -ScriptBlock {
            param($path)
            Set-Location $path
            npm run start:backend 2>&1
        } -ArgumentList $projectPath
        
        Write-Host "Backend job started (ID: $($backendJob.Id))" -ForegroundColor Green
        
        # Wait for backend to be ready
        $timeout = 30
        $elapsed = 0
        while (-not (Test-Port $backendPort) -and $elapsed -lt $timeout) {
            Write-Host "Waiting for backend server... ($elapsed/$timeout seconds)" -ForegroundColor Yellow
            Start-Sleep -Seconds 2
            $elapsed += 2
        }
        
        if (Test-Port $backendPort) {
            Write-Host "✅ Backend server is ready on http://localhost:$backendPort" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Backend server failed to start within $timeout seconds" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Failed to start backend server: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to start frontend server
function Start-FrontendServer {
    Write-Host "🎨 Starting frontend server..." -ForegroundColor Green
    
    if (Test-Port $frontendPort) {
        if ($ForceRestart) {
            Write-Host "Restarting frontend server on port $frontendPort..." -ForegroundColor Yellow
            Stop-ProcessOnPort $frontendPort
        } else {
            Write-Host "✅ Frontend server already running on port $frontendPort" -ForegroundColor Green
            return $true
        }
    }
    
    try {
        # Start the frontend server
        $frontendJob = Start-Job -ScriptBlock {
            param($path, $port)
            Set-Location $path
            # Clear any Vite cache and start fresh
            if (Test-Path "node_modules/.vite") {
                Remove-Item -Recurse -Force "node_modules/.vite" -ErrorAction SilentlyContinue
            }
            npm run dev -- --port $port --host 0.0.0.0 2>&1
        } -ArgumentList $projectPath, $frontendPort
        
        Write-Host "Frontend job started (ID: $($frontendJob.Id))" -ForegroundColor Green
        
        # Wait for frontend to be ready
        $timeout = 45
        $elapsed = 0
        while (-not (Test-Port $frontendPort) -and $elapsed -lt $timeout) {
            Write-Host "Waiting for frontend server... ($elapsed/$timeout seconds)" -ForegroundColor Yellow
            Start-Sleep -Seconds 2
            $elapsed += 2
        }
        
        if (Test-Port $frontendPort) {
            Write-Host "✅ Frontend server is ready on http://localhost:$frontendPort" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Frontend server failed to start within $timeout seconds" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Failed to start frontend server: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to start AI Agent
function Start-AIAgent {
    if ($NoAI) {
        Write-Host "⚡ Skipping AI Agent startup (--NoAI flag)" -ForegroundColor Yellow
        return $true
    }
    
    Write-Host "🤖 Starting AI Development Agent..." -ForegroundColor Magenta
    
    if (-not (Test-Path $aiAgentPath)) {
        Write-Host "❌ AI Agent not found at: $aiAgentPath" -ForegroundColor Red
        return $false
    }
    
    try {
        # Start the AI Agent in background
        $aiJob = Start-Job -ScriptBlock {
            param($agentPath)
            Set-Location (Split-Path $agentPath -Parent)
            node $agentPath
        } -ArgumentList $aiAgentPath
        
        Write-Host "🤖 AI Agent started (Job ID: $($aiJob.Id))" -ForegroundColor Magenta
        Write-Host "   AI Agent is ready for natural language development commands!" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Failed to start AI Agent: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to launch desktop GUI
function Launch-DesktopGUI {
    Write-Host "💻 Launching Smart AI IDE Desktop Application..." -ForegroundColor Blue
    
    if (-not (Test-Path $desktopGuiPath)) {
        Write-Host "❌ Desktop GUI not found at: $desktopGuiPath" -ForegroundColor Red
        return $false
    }
    
    try {
        # Try different browsers for app mode
        $browsers = @(
            @{Name="Microsoft Edge"; Path="msedge"; Args="--app=file:///$($desktopGuiPath.Replace('\', '/')) --window-size=1400,900 --disable-web-security --allow-file-access-from-files"},
            @{Name="Google Chrome"; Path="chrome"; Args="--app=file:///$($desktopGuiPath.Replace('\', '/')) --window-size=1400,900 --disable-web-security --allow-file-access-from-files"},
            @{Name="Default Browser"; Path=""; Args=""}
        )
        
        foreach ($browser in $browsers) {
            try {
                if ($browser.Path -eq "") {
                    # Use default browser
                    Start-Process $desktopGuiPath
                    Write-Host "✅ Launched Smart AI IDE in default browser" -ForegroundColor Green
                    return $true
                } else {
                    # Try specific browser
                    $process = Start-Process -FilePath $browser.Path -ArgumentList $browser.Args -PassThru -ErrorAction Stop
                    Write-Host "✅ Launched Smart AI IDE in $($browser.Name) (PID: $($process.Id))" -ForegroundColor Green
                    return $true
                }
            } catch {
                Write-Host "⚠️  Could not launch in $($browser.Name): $($_.Exception.Message)" -ForegroundColor Yellow
                continue
            }
        }
        
        Write-Host "❌ Could not launch desktop GUI in any browser" -ForegroundColor Red
        return $false
    } catch {
        Write-Host "❌ Failed to launch desktop GUI: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to show system status
function Show-SystemStatus {
    Write-Host ""
    Write-Host "📊 Smart AI IDE System Status:" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    
    $backendStatus = if (Test-Port $backendPort) { "✅ Online" } else { "❌ Offline" }
    $frontendStatus = if (Test-Port $frontendPort) { "✅ Online" } else { "❌ Offline" }
    
    Write-Host "Backend Server (Port $backendPort):  $backendStatus" -ForegroundColor White
    Write-Host "Frontend Server (Port $frontendPort): $frontendStatus" -ForegroundColor White
    Write-Host "AI Agent:                           🤖 Ready" -ForegroundColor White
    Write-Host "Desktop GUI:                        💻 Launched" -ForegroundColor White
    
    Write-Host ""
    Write-Host "🎉 Smart AI IDE is ready for natural language development!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Available endpoints:" -ForegroundColor Yellow
    Write-Host "• Backend API:     http://localhost:$backendPort" -ForegroundColor White
    Write-Host "• Frontend App:    http://localhost:$frontendPort" -ForegroundColor White
    Write-Host "• Desktop GUI:     Launched in browser app mode" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Usage Examples:" -ForegroundColor Yellow
    Write-Host '• "Create a login system with JWT authentication"' -ForegroundColor White
    Write-Host '• "Build a REST API for managing products"' -ForegroundColor White
    Write-Host '• "Generate a React dashboard with charts"' -ForegroundColor White
    Write-Host '• "Add comprehensive tests to the project"' -ForegroundColor White
    Write-Host '• "Deploy the application to production"' -ForegroundColor White
}

# Main execution
try {
    # Check Node.js availability
    try {
        $nodeVersion = node --version 2>$null
        Write-Host "✅ Node.js detected: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Node.js not found. Please install Node.js first." -ForegroundColor Red
        exit 1
    }
    
    # Check if we're in the right directory
    if (-not (Test-Path "package.json")) {
        Write-Host "❌ package.json not found. Please run this script from the project root directory." -ForegroundColor Red
        exit 1
    }
    
    # Install dependencies if needed
    if (-not (Test-Path "node_modules")) {
        Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
        npm install
    }
    
    Write-Host "Starting Smart AI IDE components..." -ForegroundColor Cyan
    Write-Host ""
    
    # Start services in order
    $backendOk = Start-BackendServer
    $frontendOk = Start-FrontendServer
    $aiAgentOk = Start-AIAgent
    
    if ($backendOk -and $frontendOk -and $aiAgentOk) {
        # Launch desktop GUI
        $guiOk = Launch-DesktopGUI
        
        if ($guiOk) {
            Show-SystemStatus
            
            Write-Host "Press Ctrl+C to stop all services and exit." -ForegroundColor Yellow
            
            # Keep the script running
            try {
                while ($true) {
                    Start-Sleep -Seconds 10
                    
                    # Check if services are still running
                    if (-not (Test-Port $backendPort)) {
                        Write-Host "⚠️  Backend server stopped unexpectedly" -ForegroundColor Red
                    }
                    if (-not (Test-Port $frontendPort)) {
                        Write-Host "⚠️  Frontend server stopped unexpectedly" -ForegroundColor Red
                    }
                }
            } catch {
                Write-Host "`nShutting down Smart AI IDE..." -ForegroundColor Yellow
            }
        } else {
            Write-Host "❌ Failed to launch desktop GUI" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Failed to start required services" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
    
    # Stop background jobs
    Get-Job | Where-Object { $_.State -eq "Running" } | Stop-Job
    Get-Job | Remove-Job -Force
    
    Write-Host "✅ Smart AI IDE stopped." -ForegroundColor Green
}