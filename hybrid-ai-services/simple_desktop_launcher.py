#!/usr/bin/env python3
"""
Simple Desktop Video Remaker GUI Launcher
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

def check_display():
    """Check if display is available for GUI"""
    if platform.system() == "Windows":
        # On Windows, check if we're in a GUI environment
        try:
            import ctypes
            return ctypes.windll.user32.GetSystemMetrics(0) > 0
        except:
            return False
    else:
        # On Linux/Mac, check DISPLAY environment variable
        return os.environ.get('DISPLAY') is not None

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

def run_simple_gui():
    """Run a simple console-based interface"""
    print("\n🎬 Hybrid AI Video Remaker - Console Mode")
    print("=" * 50)

    while True:
        print("\nChoose an option:")
        print("1. 💬 Chat with AI")
        print("2. 📁 Upload Video (simulated)")
        print("3. ⚡ Process Video (simulated)")
        print("4. 👁️ Preview Video (simulated)")
        print("5. 🚪 Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            message = input("💬 Enter your message: ")
            print("🤖 AI: This is a simulated response. The full GUI would connect to the AI service.")

        elif choice == "2":
            video_path = input("📁 Enter video file path: ")
            if os.path.exists(video_path):
                print(f"✅ Video uploaded: {os.path.basename(video_path)}")
            else:
                print("❌ File not found")

        elif choice == "3":
            print("⚡ Processing video...")
            print("✅ Video processing completed!")

        elif choice == "4":
            print("👁️ Opening video preview...")
            print("📺 Preview would show here in the full GUI")

        elif choice == "5":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please try again.")

def main():
    print("🎬 Hybrid AI Video Remaker Desktop GUI Launcher")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check display availability
    if not check_display():
        print("⚠️  No display detected. Running in console mode...")
        run_simple_gui()
        return

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    print("\n🚀 Launching Desktop GUI...")
    print("💡 If the GUI doesn't appear, it may be running in the background")
    print("💡 Check your taskbar or system tray for the application")

    try:
        # Try to run the GUI
        subprocess.run([sys.executable, "desktop_gui.py"])
    except KeyboardInterrupt:
        print("\n👋 GUI closed by user")
    except Exception as e:
        print(f"❌ Error running GUI: {e}")
        print("💡 Try running in console mode instead")
        run_simple_gui()

if __name__ == "__main__":
    main()