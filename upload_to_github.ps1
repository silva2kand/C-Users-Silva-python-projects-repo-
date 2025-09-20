# GitHub Upload Script for Windows PowerShell
# Run this after creating your repository on GitHub

Write-Host "🚀 Setting up GitHub connection..." -ForegroundColor Green

# Prompt for GitHub username
$USERNAME = Read-Host "Enter your GitHub username"

# Add remote origin
Write-Host "📡 Adding GitHub remote..." -ForegroundColor Yellow
git remote add origin "https://github.com/$USERNAME/python-projects-repo.git"

# Verify remote
Write-Host "✅ Remote repository configured:" -ForegroundColor Green
git remote -v

# Push to GitHub
Write-Host "📤 Uploading to GitHub..." -ForegroundColor Yellow
git push -u origin master

# Final status
Write-Host "🎉 Repository uploaded successfully!" -ForegroundColor Green
Write-Host "🌐 View at: https://github.com/$USERNAME/python-projects-repo" -ForegroundColor Cyan
git status