# Python File Organizer for Second PC
# Use this script to organize found Python files into the repository structure

param(
    [Parameter(Mandatory=$true)]
    [string]$SourcePath,
    [Parameter(Mandatory=$true)]
    [string]$TargetCategory
)

Write-Host "🗂️ Python File Organizer for Repository" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Yellow

# Define valid categories
$ValidCategories = @{
    "legion" = "Legion AI Agent Swarm"
    "documents-ai-collection" = "Documents AI Collection"
    "development-tools" = "Development Tools"
    "hybrid-ai-services" = "Hybrid AI Services"
    "hololens-cv-samples" = "HoloLens CV Samples"
    "ai-mouse-bot" = "AI Mouse Bot"
    "video-ai-remaker" = "Video AI Remaker"
    "desktop-ai-assistant" = "Desktop AI Assistant"
    "demo-services" = "Demo Services"
    "ai-experiments" = "AI Experiments"
    "additional-backups" = "Additional Backups"
    "desktop-projects" = "Desktop Projects"
    "ide-core-system" = "IDE Core System"
}

# Validate category
if (-not $ValidCategories.ContainsKey($TargetCategory)) {
    Write-Host "❌ Invalid category. Valid options:" -ForegroundColor Red
    foreach ($Cat in $ValidCategories.Keys) {
        Write-Host "  • $Cat ($($ValidCategories[$Cat]))" -ForegroundColor White
    }
    exit 1
}

# Check if source exists
if (-not (Test-Path $SourcePath)) {
    Write-Host "❌ Source path not found: $SourcePath" -ForegroundColor Red
    exit 1
}

# Create target directory if it doesn't exist
$TargetDir = Join-Path (Get-Location) $TargetCategory
if (-not (Test-Path $TargetDir)) {
    New-Item -Path $TargetDir -ItemType Directory -Force | Out-Null
    Write-Host "📁 Created directory: $TargetCategory" -ForegroundColor Green
}

# Copy files
if (Test-Path $SourcePath -PathType Container) {
    # Copy entire directory
    $DirName = Split-Path $SourcePath -Leaf
    $FinalTarget = Join-Path $TargetDir $DirName
    Copy-Item -Path $SourcePath -Destination $FinalTarget -Recurse -Force
    Write-Host "📂 Copied directory: $DirName → $TargetCategory/" -ForegroundColor Green
} else {
    # Copy single file
    $FileName = Split-Path $SourcePath -Leaf
    $FinalTarget = Join-Path $TargetDir $FileName
    Copy-Item -Path $SourcePath -Destination $FinalTarget -Force
    Write-Host "📄 Copied file: $FileName → $TargetCategory/" -ForegroundColor Green
}

Write-Host "✅ File organization complete!" -ForegroundColor Green
Write-Host "💡 Next steps:" -ForegroundColor Yellow
Write-Host "  1. git add ." -ForegroundColor White
Write-Host "  2. git commit -m 'Add files from PC #2'" -ForegroundColor White
Write-Host "  3. git push origin master" -ForegroundColor White