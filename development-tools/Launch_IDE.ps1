# PowerShell AI IDE Launcher
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   PowerShell AI IDE Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if the IDE file exists
$idePath = "C:\Users\Silva\ide\GUI\MainWindow.ps1"
if (-not (Test-Path $idePath)) {
    Write-Host "ERROR: IDE file not found at $idePath" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting PowerShell AI IDE..." -ForegroundColor Green
Write-Host "File location: $idePath" -ForegroundColor Gray
Write-Host ""

try {
    # Change to IDE directory
    Set-Location "C:\Users\Silva\ide"

    # Launch the IDE
    & $idePath
}
catch {
    Write-Host "ERROR: Failed to launch IDE - $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "IDE session ended. Press Enter to exit..." -ForegroundColor Yellow
Read-Host