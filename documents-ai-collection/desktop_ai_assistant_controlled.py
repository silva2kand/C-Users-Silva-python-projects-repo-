#!/usr/bin/env python3
"""
Desktop AI Assistant - Voice Control Version
A comprehensive AI assistant with controllable voice features and colorful GUI.
"""

import sys
import os
import subprocess
import webbrowser
import pyautogui
import keyboard
import time
import psutil
import platform
from datetime import datetime
import json
from pathlib import Path
import threading

# PyQt5 imports
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QLineEdit, QLabel,
                             QSystemTrayIcon, QMenu, QAction, QMessageBox,
                             QProgressBar, QFrame, QScrollArea, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPalette, QLinearGradient, QBrush

# AI/ML imports - Try Qwen first, fallback to GPT4All
AI_AVAILABLE = False
QWEN_AVAILABLE = False
GPT4ALL_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    QWEN_AVAILABLE = True
    AI_AVAILABLE = True
    print("AI: Qwen AI model available!")
except ImportError:
    print("AI: Qwen not available, trying GPT4All...")

if not QWEN_AVAILABLE:
    try:
        from gpt4all import GPT4All
        GPT4ALL_AVAILABLE = True
        AI_AVAILABLE = True
        print("AI: GPT4All available as fallback")
    except ImportError:
        print("AI: No AI models available")

# Voice recognition imports
VOICE_AVAILABLE = False
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
    print("VOICE: Voice recognition available!")
except ImportError:
    print("VOICE: Voice recognition not available")

class VoiceWorker(QThread):
    """Robust voice recognition worker thread"""
    voice_detected = pyqtSignal(str)
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    listening_started = pyqtSignal()
    listening_stopped = pyqtSignal()

    def __init__(self, recognizer):
        super().__init__()
        self.recognizer = recognizer
        self.listening = False
        self.consecutive_errors = 0
        self.max_consecutive_errors = 3

    def run(self):
        """Main voice recognition loop with error recovery"""
        while True:  # Keep thread alive
            if self.listening:
                try:
                    self._run_voice_recognition()
                except Exception as e:
                    print(f"VOICE THREAD ERROR: {e}")
                    self.error_occurred.emit(f"Voice thread error: {e}")
                    time.sleep(2)  # Wait before retry
            else:
                time.sleep(0.1)  # Small sleep when not listening

    def _run_voice_recognition(self):
        """Voice recognition loop"""
        try:
            with sr.Microphone() as source:
                print("VOICE: Initializing microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.listening_started.emit()
                self.status_update.emit("VOICE: Ready - Say a command!")

                consecutive_timeouts = 0
                max_timeouts = 5

                while self.listening:
                    try:
                        print("VOICE: Listening for command...")
                        self.status_update.emit("VOICE: Listening...")

                        # Listen with timeout
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)

                        print("VOICE: Audio captured, processing...")
                        self.status_update.emit("VOICE: Processing...")

                        # Try recognition with fallback
                        text = self._recognize_audio(audio)

                        if text and len(text.strip()) > 0:
                            print(f"VOICE: Recognized: '{text}'")
                            self.voice_detected.emit(text)
                            self.status_update.emit("VOICE: Command received!")
                            consecutive_timeouts = 0  # Reset timeout counter
                            time.sleep(1)  # Brief pause after successful recognition

                    except sr.WaitTimeoutError:
                        consecutive_timeouts += 1
                        print(f"VOICE: Timeout ({consecutive_timeouts}/{max_timeouts})")
                        if consecutive_timeouts >= max_timeouts:
                            self.status_update.emit("VOICE: No speech detected for a while")
                            consecutive_timeouts = 0
                        continue

                    except sr.UnknownValueError:
                        print("VOICE: Could not understand audio")
                        self.status_update.emit("VOICE: Didn't catch that, try again")
                        continue

                    except sr.RequestError as e:
                        print(f"VOICE: API Error: {e}")
                        self.error_occurred.emit(f"Voice service error: {e}")
                        time.sleep(5)  # Wait longer for API errors
                        break

                    except Exception as e:
                        print(f"VOICE: Unexpected error: {e}")
                        self.error_occurred.emit(f"Voice error: {e}")
                        time.sleep(2)
                        continue

        except sr.MicrophoneUnavailableError:
            print("VOICE: Microphone not available")
            self.error_occurred.emit("Microphone not found or unavailable")
            self.listening = False

        except Exception as e:
            print(f"VOICE: Failed to start: {e}")
            self.error_occurred.emit(f"Voice initialization failed: {e}")
            self.listening = False

        finally:
            self.listening_stopped.emit()

    def _recognize_audio(self, audio):
        """Recognize audio with multiple attempts"""
        recognition_methods = [
            lambda: self.recognizer.recognize_google(audio, language='en-US'),
            lambda: self.recognizer.recognize_google(audio, language='en-GB'),
        ]

        for method in recognition_methods:
            try:
                text = method()
                if text and len(text.strip()) > 2:  # Minimum length check
                    return text.lower().strip()
            except:
                continue

        return None

    def start_listening(self):
        """Start voice recognition"""
        if not self.isRunning():
            self.start()
        self.listening = True
        print("VOICE: Starting voice recognition")

    def stop_listening(self):
        """Stop voice recognition"""
        self.listening = False
        self.status_update.emit("VOICE: Stopped")
        print("VOICE: Stopping voice recognition")

class DesktopAI(QWidget):
    """Main Desktop AI Assistant Window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Assistant - Voice & PC Control")
        self.setGeometry(100, 100, 550, 650)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Initialize components
        self.ai_model = None
        self.conversation_history = []
        self.load_conversation_history()

        # Voice components
        self.voice_recognizer = None
        self.voice_engine = None
        self.voice_worker = None
        self.voice_listening = False
        self.voice_output_enabled = True  # Control voice output

        # System control permissions
        self.permissions = {
            'file_access': False,
            'web_access': False,
            'app_launch': False,
            'system_control': False,
            'internet_search': False,
            'pc_maintenance': False,
            'programming': False,
            'auto_install': False
        }

        # Initialize voice if available
        if VOICE_AVAILABLE:
            self.init_voice()

        # Setup UI
        self.setup_modern_ui()

        # Tray icon
        self.setup_tray_icon()

        # Start AI loading
        self.start_ai_loading_thread()

        # Auto-save timer
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_conversation_history)
        self.save_timer.start(30000)

        # Voice health check timer
        self.voice_health_timer = QTimer()
        self.voice_health_timer.timeout.connect(self.check_voice_health)
        self.voice_health_timer.start(10000)  # Check every 10 seconds

    def setup_modern_ui(self):
        """Setup modern colorful UI"""
        # Main container with gradient background
        self.main_frame = QFrame()
        self.main_frame.setObjectName("mainFrame")
        self.main_frame.setStyleSheet("""
            QFrame#mainFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                border: 2px solid #5a67d8;
            }
        """)

        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title bar with modern styling
        title_bar = self.create_modern_title_bar()
        layout.addWidget(title_bar)

        # Chat display with modern styling
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.95);
                color: #2d3748;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 15px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                selection-background-color: #667eea;
            }
        """)
        layout.addWidget(self.chat_display)

        # Input area with modern buttons
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your command or click voice button...")
        self.message_input.returnPressed.connect(self.process_message)
        self.message_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.95);
                color: #2d3748;
                border: 2px solid #cbd5e0;
                border-radius: 25px;
                padding: 10px 20px;
                font-size: 12px;
                font-family: 'Segoe UI', sans-serif;
                selection-background-color: #667eea;
            }
            QLineEdit:focus {
                border-color: #667eea;
                background: rgba(255, 255, 255, 1);
            }
        """)
        input_layout.addWidget(self.message_input)

        # Send button with modern styling
        self.send_button = QPushButton("SEND")
        self.send_button.clicked.connect(self.process_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #5a67d8);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 10px 25px;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a67d8, stop:1 #4c51bf);
            }
            QPushButton:pressed {
                background: #4c51bf;
            }
        """)
        input_layout.addWidget(self.send_button)

        # Voice button with modern styling
        if VOICE_AVAILABLE:
            self.voice_button = QPushButton("VOICE")
            self.voice_button.clicked.connect(self.toggle_voice_listening)
            self.voice_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #48bb78, stop:1 #38a169);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #38a169, stop:1 #2f855a);
                }
                QPushButton:pressed {
                    background: #2f855a;
                }
            """)
            self.voice_button.setToolTip("Click to start/stop voice recognition")
            input_layout.addWidget(self.voice_button)

            # Voice output toggle button
            self.voice_toggle_button = QPushButton("SOUND ON")
            self.voice_toggle_button.clicked.connect(self.toggle_voice_output)
            self.voice_toggle_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ed8936, stop:1 #dd6b20);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    padding: 10px 15px;
                    font-weight: bold;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #dd6b20, stop:1 #c05621);
                }
                QPushButton:pressed {
                    background: #c05621;
                }
            """)
            self.voice_toggle_button.setToolTip("Toggle voice output on/off")
            input_layout.addWidget(self.voice_toggle_button)

        layout.addLayout(input_layout)

        # Status bar with modern styling
        self.status_label = QLabel("Initializing AI Assistant...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
                padding: 8px 0;
                font-size: 11px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Set main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.main_frame)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)

        # Welcome message
        ai_model_name = "Qwen" if QWEN_AVAILABLE else ("GPT4All" if GPT4ALL_AVAILABLE else "Basic")
        voice_status = "VOICE ENABLED" if VOICE_AVAILABLE else "VOICE DISABLED"
        self.add_message("AI Assistant", f"""Welcome to Advanced AI Assistant!

AI Model: {ai_model_name}
Voice Status: {voice_status}

I can help you with:
• Voice commands (click VOICE button)
• PC maintenance & repair
• File operations
• Web browsing
• System diagnostics
• Programming assistance

Try: 'help', 'system info', 'open youtube', or click VOICE!

VOICE OUTPUT: {'ENABLED' if self.voice_output_enabled else 'DISABLED'}
Click SOUND ON/OFF to toggle voice responses.""")

    def create_modern_title_bar(self):
        """Create modern title bar"""
        title_bar = QFrame()
        title_bar.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px 10px 0 0;
            }
        """)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(15, 8, 15, 8)

        title_label = QLabel("AI Assistant")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
                font-size: 16px;
            }
        """)
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # Window controls with modern styling
        minimize_btn = QPushButton("-")
        minimize_btn.clicked.connect(self.showMinimized)
        minimize_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #ffffff;
                border: none;
                font-size: 18px;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        title_layout.addWidget(minimize_btn)

        tray_btn = QPushButton("O")
        tray_btn.clicked.connect(self.hide_to_tray)
        tray_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #ffffff;
                border: none;
                font-size: 14px;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        title_layout.addWidget(tray_btn)

        close_btn = QPushButton("X")
        close_btn.clicked.connect(self.hide_to_tray)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #ffffff;
                border: none;
                font-size: 18px;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        title_layout.addWidget(close_btn)

        title_bar.setLayout(title_layout)
        return title_bar

    def setup_tray_icon(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            # Create modern icon
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor('#667eea'))
            painter = QPainter(pixmap)
            painter.setPen(QColor('white'))
            painter.setFont(QFont('Arial', 20, QFont.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, 'AI')
            painter.end()

            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon(pixmap))
            self.tray_icon.setToolTip('Advanced AI Assistant')

            # Tray menu
            tray_menu = QMenu()
            show_action = QAction('Show Assistant', self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)

            hide_action = QAction('Hide to Tray', self)
            hide_action.triggered.connect(self.hide_to_tray)
            tray_menu.addAction(hide_action)

            quit_action = QAction('Quit', self)
            quit_action.triggered.connect(self.quit_application)
            tray_menu.addAction(quit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self.tray_icon_activated)
            self.tray_icon.show()

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()

    def hide_to_tray(self):
        """Hide window to system tray"""
        self.hide()
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                'AI Assistant',
                'I\'m here! Double-click the tray icon to show me.',
                QSystemTrayIcon.Information,
                2000
            )

    def quit_application(self):
        """Quit the application"""
        if self.voice_worker:
            self.voice_worker.stop_listening()
            self.voice_worker.quit()
        self.save_conversation_history()
        QApplication.quit()

    def toggle_voice_output(self):
        """Toggle voice output on/off"""
        self.voice_output_enabled = not self.voice_output_enabled

        if self.voice_output_enabled:
            self.voice_toggle_button.setText("SOUND ON")
            self.voice_toggle_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ed8936, stop:1 #dd6b20);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    padding: 10px 15px;
                    font-weight: bold;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #dd6b20, stop:1 #c05621);
                }
                QPushButton:pressed {
                    background: #c05621;
                }
            """)
            self.add_message("System", "VOICE OUTPUT: ENABLED - Responses will be spoken")
        else:
            self.voice_toggle_button.setText("SOUND OFF")
            self.voice_toggle_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #a0aec0, stop:1 #718096);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    padding: 10px 15px;
                    font-weight: bold;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #718096, stop:1 #4a5568);
                }
                QPushButton:pressed {
                    background: #4a5568;
                }
            """)
            self.add_message("System", "VOICE OUTPUT: DISABLED - Responses will be text only")

    def init_voice(self):
        """Initialize voice recognition and text-to-speech"""
        try:
            self.voice_recognizer = sr.Recognizer()
            self.voice_engine = pyttsx3.init()
            self.voice_worker = VoiceWorker(self.voice_recognizer)

            # Connect voice worker signals
            self.voice_worker.voice_detected.connect(self.process_voice_command)
            self.voice_worker.status_update.connect(self.update_voice_status)
            self.voice_worker.error_occurred.connect(self.handle_voice_error)
            self.voice_worker.listening_started.connect(self.on_voice_started)
            self.voice_worker.listening_stopped.connect(self.on_voice_stopped)

            # Configure voice settings
            voices = self.voice_engine.getProperty('voices')
            english_voice = None

            for voice in voices:
                if 'english' in voice.name.lower() or 'en' in voice.name.lower():
                    english_voice = voice
                    break

            if english_voice:
                self.voice_engine.setProperty('voice', english_voice.id)
                self.current_language = 'en'
            else:
                self.current_language = 'en'

            # Set speech rate
            self.voice_engine.setProperty('rate', 180)
            print("VOICE: Voice initialized successfully")

        except Exception as e:
            print(f"VOICE: Voice initialization failed: {e}")
            self.voice_recognizer = None
            self.voice_engine = None

    def check_voice_health(self):
        """Check voice system health and restart if needed"""
        if not VOICE_AVAILABLE or not self.voice_worker:
            return

        # If voice should be listening but worker is not running, restart it
        if self.voice_listening and not self.voice_worker.isRunning():
            print("VOICE: Health check - restarting voice worker")
            self.restart_voice_worker()

    def restart_voice_worker(self):
        """Restart voice worker if it's not working"""
        try:
            if self.voice_worker and self.voice_worker.isRunning():
                self.voice_worker.stop_listening()
                self.voice_worker.quit()
                self.voice_worker.wait(2000)  # Wait up to 2 seconds

            # Create new worker
            self.voice_worker = VoiceWorker(self.voice_recognizer)
            self.voice_worker.voice_detected.connect(self.process_voice_command)
            self.voice_worker.status_update.connect(self.update_voice_status)
            self.voice_worker.error_occurred.connect(self.handle_voice_error)
            self.voice_worker.listening_started.connect(self.on_voice_started)
            self.voice_worker.listening_stopped.connect(self.on_voice_stopped)

            if self.voice_listening:
                self.voice_worker.start_listening()

            print("VOICE: Worker restarted successfully")

        except Exception as e:
            print(f"VOICE: Failed to restart worker: {e}")

    def toggle_voice_listening(self):
        """Toggle voice listening on/off"""
        if not VOICE_AVAILABLE or not self.voice_recognizer:
            self.add_message("System", "VOICE: Voice recognition not available")
            return

        if self.voice_listening:
            self.stop_voice_listening()
        else:
            self.start_voice_listening()

    def start_voice_listening(self):
        """Start voice recognition"""
        if self.voice_worker:
            self.voice_listening = True
            self.voice_worker.start_listening()
            self.voice_button.setText("STOP")
            self.voice_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e53e3e, stop:1 #c53030);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #c53030, stop:1 #9b2c2c);
                }
                QPushButton:pressed {
                    background: #9b2c2c;
                }
            """)

    def stop_voice_listening(self):
        """Stop voice recognition"""
        if self.voice_worker:
            self.voice_listening = False
            self.voice_worker.stop_listening()
            self.voice_button.setText("VOICE")
            self.voice_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #48bb78, stop:1 #38a169);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #38a169, stop:1 #2f855a);
                }
                QPushButton:pressed {
                    background: #2f855a;
                }
            """)

    def update_voice_status(self, status):
        """Update voice status"""
        self.status_label.setText(f"VOICE: {status}")

    def handle_voice_error(self, error):
        """Handle voice recognition errors"""
        self.add_message("System", f"VOICE ERROR: {error}")
        # Don't stop listening automatically - let health check handle it
        self.status_label.setText("VOICE: Error - Retrying...")

    def on_voice_started(self):
        """Called when voice listening starts"""
        print("VOICE: Listening started successfully")

    def on_voice_stopped(self):
        """Called when voice listening stops"""
        print("VOICE: Listening stopped")

    def process_voice_command(self, text):
        """Process voice command"""
        self.add_message("Voice", f"VOICE: {text}")
        self.message_input.setText(text)
        self.process_message()

    def speak_response(self, text):
        """Speak the response using text-to-speech"""
        if not VOICE_AVAILABLE or not self.voice_engine or not self.voice_output_enabled:
            return

        try:
            # Clean text for speech
            clean_text = text.replace('[OK]', '').replace('[ERROR]', '').replace('[AI]', '').replace('[TIP]', '')
            clean_text = clean_text.replace('[FIX]', '').replace('[CLEAN]', '').replace('[FAST]', '')

            # Speak in a separate thread to avoid blocking
            import threading
            def speak():
                try:
                    self.voice_engine.say(clean_text)
                    self.voice_engine.runAndWait()
                except Exception as e:
                    print(f"SPEECH ERROR: {e}")

            speech_thread = threading.Thread(target=speak, daemon=True)
            speech_thread.start()

        except Exception as e:
            print(f"SPEECH ERROR: {e}")

    def start_ai_loading_thread(self):
        """Start AI loading with better error handling"""
        try:
            QTimer.singleShot(100, self.load_ai_with_timeout)
        except Exception as e:
            print(f"AI: Failed to start AI loading: {e}")
            self.status_label.setText("Ready - AI Offline (Loading failed)")

    def load_ai_with_timeout(self):
        """Load AI with timeout to prevent UI freezing"""
        try:
            import threading
            result = [None]
            exception = [None]

            def load_ai():
                try:
                    result[0] = self.setup_ai()
                except Exception as e:
                    exception[0] = e

            ai_thread = threading.Thread(target=load_ai, daemon=True)
            ai_thread.start()
            ai_thread.join(timeout=30)

            if ai_thread.is_alive():
                self.status_label.setText("Ready - AI Loading Timed Out")
                self.add_message("System", "AI: Model loading timed out. Basic commands will still work.")
            elif exception[0]:
                self.status_label.setText("Ready - AI Offline (Error)")
                self.add_message("System", f"AI: Loading failed: {str(exception[0])}")
            else:
                self.status_label.setText(result[0])
                if "Active" in result[0]:
                    self.add_message("System", "AI: Model loaded successfully! I'm ready to help.")
                elif "Offline" in result[0]:
                    self.add_message("System", "AI: Model not available. Basic commands will still work.")

        except Exception as e:
            print(f"AI: AI loading thread failed: {e}")
            self.status_label.setText("Ready - AI Offline (Thread error)")

    def setup_ai(self):
        """Setup AI model"""
        if QWEN_AVAILABLE:
            try:
                print("AI: Loading Qwen AI model...")
                model_name = "microsoft/DialoGPT-small"
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.ai_model = AutoModelForCausalLM.from_pretrained(model_name)
                print("AI: Qwen AI loaded successfully!")
                return "Ready - AI Active with Enhanced Model!"
            except Exception as e:
                print(f"AI: Qwen loading failed: {e}")
                return self.fallback_to_gpt4all()
        elif GPT4ALL_AVAILABLE:
            return self.fallback_to_gpt4all()
        else:
            return "Ready - AI Offline (No models available)"

    def fallback_to_gpt4all(self):
        """Fallback to GPT4All"""
        try:
            print("AI: Falling back to GPT4All...")
            self.ai_model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf", device='cpu')
            print("AI: GPT4All loaded as fallback")
            return "Ready - AI Active with GPT4All"
        except Exception as e:
            self.ai_model = None
            print(f"AI: GPT4All also failed: {e}")
            return f"Ready - AI Offline: {str(e)}"

    def process_message(self):
        """Process user message with improved threading"""
        message = self.message_input.text().strip()
        if not message:
            return

        self.add_message("You", message)
        self.message_input.clear()

        # Disable input while processing
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        if hasattr(self, 'voice_button'):
            self.voice_button.setEnabled(False)
        if hasattr(self, 'voice_toggle_button'):
            self.voice_toggle_button.setEnabled(False)
        self.status_label.setText("Processing...")

        # Process command in a separate thread
        import threading
        def process_command_thread():
            try:
                response = self.execute_command(message)

                # Use QTimer to update UI from main thread
                QTimer.singleShot(0, lambda: self.add_message("Assistant", response))
                QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))

                # Speak the response if voice is available and enabled
                if VOICE_AVAILABLE and self.voice_engine and self.voice_output_enabled:
                    speech_thread = threading.Thread(target=lambda: self.speak_response(response), daemon=True)
                    speech_thread.start()

            except Exception as e:
                error_msg = f"ERROR: An error occurred: {str(e)}"
                QTimer.singleShot(0, lambda: self.add_message("Assistant", error_msg))
                QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))
                print(f"ERROR: Message processing failed: {e}")
            finally:
                QTimer.singleShot(0, lambda: self.message_input.setEnabled(True))
                QTimer.singleShot(0, lambda: self.send_button.setEnabled(True))
                if hasattr(self, 'voice_button'):
                    QTimer.singleShot(0, lambda: self.voice_button.setEnabled(True))
                if hasattr(self, 'voice_toggle_button'):
                    QTimer.singleShot(0, lambda: self.voice_toggle_button.setEnabled(True))

        command_thread = threading.Thread(target=process_command_thread, daemon=True)
        command_thread.start()

    def execute_command(self, command):
        """Execute natural language commands"""
        command_lower = command.lower()

        # Help command
        if any(word in command_lower for word in ['help', 'commands', 'what can you do']):
            return self.get_help_text()

        # System information
        elif any(phrase in command_lower for phrase in ['system info', 'computer info', 'my pc info']):
            return self.get_system_info()

        # PC Maintenance & Repair
        elif any(word in command_lower for word in ['repair', 'fix', 'maintain', 'clean', 'optimize']):
            return self.pc_maintenance(command)

        # Programming & Development
        elif any(word in command_lower for word in ['code', 'program', 'develop', 'script', 'vs code', 'vscode']):
            return self.programming_assistance(command)

        # Internet Research & Learning
        elif any(word in command_lower for word in ['learn', 'research', 'find', 'discover', 'tutorial']):
            return self.internet_research(command)

        # Auto-installation
        elif any(word in command_lower for word in ['install', 'download', 'setup', 'get']):
            return self.auto_install(command)

        # File operations
        elif any(word in command_lower for word in ['create', 'make', 'new']) and 'folder' in command_lower:
            return self.create_folder(command)

        # Application launching
        elif 'open' in command_lower or 'launch' in command_lower or 'start' in command_lower:
            return self.open_application(command)

        # Web operations
        elif any(word in command_lower for word in ['search', 'google', 'find']):
            return self.web_search(command)
        elif any(phrase in command_lower for phrase in ['open website', 'go to', 'visit']):
            return self.open_website(command)

        # System control
        elif any(word in command_lower for word in ['shutdown', 'restart', 'power off']):
            return self.system_control(command)
        elif 'volume' in command_lower or 'sound' in command_lower:
            return self.control_volume(command)

        # Voice commands
        elif any(word in command_lower for word in ['voice', 'speak', 'talk', 'say']):
            return self.handle_voice_command(command)

        # AI-powered response
        else:
            return self.get_ai_response(command)

    def get_help_text(self):
        """Get comprehensive help text"""
        voice_status = "VOICE ENABLED" if VOICE_AVAILABLE else "VOICE DISABLED"
        ai_status = "AI ACTIVE" if AI_AVAILABLE else "AI OFFLINE"
        sound_status = "VOICE OUTPUT ENABLED" if self.voice_output_enabled else "VOICE OUTPUT DISABLED"

        return f"""AI ASSISTANT HELP - {ai_status} | {voice_status}

VOICE COMMANDS:
• Click VOICE button to start/stop voice recognition
• Say commands naturally (e.g., "open youtube", "system info")
• Click SOUND ON/OFF to toggle voice responses
• {sound_status}

PC MAINTENANCE & REPAIR:
• 'clean temp files' - Clear temporary files
• 'disk cleanup' - Free up disk space
• 'check for updates' - System updates
• 'update drivers' - Device driver updates
• 'virus scan' - Security scan
• 'run diagnostics' - System health check
• 'network diagnostics' - Fix connection issues
• 'system repair' - Run repair tools
• 'optimize performance' - Speed up your PC

APPLICATIONS & WEBSITES:
• 'open chrome/firefox/edge' - Web browsers
• 'open notepad/calculator' - System apps
• 'open youtube/gmail/facebook' - Popular websites
• 'open [app name]' - Any application

WEB & SEARCH:
• 'search for [query]' - Google search
• 'open website [url]' - Visit website

SYSTEM CONTROL:
• 'system info' - Computer details
• 'shutdown/restart' - Power management

PROGRAMMING:
• 'open vs code' - Launch code editor
• 'create python project [name]' - New Python project

VOICE CONTROLS:
• 'start listening' - Begin voice recognition
• 'stop listening' - End voice recognition
• 'speak [text]' - Text-to-speech

Try any command or use voice recognition!"""

    def get_system_info(self):
        """Get system information"""
        try:
            info = {
                'OS': f"{platform.system()} {platform.release()}",
                'Processor': platform.processor(),
                'RAM': f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
                'CPU Usage': f"{psutil.cpu_percent()}%",
                'Memory Usage': f"{psutil.virtual_memory().percent}%",
                'Disk Usage': f"{psutil.disk_usage('/').percent}%"
            }

            return f"""SYSTEM INFORMATION:
• OS: {info['OS']}
• Processor: {info['Processor']}
• RAM: {info['RAM']}
• CPU Usage: {info['CPU Usage']}
• Memory Usage: {info['Memory Usage']}
• Disk Usage: {info['Disk Usage']}"""
        except Exception as e:
            return f"ERROR: Could not get system info: {str(e)}"

    def open_application(self, command):
        """Open applications with improved parsing"""
        command_lower = command.lower()

        # Remove common prefixes
        for prefix in ['open', 'launch', 'start', 'can you', 'please', 'plz', 'could you']:
            command_lower = command_lower.replace(prefix, '').strip()

        # Handle YouTube and websites
        if 'youtube' in command_lower:
            try:
                webbrowser.open('https://www.youtube.com')
                return "OPENED: YouTube in your default browser"
            except Exception as e:
                return f"ERROR: Could not open YouTube: {str(e)}"

        websites = {
            'google': 'https://www.google.com',
            'gmail': 'https://www.gmail.com',
            'facebook': 'https://www.facebook.com',
            'twitter': 'https://www.twitter.com',
            'instagram': 'https://www.instagram.com',
            'github': 'https://www.github.com'
        }

        for site, url in websites.items():
            if site in command_lower:
                try:
                    webbrowser.open(url)
                    return f"OPENED: {site.capitalize()}"
                except Exception as e:
                    return f"ERROR: Could not open {site}: {str(e)}"

        # Handle applications
        app_commands = {
            'chrome': 'chrome',
            'firefox': 'firefox',
            'edge': 'msedge',
            'notepad': 'notepad',
            'calculator': 'calc',
            'explorer': 'explorer',
            'cmd': 'cmd',
            'powershell': 'powershell',
            'word': 'winword',
            'excel': 'excel',
            'powerpoint': 'powerpnt',
            'paint': 'mspaint'
        }

        for app_key, app_cmd in app_commands.items():
            if app_key in command_lower:
                try:
                    if not self.request_permission('app_launch', f"Launch {app_key}?"):
                        return "ERROR: Permission denied"

                    result = subprocess.Popen(
                        app_cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        shell=True
                    )
                    return f"OPENED: {app_key}"
                except FileNotFoundError:
                    return f"ERROR: {app_key} not found. Please check if it's installed."
                except Exception as e:
                    return f"ERROR: Could not open {app_key}: {str(e)}"

        return f"I understand you want to open something, but I couldn't identify '{command}'. Try: chrome, firefox, notepad, calculator, youtube, etc."

    def pc_maintenance(self, command):
        """PC maintenance and repair"""
        if not self.request_permission('pc_maintenance', 'perform PC maintenance tasks'):
            return "ERROR: Permission denied for PC maintenance"

        command_lower = command.lower()

        if 'clean' in command_lower or 'temp' in command_lower:
            if 'browser' in command_lower or 'cache' in command_lower:
                return self.clear_browser_cache()
            else:
                return self.clean_temp_files()
        elif 'disk' in command_lower or 'storage' in command_lower:
            return self.disk_cleanup()
        elif 'update' in command_lower:
            if 'driver' in command_lower:
                return self.update_drivers()
            else:
                return self.check_updates()
        elif 'virus' in command_lower or 'scan' in command_lower:
            return self.virus_scan()
        elif 'performance' in command_lower or 'optimize' in command_lower:
            return self.optimize_performance()
        elif 'diagnostics' in command_lower:
            return self.system_diagnostics()
        elif 'network' in command_lower:
            return self.network_diagnostics()
        elif 'repair' in command_lower or 'fix' in command_lower:
            return self.system_diagnostics()
        else:
            return """PC MAINTENANCE OPTIONS:
• 'clean temp files' - Clear temporary files
• 'clear browser cache' - Clean browser caches
• 'disk cleanup' - Free up disk space
• 'check for updates' - System updates
• 'update drivers' - Device driver updates
• 'virus scan' - Security scan
• 'run diagnostics' - System health check
• 'network diagnostics' - Fix connection issues
• 'system repair' - Run repair tools
• 'optimize performance' - Speed up your PC"""

    def clean_temp_files(self):
        """Clean temporary files"""
        try:
            import tempfile
            import shutil

            temp_dir = tempfile.gettempdir()
            cleaned_size = 0

            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        cleaned_size += size
                    except:
                        pass

            return f"CLEANED: {cleaned_size / (1024*1024):.2f} MB of temporary files"
        except Exception as e:
            return f"ERROR: Could not clean temp files: {str(e)}"

    def disk_cleanup(self):
        """Perform disk cleanup"""
        try:
            if platform.system() == 'Windows':
                subprocess.run(['cleanmgr', '/sagerun:1'], capture_output=True)
                return "STARTED: Windows Disk Cleanup - this will help free up disk space"
            else:
                return "TIP: Disk cleanup is primarily available on Windows"
        except Exception as e:
            return f"ERROR: Could not run disk cleanup: {str(e)}"

    def check_updates(self):
        """Check for system updates"""
        try:
            if platform.system() == 'Windows':
                try:
                    subprocess.run(['wuauclt', '/detectnow'], capture_output=True)
                except:
                    pass

                try:
                    subprocess.run(['powershell', 'Start-Process "ms-settings:windowsupdate"'], capture_output=True)
                except:
                    pass

                return "STARTED: Windows Update check - your system will check for available updates"
            else:
                return "TIP: System updates are managed differently on your OS"
        except Exception as e:
            return f"ERROR: Could not check updates: {str(e)}"

    def update_drivers(self):
        """Update device drivers"""
        try:
            if platform.system() == 'Windows':
                subprocess.run(['devmgmt.msc'], shell=True)
                return "OPENED: Device Manager - right-click on devices and select 'Update driver'"
            else:
                return "TIP: Driver updates are OS-specific"
        except Exception as e:
            return f"ERROR: Could not open Device Manager: {str(e)}"

    def virus_scan(self):
        """Perform virus scan"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['powershell', 'Start-MpScan -ScanType QuickScan'], capture_output=True, text=True)
                if result.returncode == 0:
                    return "STARTED: Windows Defender quick scan"
                else:
                    return "WARNING: Windows Defender scan couldn't be started"
            else:
                return "TIP: Antivirus scanning is OS-specific"
        except Exception as e:
            return f"ERROR: Could not start virus scan: {str(e)}"

    def optimize_performance(self):
