# Hybrid AI Video Remaker Launcher
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "   Hybrid AI Video Remaker" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "video_remaker.py")) {
    Set-Location "C:\Users\Silva\hybrid_ai_video_remaker"
}

# Check for Python dependencies
if (Test-Path "requirements.txt") {
    Write-Host "Checking dependencies..." -ForegroundColor Yellow
    # You might want to activate a virtual environment here if you have one
}

Write-Host "Starting Hybrid AI Video Remaker..." -ForegroundColor Green
Write-Host "Features: File processing, Video streaming, AI generation" -ForegroundColor Gray
Write-Host ""

try {
    # Launch the main video remaker
    python video_remaker.py
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure Python is installed and dependencies are met." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Video AI session ended." -ForegroundColor Yellow
pause