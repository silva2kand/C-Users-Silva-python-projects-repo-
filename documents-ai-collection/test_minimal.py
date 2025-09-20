#!/usr/bin/env python3
"""
Minimal test version of Desktop AI Assistant
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QLineEdit, QLabel, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

class MinimalAI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal AI Test")
        self.setGeometry(100, 100, 400, 300)

        # Setup UI
        self.setup_ui()

        # Timer for testing
        self.timer = QTimer()
        self.timer.timeout.connect(self.test_message)
        self.timer.start(2000)  # 2 seconds

    def setup_ui(self):
        layout = QVBoxLayout()

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type something...")
        self.message_input.returnPressed.connect(self.process_message)
        input_layout.addWidget(self.message_input)

        self.send_button = QPushButton("SEND")
        self.send_button.clicked.connect(self.process_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

        # Welcome message
        self.add_message("AI", "Hello! This is a minimal test version.")

    def add_message(self, sender, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.append(f"[{timestamp}] {sender}: {message}")

    def test_message(self):
        self.add_message("System", "Test message - app is working!")

    def process_message(self):
        message = self.message_input.text().strip()
        if not message:
            return

        self.add_message("You", message)
        self.message_input.clear()

        # Simple response
        if "hello" in message.lower():
            response = "Hello! How can I help you?"
        elif "time" in message.lower():
            from datetime import datetime
            response = f"Current time: {datetime.now().strftime('%H:%M:%S')}"
        else:
            response = f"I heard: '{message}'. Try saying 'hello' or 'time'!"

        self.add_message("AI", response)

def main():
    app = QApplication(sys.argv)
    window = MinimalAI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()