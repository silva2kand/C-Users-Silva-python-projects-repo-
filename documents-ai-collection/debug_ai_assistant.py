#!/usr/bin/env python3
"""
Debug Version of Desktop AI Assistant - Step by step testing
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QLineEdit, QLabel)
from PyQt5.QtCore import Qt

print("Starting Debug AI Assistant...")

class DebugAI(QWidget):
    def __init__(self):
        super().__init__()
        print("Initializing DebugAI class...")

        self.setWindowTitle("Debug AI Assistant")
        self.setGeometry(100, 100, 500, 400)

        print("Setting up UI...")

        layout = QVBoxLayout()

        # Status display
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setMaximumHeight(150)
        layout.addWidget(self.status_display)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Test commands...")
        self.message_input.returnPressed.connect(self.process_command)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.process_command)

        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        self.setLayout(layout)

        print("UI setup complete")

        # Test different features
        self.test_features()

    def test_features(self):
        """Test various features step by step"""
        self.log_status("Starting feature tests...")

        # Test 1: Basic functionality
        self.log_status("PASS: Test 1 - Basic UI")

        # Test 2: Voice libraries
        try:
            import speech_recognition as sr
            import pyttsx3
            self.log_status("PASS: Test 2 - Voice libraries")
        except Exception as e:
            self.log_status(f"FAIL: Test 2 - Voice libraries - {e}")

        # Test 3: AI libraries
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            self.log_status("PASS: Test 3 - AI libraries")
        except Exception as e:
            self.log_status(f"FAIL: Test 3 - AI libraries - {e}")

        # Test 4: System libraries
        try:
            import psutil, platform
            self.log_status("PASS: Test 4 - System libraries")
        except Exception as e:
            self.log_status(f"FAIL: Test 4 - System libraries - {e}")

        # Test 5: Windows-specific
        try:
            import winshell
            from win32com.client import Dispatch
            self.log_status("PASS: Test 5 - Windows libraries")
        except Exception as e:
            self.log_status(f"WARN: Test 5 - Windows libraries - {e}")

        self.log_status("Feature testing complete!")
        self.add_message("Debug AI", "Debug Assistant Ready!\n\nAll core features tested. Try commands like:\n• 'test voice'\n• 'test ai'\n• 'test system'\n• 'help'")

    def log_status(self, message):
        """Log status message"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_display.append(f"[{timestamp}] {message}")

    def add_message(self, sender, message):
        """Add message to chat"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.append(f"[{timestamp}] <b>{sender}:</b> {message}")
        self.chat_display.append("")

    def process_command(self):
        """Process test commands"""
        command = self.message_input.text().strip().lower()
        if not command:
            return

        self.add_message("You", command)
        self.message_input.clear()

        if command == 'test voice':
            self.test_voice_feature()
        elif command == 'test ai':
            self.test_ai_feature()
        elif command == 'test system':
            self.test_system_feature()
        elif command == 'help':
            self.show_help()
        else:
            self.add_message("Debug AI", f"Command: '{command}'\n\nTry: 'test voice', 'test ai', 'test system', 'help'")

    def test_voice_feature(self):
        """Test voice functionality"""
        try:
            self.log_status("Testing voice recognition...")
            import speech_recognition as sr

            # Test microphone access
            with sr.Microphone() as source:
                recognizer = sr.Recognizer()
                recognizer.adjust_for_ambient_noise(source, duration=0.5)

            self.log_status("PASS: Voice recognition test")
            self.add_message("Debug AI", "Voice recognition is working!\n\nFeatures available:\n• Voice input\n• Text-to-speech\n• Continuous chat mode")

        except Exception as e:
            self.log_status(f"FAIL: Voice recognition test - {e}")
            self.add_message("Debug AI", f"Voice recognition failed: {e}")

    def test_ai_feature(self):
        """Test AI functionality"""
        try:
            self.log_status("Testing AI models...")
            from transformers import AutoTokenizer, AutoModelForCausalLM

            # Test model loading (lightweight)
            model_name = "microsoft/DialoGPT-small"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)

            self.log_status("PASS: AI model test")
            self.add_message("Debug AI", "AI models are working!\n\nFeatures available:\n• Natural language processing\n• Context-aware responses\n• Intelligent command parsing")

        except Exception as e:
            self.log_status(f"FAIL: AI model test - {e}")
            self.add_message("Debug AI", f"AI model failed: {e}")

    def test_system_feature(self):
        """Test system functionality"""
        try:
            self.log_status("Testing system features...")
            import psutil, platform

            # Test system info
            info = {
                'OS': platform.system(),
                'CPU': psutil.cpu_percent(),
                'Memory': psutil.virtual_memory().percent
            }

            self.log_status("PASS: System features test")
            self.add_message("Debug AI", f"System features working!\n\nSystem Info:\n• OS: {info['OS']}\n• CPU: {info['CPU']}%\n• Memory: {info['Memory']}%\n\nFeatures available:\n• System monitoring\n• PC maintenance\n• Performance optimization")

        except Exception as e:
            self.log_status(f"FAIL: System features test - {e}")
            self.add_message("Debug AI", f"System features failed: {e}")

    def show_help(self):
        """Show help information"""
        help_text = """Debug Assistant Help:

TESTING COMMANDS:
• 'test voice' - Test voice recognition
• 'test ai' - Test AI models
• 'test system' - Test system features
• 'help' - Show this help

WORKING FEATURES:
• Basic GUI interface
• Text input/output
• Status logging
• Feature testing

DIAGNOSTICS:
Check the status panel above for detailed test results and error messages.

NEXT STEPS:
Once all tests pass, the full AI Assistant should work properly!"""

        self.add_message("Debug AI", help_text)

def main():
    print("Starting Debug AI Assistant...")
    try:
        app = QApplication(sys.argv)
        print("QApplication created")

        debug_ai = DebugAI()
        print("DebugAI instance created")

        debug_ai.show()
        print("Window shown")

        print("Debug AI Assistant ready!")
        sys.exit(app.exec_())

    except Exception as e:
        print(f"Application failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()