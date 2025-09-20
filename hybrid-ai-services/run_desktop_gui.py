#!/usr/bin/env python3
"""
Hybrid AI Video Remaker Desktop GUI Launcher
"""

import sys
import os
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_docker_container():
    """Check if the Docker container is running"""
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "lightweight-ai-container" in result.stdout:
            print("✅ Docker container is running")
            return True
        else:
            print("⚠️  Warning: Docker container 'lightweight-ai-container' not found")
            print("Please start it with:")
            print("docker run -d -p 8000:8000 --name lightweight-ai-container lightweight-ai")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  Warning: Could not check Docker status")
        return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing/updating dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_gui():
    """Launch the desktop GUI"""
    print("🚀 Starting Hybrid AI Video Remaker Desktop GUI...")
    try:
        subprocess.run([sys.executable, "desktop_gui.py"])
    except KeyboardInterrupt:
        print("\n👋 GUI closed by user")
    except Exception as e:
        print(f"❌ Error running GUI: {e}")

def main():
    print("🎬 Hybrid AI Video Remaker Desktop GUI Launcher")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check Docker container
    check_docker_container()

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    print("\n" + "=" * 50)
    print("🎯 Desktop GUI Features:")
    print("  • AI Chat Assistant")
    print("  • Video File Selection")
    print("  • Processing Options (Format, Quality, Effects)")
    print("  • Real-time Progress")
    print("  • Settings Management")
    print("=" * 50)

    # Run the GUI
    run_gui()

if __name__ == "__main__":
    main()