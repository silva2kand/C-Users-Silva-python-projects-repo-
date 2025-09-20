#!/bin/bash
# GitHub Upload Script
# Run this after creating your repository on GitHub

echo "🚀 Setting up GitHub connection..."

# Prompt for GitHub username
echo "Enter your GitHub username:"
read -r USERNAME

# Add remote origin
echo "📡 Adding GitHub remote..."
git remote add origin "https://github.com/$USERNAME/python-projects-repo.git"

# Verify remote
echo "✅ Remote repository configured:"
git remote -v

# Push to GitHub
echo "📤 Uploading to GitHub..."
git push -u origin master

# Final status
echo "🎉 Repository uploaded successfully!"
echo "🌐 View at: https://github.com/$USERNAME/python-projects-repo"
git status