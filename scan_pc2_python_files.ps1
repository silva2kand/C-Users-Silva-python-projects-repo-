# Python File Scanner for Second PC
# Run this script on your second PC to find all Python development files

Write-Host "🔍 Scanning Second PC for Python Files..." -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Yellow

# Get the current user's directory
$UserProfile = $env:USERPROFILE
$Username = $env:USERNAME

Write-Host "👤 Scanning user: $Username" -ForegroundColor Cyan
Write-Host "📁 User profile: $UserProfile" -ForegroundColor Cyan
Write-Host ""

# Comprehensive scan for Python files, excluding system directories
Write-Host "🔎 Finding all custom Python files..." -ForegroundColor Yellow

$PythonFiles = Get-ChildItem -Path $UserProfile -Include "*.py" -Recurse -ErrorAction SilentlyContinue | Where-Object {
    $_.FullName -notlike "*\.vscode*" -and
    $_.FullName -notlike "*\.windsurf*" -and 
    $_.FullName -notlike "*site-packages*" -and
    $_.FullName -notlike "*node_modules*" -and
    $_.FullName -notlike "*AppData\Local*" -and
    $_.FullName -notlike "*AppData\Roaming*" -and
    $_.FullName -notlike "*myenv*" -and
    $_.FullName -notlike "*\.env*" -and
    $_.Name -notlike "*test*" -and
    $_.Name -notlike "*__pycache__*"
}

Write-Host "📊 Found $($PythonFiles.Count) Python files" -ForegroundColor Green
Write-Host ""

# Group files by directory for better organization
$GroupedFiles = $PythonFiles | Group-Object {Split-Path $_.Directory -Leaf} | Sort-Object Name

Write-Host "📂 Files organized by directory:" -ForegroundColor Cyan
foreach ($Group in $GroupedFiles) {
    Write-Host "  📁 $($Group.Name): $($Group.Count) files" -ForegroundColor White
    foreach ($File in $Group.Group) {
        Write-Host "    📄 $($File.Name)" -ForegroundColor Gray
    }
    Write-Host ""
}

# Create a detailed report
$ReportPath = "$UserProfile\Desktop\PC2_Python_Files_Report.txt"
$ReportContent = @"
Python Files Scan Report - PC #2
Generated: $(Get-Date)
Username: $Username
Total Files Found: $($PythonFiles.Count)

Full File List:
===============
"@

foreach ($File in $PythonFiles) {
    $ReportContent += "$($File.FullName)`n"
}

$ReportContent | Out-File -FilePath $ReportPath -Encoding UTF8

Write-Host "📋 Detailed report saved to: $ReportPath" -ForegroundColor Green
Write-Host ""

# Suggest organization categories
Write-Host "🗂️ Suggested organization for GitHub repository:" -ForegroundColor Yellow
Write-Host "  • AI/ML Projects → documents-ai-collection/" -ForegroundColor White
Write-Host "  • Desktop Automation → desktop-ai-assistant/" -ForegroundColor White  
Write-Host "  • Development Tools → development-tools/" -ForegroundColor White
Write-Host "  • Web Services → hybrid-ai-services/" -ForegroundColor White
Write-Host "  • Computer Vision → hololens-cv-samples/" -ForegroundColor White
Write-Host "  • Agent Systems → legion/" -ForegroundColor White
Write-Host "  • Video Processing → video-ai-remaker/" -ForegroundColor White
Write-Host "  • Experimental Code → ai-experiments/" -ForegroundColor White
Write-Host "  • Demo Applications → demo-services/" -ForegroundColor White
Write-Host ""

Write-Host "✅ Scan complete! Review the files and organize them into your repository." -ForegroundColor Green
Write-Host "🚀 Repository URL: https://github.com/silva2kand/C-Users-Silva-python-projects-repo-" -ForegroundColor Cyan