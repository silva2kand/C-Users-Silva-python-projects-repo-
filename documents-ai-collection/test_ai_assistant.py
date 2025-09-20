#!/usr/bin/env python3
"""
Simple Test Version of Desktop AI Assistant
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QLineEdit, QLabel)
from PyQt5.QtCore import Qt

class TestAI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test AI Assistant")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Test message...")
        self.message_input.returnPressed.connect(self.test_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.test_message)

        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        # Status
        self.status_label = QLabel("Test Mode - Basic Functions Only")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # Welcome message
        self.add_message("Test AI", "🤖 Test Assistant Ready!\n\nBasic functions working:\n• Text input/output\n• Button clicks\n• Window display\n\nTry typing a message!")

    def test_message(self):
        message = self.message_input.text().strip()
        if not message:
            return

        self.add_message("You", message)
        self.message_input.clear()

        # Simple response
        if message.lower() in ['hello', 'hi', 'hey']:
            response = "👋 Hello! Test mode is working!"
        elif 'help' in message.lower():
            response = "🆘 Test Help:\n• Type any message\n• Click Send button\n• Basic GUI functions work"
        else:
            response = f"📝 You said: '{message}'\n\n✅ GUI and input working perfectly!"

        self.add_message("Test AI", response)

    def add_message(self, sender, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.append(f"[{timestamp}] <b>{sender}:</b> {message}")
        self.chat_display.append("")

def main():
    app = QApplication(sys.argv)
    test_ai = TestAI()
    test_ai.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()