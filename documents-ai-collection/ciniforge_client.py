#!/usr/bin/env python3
"""
Ciniforge Client - Lightweight
Connects to the centralized AI API server for video creation assistance
"""

import sys
import os
import time
import threading
import requests
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QPushButton, QLineEdit, QLabel, QScrollArea,
                             QApplication, QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor

class FloatingChatIcon(QWidget):
    """Floating chat icon that can be clicked to open full chat"""
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setFixedSize(60, 60)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Position in bottom right corner
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 80, screen.height() - 140)

        # Create circular icon
        self.setStyleSheet("""
            FloatingChatIcon {
                background-color: #0078d4;
                border-radius: 30px;
                border: 3px solid #ffffff;
            }
        """)

        # Add chat icon label
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        chat_label = QLabel("🎬")
        chat_label.setAlignment(Qt.AlignCenter)
        chat_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(chat_label)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def enterEvent(self, event):
        self.setStyleSheet("""
            FloatingChatIcon {
                background-color: #106ebe;
                border-radius: 30px;
                border: 3px solid #ffffff;
            }
        """)

    def leaveEvent(self, event):
        self.setStyleSheet("""
            FloatingChatIcon {
                background-color: #0078d4;
                border-radius: 30px;
                border: 3px solid #ffffff;
            }
        """)

class CiniforgeClient(QWidget):
    def __init__(self, api_url="http://localhost:3000"):
        super().__init__()
        self.api_url = api_url
        self.session_id = f"ciniforge_{int(time.time())}"

        self.setWindowTitle("Ciniforge AI Client")
        self.setGeometry(300, 300, 600, 500)

        # Create floating icon
        self.floating_icon = FloatingChatIcon()
        self.floating_icon.clicked.connect(self.show)
        self.floating_icon.show()

        # Initialize components
        self.conversation_history = []
        self.conversation_file = "assets/ciniforge_client_history.txt"
        self.load_conversation_history()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ask about video creation, news, or get help...")
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: #404040;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
        """)
        input_layout.addWidget(self.message_input)

        self.voice_input_btn = QPushButton("🎤")
        self.voice_input_btn.setToolTip("Voice Input")
        self.voice_input_btn.clicked.connect(self.start_voice_input)
        self.voice_input_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        input_layout.addWidget(self.voice_input_btn)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                color: #ffffff;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        input_layout.addWidget(self.send_btn)

        layout.addLayout(input_layout)

        # Quick action buttons
        quick_layout = QHBoxLayout()

        self.script_help_btn = QPushButton("Script Help")
        self.script_help_btn.clicked.connect(lambda: self.quick_query("Help me write a better video script"))
        quick_layout.addWidget(self.script_help_btn)

        self.topic_suggest_btn = QPushButton("Topic Ideas")
        self.topic_suggest_btn.clicked.connect(lambda: self.quick_query("Suggest trending news topics for videos"))
        quick_layout.addWidget(self.topic_suggest_btn)

        self.tech_help_btn = QPushButton("Tech Support")
        self.tech_help_btn.clicked.connect(lambda: self.quick_query("Help with video editing and production"))
        quick_layout.addWidget(self.tech_help_btn)

        layout.addLayout(quick_layout)

        self.setLayout(layout)

        # Welcome message
        self.add_message("Ciniforge AI", "🎬 Welcome to Ciniforge AI Client!\n\n"
                                        "🤖 Connected to lightweight AI API server\n\n"
                                        "💡 Direct commands:\n"
                                        "• 'Generate news video with Tamil sources'\n"
                                        "• 'Set language to Tamil, voice female'\n"
                                        "• 'Use BBC and CNN sources'\n\n"
                                        "🌐 Internet features:\n"
                                        "• 'search video editing tips'\n"
                                        "• 'wiki cinematography'\n"
                                        "• 'news technology'\n\n"
                                        "What can I help with?")

    def add_message(self, sender, message):
        """Add a message to the chat display"""
        self.chat_display.append(f"<b>{sender}:</b> {message}")
        self.chat_display.append("")  # Add spacing

        # Auto scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def send_message(self):
        message = self.message_input.text().strip()
        if not message:
            return

        self.add_message("You", message)
        self.message_input.clear()

        # Get response from API
        try:
            payload = {
                'message': message,
                'session_id': self.session_id
            }

            response = requests.post(f"{self.api_url}/chat", json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', 'No response from server')
            else:
                ai_response = f"Server error: {response.status_code}"

        except requests.exceptions.RequestException as e:
            ai_response = f"Connection error: {str(e)}. Is the API server running?"
        except Exception as e:
            ai_response = f"Error: {str(e)}"

        self.add_message("Ciniforge AI", ai_response)

        # Save conversation
        self.conversation_history.append(("You", message))
        self.conversation_history.append(("Ciniforge AI", ai_response))
        self.save_conversation_history()

    def start_voice_input(self):
        """Start voice input recording"""
        try:
            import speech_recognition as sr

            self.voice_input_btn.setText("⏹️")
            self.voice_input_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 12px;
                    color: #ffffff;
                    font-size: 14px;
                    font-weight: 600;
                }
            """)

            self.add_message("Ciniforge AI", "🎤 Listening... Speak now!")

            recognizer = sr.Recognizer()

            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)

            text = recognizer.recognize_google(audio)
            self.message_input.setText(text)
            self.add_message("Voice Input", f"Recognized: {text}")
            self.send_message()  # Auto-send the recognized text

        except sr.WaitTimeoutError:
            self.add_message("Ciniforge AI", "No speech detected. Please try again.")
        except sr.UnknownValueError:
            self.add_message("Ciniforge AI", "Could not understand audio. Please try again.")
        except sr.RequestError as e:
            self.add_message("Ciniforge AI", f"Speech recognition error: {e}")
        except ImportError:
            self.add_message("Ciniforge AI", "Voice recognition not available. Install speech_recognition")
        except Exception as e:
            self.add_message("Ciniforge AI", f"Voice input error: {e}")
        finally:
            self.voice_input_btn.setText("🎤")
            self.voice_input_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 12px;
                    color: #ffffff;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)

    def quick_query(self, query):
        """Handle quick action button clicks"""
        self.message_input.setText(query)
        self.send_message()

    def load_conversation_history(self):
        """Load conversation history from file"""
        try:
            if os.path.exists(self.conversation_file):
                with open(self.conversation_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            parts = line.strip().split('|', 1)
                            if len(parts) == 2:
                                sender, message = parts
                                self.conversation_history.append((sender, message))
                                if hasattr(self, 'chat_display'):
                                    self.add_message(sender, message)
        except Exception as e:
            print(f"Error loading conversation history: {e}")

    def save_conversation_history(self):
        """Save conversation history to file"""
        try:
            os.makedirs(os.path.dirname(self.conversation_file), exist_ok=True)
            with open(self.conversation_file, 'w', encoding='utf-8') as f:
                for sender, message in self.conversation_history[-50:]:  # Keep last 50 messages
                    f.write(f"{sender}|{message}\n")
        except Exception as e:
            print(f"Error saving conversation history: {e}")

def main():
    """Main entry point"""
    app = QApplication(sys.argv)

    # Create and show main window
    client = CiniforgeClient()

    client.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()