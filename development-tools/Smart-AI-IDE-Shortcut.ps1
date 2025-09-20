# Smart AI IDE Shortcut Launcher (PowerShell)
# Recreates the functionality of Smart AI IDE.lnk

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Smart AI IDE Shortcut Launcher" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Define Smart AI IDE directory
$smartAIIDEDir = "C:\Users\Silva\Documents\smart-ai-ide"
$fastLauncher = Join-Path $smartAIIDEDir "Smart-AI-IDE-FAST.bat"

# Check if directory exists
if (-not (Test-Path $smartAIIDEDir)) {
    Write-Host "❌ Smart AI IDE directory not found at: $smartAIIDEDir" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure Smart AI IDE is installed or update the path in this script." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Found Smart AI IDE at: $smartAIIDEDir" -ForegroundColor Green

# Check if fast launcher exists
if (-not (Test-Path $fastLauncher)) {
    Write-Host "❌ Fast launcher not found at: $fastLauncher" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Found fast launcher: $fastLauncher" -ForegroundColor Green
Write-Host ""

try {
    # Change to Smart AI IDE directory
    Set-Location $smartAIIDEDir
    Write-Host "🎯 Launching Smart AI IDE Fast Launcher..." -ForegroundColor Yellow
    Write-Host "Working directory: $(Get-Location)" -ForegroundColor Gray
    Write-Host ""
    
    # Execute the fast launcher
    & $fastLauncher
    
    Write-Host ""
    Write-Host "🏁 Smart AI IDE session completed." -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error launching Smart AI IDE: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
} finally {
    Read-Host "Press Enter to exit"
}