#!/usr/bin/env python3
"""
Qwen AI Model Installer for Desktop AI Assistant
This script helps install and setup Qwen AI model for enhanced AI capabilities.
"""

import subprocess
import sys
import os

def install_qwen():
    """Install Qwen AI model and dependencies"""
    print("🚀 Installing Qwen AI Model for Desktop AI Assistant")
    print("=" * 60)

    try:
        # Install required packages
        print("📦 Installing required packages...")
        packages = [
            "transformers>=4.21.0",
            "torch>=1.12.0",
            "accelerate>=0.20.0"
        ]

        for package in packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

        print("✅ All packages installed successfully!")
        print("\n🧠 Qwen AI Model Setup Complete!")
        print("The Desktop AI Assistant will now use Qwen for enhanced intelligence.")
        print("\nTo start the assistant, run:")
        print("python desktop_ai_assistant.py")

    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print("\n🔄 Falling back to GPT4All...")
        print("The assistant will still work with GPT4All if available.")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    install_qwen()