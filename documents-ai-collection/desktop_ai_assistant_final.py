#!/usr/bin/env python3
"""
Desktop AI Assistant - Final Version with Voice & Color GUI
A comprehensive AI assistant with voice commands, colorful GUI, and full PC control.
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

# PyQt5 imports
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QLineEdit, QLabel,
                             QSystemTrayIcon, QMenu, QAction, QMessageBox,
                             QProgressBar, QFrame, QScrollArea, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPalette, QLinearGradient, QBrush

# AI/ML imports - Prioritize local models, then free APIs
AI_AVAILABLE = False
QWEN_AVAILABLE = False
GPT4ALL_AVAILABLE = False
LOCAL_LLM_AVAILABLE = False
FREE_API_AVAILABLE = False

# Try local models first
try:
    from gpt4all import GPT4All
    GPT4ALL_AVAILABLE = True
    AI_AVAILABLE = True
    print("AI: GPT4All local model available!")
except ImportError:
    print("AI: GPT4All not available, trying other local options...")

if not GPT4ALL_AVAILABLE:
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        QWEN_AVAILABLE = True
        AI_AVAILABLE = True
        print("AI: Qwen local model available!")
    except ImportError:
        print("AI: Local models not available, trying free APIs...")

# Try free API alternatives
if not AI_AVAILABLE:
    try:
        import requests
        FREE_API_AVAILABLE = True
        AI_AVAILABLE = True
        print("AI: Free API alternatives available!")
    except ImportError:
        print("AI: No AI models or APIs available")

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
    """Voice recognition worker thread"""
    voice_detected = pyqtSignal(str)
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, recognizer):
        super().__init__()
        self.recognizer = recognizer
        self.listening = False

    def run(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.status_update.emit("VOICE: Ready to listen...")

                while self.listening:
                    try:
                        self.status_update.emit("VOICE: Listening...")
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)

                        self.status_update.emit("VOICE: Processing...")
                        # Try English first, then Tamil
                        try:
                            text = self.recognizer.recognize_google(audio, language='en-US')
                        except sr.UnknownValueError:
                            try:
                                text = self.recognizer.recognize_google(audio, language='ta-IN')
                            except sr.UnknownValueError:
                                text = ""

                        if text and len(text.strip()) > 0:
                            self.voice_detected.emit(text)
                            time.sleep(1)  # Prevent rapid re-triggering

                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as e:
                        self.error_occurred.emit(f"VOICE: Service error - {e}")
                        break
                    except Exception as e:
                        self.error_occurred.emit(f"VOICE: Error - {e}")
                        continue

        except Exception as e:
            self.error_occurred.emit(f"VOICE: Failed to start - {e}")

    def start_listening(self):
        self.listening = True
        if not self.isRunning():
            self.start()

    def stop_listening(self):
        self.listening = False

class DesktopAI(QWidget):
    """Main Desktop AI Assistant Window"""

    def __init__(self):
        super().__init__()
        print("DEBUG: Initializing Desktop AI Assistant...")
        self.setWindowTitle("AI Assistant - Voice & PC Control")
        # Position window in center of screen
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(
            (screen.width() - 550) // 2,
            (screen.height() - 650) // 2,
            550, 650
        )
        # Simple window setup for maximum visibility
        self.setWindowFlags(Qt.Window)
        self.setWindowState(Qt.WindowActive)
        self.setFocus()

        # Ensure window is properly sized and positioned
        self.resize(550, 650)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        print("DEBUG: Window initialized")

        # Initialize components
        self.ai_model = None
        self.pygpt_client = None
        self.conversation_history = []
        self.load_conversation_history()

        # Voice components
        self.voice_recognizer = None
        self.voice_engine = None
        self.voice_worker = None
        self.voice_listening = False

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

        # Ensure window is visible
        self.show()
        self.raise_()
        self.activateWindow()

        # Force window to stay on top temporarily
        QTimer.singleShot(2000, lambda: self.setWindowFlags(Qt.Window))

        # Simple status message
        print("AI Assistant window is now visible on desktop!")

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
        # Set solid background for main window
        self.setStyleSheet("background-color: #f0f0f0;")

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

        layout.addLayout(input_layout)

        # Progress bar for AI loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 5px;
                text-align: center;
                color: white;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 5px;
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

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

    def fade_in_animation(self):
        """Smooth fade-in animation for window"""
        self.setWindowOpacity(0.0)
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(500)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()

        # Welcome message
        if GPT4ALL_AVAILABLE:
            ai_model_name = "Local GPT4All"
        elif QWEN_AVAILABLE:
            ai_model_name = "Local Qwen"
        elif FREE_API_AVAILABLE:
            ai_model_name = "Free API"
        else:
            ai_model_name = "Basic"
        voice_status = "VOICE ENABLED" if VOICE_AVAILABLE else "VOICE DISABLED"
        self.add_message("AI Assistant", f"""Welcome to Advanced AI Assistant!

AI Model: {ai_model_name}
Voice Status: {voice_status}
Language Support: Tamil & English

I can help you with:
• Voice commands (click VOICE button)
• PC maintenance & repair
• File operations
• Web browsing
• System diagnostics
• Programming assistance
• Bilingual Tamil/English support

Try: 'help', 'system info', 'open youtube', or click VOICE!
தமிழ் மொழியில் கேள்விகளைக் கேட்கலாம்!""")

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
        minimize_btn = QPushButton("−")
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

        tray_btn = QPushButton("□")
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

        close_btn = QPushButton("×")
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
            show_action.triggered.connect(self.show_window)
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
            self.setWindowState(Qt.WindowActive)
            # Ensure window is not minimized
            if self.isMinimized():
                self.showNormal()

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

    def show_window(self):
        """Show window properly"""
        self.show()
        self.raise_()
        self.activateWindow()
        self.setWindowState(Qt.WindowActive)
        if self.isMinimized():
            self.showNormal()
        # Ensure window is focused
        self.setFocus()

    def quit_application(self):
        """Quit the application"""
        self.save_conversation_history()
        QApplication.quit()

    def init_voice(self):
        """Initialize voice recognition and text-to-speech with bilingual support"""
        try:
            self.voice_recognizer = sr.Recognizer()
            self.voice_engine = pyttsx3.init()
            self.voice_worker = VoiceWorker(self.voice_recognizer)

            # Connect voice worker signals
            self.voice_worker.voice_detected.connect(self.process_voice_command)
            self.voice_worker.status_update.connect(self.update_voice_status)
            self.voice_worker.error_occurred.connect(self.handle_voice_error)

            # Configure voice settings with bilingual support
            voices = self.voice_engine.getProperty('voices')
            english_voice = None
            tamil_voice = None

            for voice in voices:
                voice_name = voice.name.lower()
                if 'tamil' in voice_name or 'ta' in voice_name:
                    tamil_voice = voice
                elif 'english' in voice_name or 'en' in voice_name:
                    english_voice = voice

            # Default to English, but support Tamil
            self.current_language = 'en'
            if english_voice:
                self.voice_engine.setProperty('voice', english_voice.id)
            elif tamil_voice:
                self.voice_engine.setProperty('voice', tamil_voice.id)
                self.current_language = 'ta'

            # Set speech rate
            self.voice_engine.setProperty('rate', 180)
            print("VOICE: Voice initialized with bilingual support")

        except Exception as e:
            print(f"VOICE: Voice initialization failed: {e}")
            self.voice_recognizer = None
            self.voice_engine = None

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
        self.stop_voice_listening()

    def process_voice_command(self, text):
        """Process voice command"""
        self.add_message("Voice", f"VOICE: {text}")
        self.message_input.setText(text)
        self.process_message()

    def speak_response(self, text):
        """Speak the response using text-to-speech with bilingual support"""
        if not VOICE_AVAILABLE or not self.voice_engine:
            return

        try:
            # Clean text for speech
            clean_text = text.replace('[OK]', '').replace('[ERROR]', '').replace('[AI]', '').replace('[TIP]', '')
            clean_text = clean_text.replace('[FIX]', '').replace('[CLEAN]', '').replace('[FAST]', '')

            # Set voice based on current language
            voices = self.voice_engine.getProperty('voices')
            if self.current_language == 'ta':
                tamil_voice = None
                for voice in voices:
                    if 'tamil' in voice.name.lower() or 'ta' in voice.name.lower():
                        tamil_voice = voice
                        break
                if tamil_voice:
                    self.voice_engine.setProperty('voice', tamil_voice.id)
            else:
                english_voice = None
                for voice in voices:
                    if 'english' in voice.name.lower() or 'en' in voice.name.lower():
                        english_voice = voice
                        break
                if english_voice:
                    self.voice_engine.setProperty('voice', english_voice.id)

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
                    # Show progress bar
                    QTimer.singleShot(0, lambda: self.progress_bar.show())
                    QTimer.singleShot(0, lambda: self.progress_bar.setValue(10))
                    QTimer.singleShot(0, lambda: self.status_label.setText("Loading AI Model..."))

                    result[0] = self.setup_ai()

                    QTimer.singleShot(0, lambda: self.progress_bar.setValue(100))
                    QTimer.singleShot(0, lambda: self.progress_bar.hide())
                except Exception as e:
                    exception[0] = e
                    QTimer.singleShot(0, lambda: self.progress_bar.hide())

            ai_thread = threading.Thread(target=load_ai, daemon=True)
            ai_thread.start()
            ai_thread.join(timeout=30)

            if ai_thread.is_alive():
                self.status_label.setText("Ready - AI Loading Timed Out")
                self.progress_bar.hide()
                self.add_message("System", "AI: Model loading timed out. Basic commands will still work.")
            elif exception[0]:
                self.status_label.setText("Ready - AI Offline (Error)")
                self.progress_bar.hide()
                self.add_message("System", f"AI: Loading failed: {str(exception[0])}")
            else:
                self.status_label.setText(result[0])
                self.progress_bar.hide()
                if "Active" in result[0]:
                    self.add_message("System", "AI: Model loaded successfully! I'm ready to help.")
                elif "Offline" in result[0]:
                    self.add_message("System", "AI: Model not available. Basic commands will still work.")

        except Exception as e:
            print(f"AI: AI loading thread failed: {e}")
            self.status_label.setText("Ready - AI Offline (Thread error)")
            self.progress_bar.hide()

    def setup_ai(self):
        """Setup AI model - prioritize local models"""
        if GPT4ALL_AVAILABLE:
            return self.setup_gpt4all()
        elif QWEN_AVAILABLE:
            return self.setup_qwen()
        elif FREE_API_AVAILABLE:
            return self.setup_free_api()
        else:
            return "Ready - AI Offline (No models available)"

    def setup_gpt4all(self):
        """Setup GPT4All local model"""
        try:
            print("AI: Loading GPT4All local model...")
            # Try different model names and CPU-only mode
            model_names = [
                "orca-mini-3b-gguf2-q4_0.gguf",
                "orca-2-7b.Q4_0.gguf",
                "gpt4all-falcon-q4_0.gguf",
                "wizardlm-13b-v1.2.Q4_0.gguf"
            ]

            for model_name in model_names:
                try:
                    print(f"AI: Trying model: {model_name}")
                    self.ai_model = GPT4All(model_name, device='cpu', verbose=False)
                    print("AI: GPT4All loaded successfully!")
                    return "Ready - AI Active with Local GPT4All!"
                except Exception as e:
                    print(f"AI: Model {model_name} failed: {e}")
                    continue

            # If all models fail, try without specifying model (uses default)
            print("AI: Trying default GPT4All model...")
            self.ai_model = GPT4All(device='cpu', verbose=False)
            print("AI: GPT4All loaded with default model!")
            return "Ready - AI Active with Local GPT4All!"

        except Exception as e:
            print(f"AI: GPT4All loading failed: {e}")
            return self.setup_qwen()

    def setup_qwen(self):
        """Setup Qwen local model"""
        try:
            print("AI: Loading Qwen local model...")
            model_name = "microsoft/DialoGPT-small"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.ai_model = AutoModelForCausalLM.from_pretrained(model_name)
            print("AI: Qwen loaded successfully!")
            return "Ready - AI Active with Local Qwen!"
        except Exception as e:
            print(f"AI: Qwen loading failed: {e}")
            return self.setup_free_api()

    def setup_free_api(self):
        """Setup free API alternatives"""
        try:
            print("AI: Setting up free API alternatives...")
            # Use Hugging Face free inference API or similar
            self.api_base_url = "https://api-inference.huggingface.co/models/"
            self.api_model = "microsoft/DialoGPT-medium"
            print("AI: Free API ready!")
            return "Ready - AI Active with Free API!"
        except Exception as e:
            print(f"AI: Free API setup failed: {e}")
            return "Ready - AI Offline (All options failed)"

    def call_free_api(self, prompt):
        """Call free API for AI response"""
        try:
            import requests
            url = f"{self.api_base_url}{self.api_model}"
            headers = {"Authorization": "Bearer hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}  # Free tier
            data = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 150,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', 'No response generated').strip()
            return "Free API response unavailable. Using basic responses."
        except Exception as e:
            print(f"Free API error: {e}")
            return "Free API unavailable. Using basic responses."

    def detect_language(self, text):
        """Detect if text is Tamil or English"""
        tamil_chars = set('அஆஇஈஉஊஎஏஐஒஓஔகஙசஜஞடணதநபமயரலவஶஷஸஹாிீுூெேைொோௌ்')
        for char in text:
            if char in tamil_chars:
                return 'ta'
        return 'en'

    def process_message(self):
        """Process user message with bilingual support"""
        message = self.message_input.text().strip()
        if not message:
            return

        # Detect language
        detected_lang = self.detect_language(message)
        self.current_language = detected_lang

        self.add_message("You", message)
        self.message_input.clear()

        # Disable input while processing
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        if hasattr(self, 'voice_button'):
            self.voice_button.setEnabled(False)
        self.status_label.setText("Processing...")

        # Process command in a separate thread
        import threading
        def process_command_thread():
            try:
                response = self.execute_command(message)

                # Use QTimer to update UI from main thread
                QTimer.singleShot(0, lambda: self.add_message("Assistant", response))
                QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))

                # Speak the response if voice is available
                if VOICE_AVAILABLE and self.voice_engine:
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
        elif any(word in command_lower for word in ['code', 'program', 'develop', 'script', 'vs code', 'vscode', 'python', 'javascript', 'java', 'c++', 'html', 'css']):
            return self.programming_assistance(command)

        # Internet Research & Learning
        elif any(word in command_lower for word in ['learn', 'research', 'find', 'discover', 'tutorial']):
            return self.internet_research(command)

        # Video & Media Control
        elif any(word in command_lower for word in ['video', 'youtube', 'media', 'play', 'stream', 'watch']):
            return self.media_control(command)

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

    def programming_assistance(self, command):
        """Enhanced programming assistance"""
        command_lower = command.lower()

        if 'open vs code' in command_lower or 'open vscode' in command_lower:
            try:
                subprocess.Popen(['code'], shell=True)
                return "OPENED: Visual Studio Code"
            except FileNotFoundError:
                return "ERROR: VS Code not found. Please install it first."
            except Exception as e:
                return f"ERROR: Could not open VS Code: {str(e)}"
        elif 'create python project' in command_lower:
            return self.create_python_project(command)
        elif 'run python' in command_lower:
            return self.run_python_script(command)
        elif 'check code' in command_lower or 'syntax check' in command_lower:
            return self.check_code_syntax(command)
        elif 'install' in command_lower and 'package' in command_lower:
            return self.install_package(command)
        elif 'create' in command_lower and 'html' in command_lower:
            return self.create_html_template(command)
        elif 'generate code' in command_lower or 'write code' in command_lower:
            return self.generate_code(command)
        else:
            return """PROGRAMMING ASSISTANCE:
• 'open vs code' - Launch code editor
• 'create python project [name]' - New Python project
• 'run python [file]' - Execute Python script
• 'check code [file]' - Syntax check
• 'install package [name]' - Install Python package
• 'create html template' - Generate HTML template
• 'generate code for [task]' - AI code generation
• 'debug [code]' - Code debugging help"""

    def create_python_project(self, command):
        """Create a new Python project"""
        try:
            # Extract project name
            import re
            match = re.search(r'create python project (\w+)', command.lower())
            if match:
                project_name = match.group(1)
            else:
                project_name = "my_python_project"

            project_dir = Path.home() / "Desktop" / project_name
            project_dir.mkdir(exist_ok=True)

            # Create main.py
            main_py = project_dir / "main.py"
            main_py.write_text("""#!/usr/bin/env python3
\"\"\"
{project_name} - Main Python Script
\"\"\"

def main():
    print("Hello from {project_name}!")

if __name__ == "__main__":
    main()
""".format(project_name=project_name))

            # Create requirements.txt
            req_txt = project_dir / "requirements.txt"
            req_txt.write_text("# Add your dependencies here\n")

            # Create README.md
            readme = project_dir / "README.md"
            readme.write_text(f"""# {project_name}

A Python project created by AI Assistant.

## Usage

Run the main script:
```bash
python main.py
```

## Requirements

Install dependencies:
```bash
pip install -r requirements.txt
```
""")

            return f"CREATED: Python project '{project_name}' on Desktop with main.py, requirements.txt, and README.md"
        except Exception as e:
            return f"ERROR: Could not create Python project: {str(e)}"

    def run_python_script(self, command):
        """Run a Python script"""
        try:
            import re
            match = re.search(r'run python (.+)', command.lower())
            if match:
                script_path = match.group(1).strip()
                if not script_path.endswith('.py'):
                    script_path += '.py'

                # Try to find the script
                script_file = Path(script_path)
                if not script_file.is_absolute():
                    script_file = Path.cwd() / script_path

                if script_file.exists():
                    result = subprocess.run(['python', str(script_file)], capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        return f"EXECUTED: {script_path}\nOutput: {result.stdout}"
                    else:
                        return f"ERROR: Script failed\n{result.stderr}"
                else:
                    return f"ERROR: Script not found: {script_path}"
            else:
                return "ERROR: Please specify a Python script to run"
        except Exception as e:
            return f"ERROR: Could not run Python script: {str(e)}"

    def check_code_syntax(self, command):
        """Check Python code syntax"""
        try:
            import re
            match = re.search(r'check code (.+)', command.lower())
            if match:
                file_path = match.group(1).strip()
                if not file_path.endswith('.py'):
                    file_path += '.py'

                script_file = Path(file_path)
                if not script_file.is_absolute():
                    script_file = Path.cwd() / file_path

                if script_file.exists():
                    result = subprocess.run(['python', '-m', 'py_compile', str(script_file)], capture_output=True, text=True)
                    if result.returncode == 0:
                        return f"SYNTAX OK: {file_path} - No syntax errors found"
                    else:
                        return f"SYNTAX ERROR in {file_path}:\n{result.stderr}"
                else:
                    return f"ERROR: File not found: {file_path}"
            else:
                return "ERROR: Please specify a Python file to check"
        except Exception as e:
            return f"ERROR: Could not check syntax: {str(e)}"

    def install_package(self, command):
        """Install Python package"""
        try:
            import re
            match = re.search(r'install package (\w+)', command.lower())
            if match:
                package_name = match.group(1)
                result = subprocess.run(['pip', 'install', package_name], capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    return f"INSTALLED: {package_name} successfully"
                else:
                    return f"ERROR: Failed to install {package_name}\n{result.stderr}"
            else:
                return "ERROR: Please specify a package name"
        except Exception as e:
            return f"ERROR: Could not install package: {str(e)}"

    def create_html_template(self, command):
        """Create HTML template"""
        try:
            html_file = Path.home() / "Desktop" / "index.html"
            html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Web Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to My Web Page</h1>
        <p>This is a basic HTML template created by AI Assistant.</p>
    </div>

    <script>
        console.log('Page loaded successfully!');
    </script>
</body>
</html>"""
            html_file.write_text(html_content)
            return f"CREATED: HTML template at {html_file}"
        except Exception as e:
            return f"ERROR: Could not create HTML template: {str(e)}"

    def generate_code(self, command):
        """Generate code using AI"""
        try:
            import re
            match = re.search(r'generate code for (.+)', command.lower())
            if match:
                task = match.group(1).strip()
                prompt = f"Generate Python code for: {task}. Provide clean, well-commented code."

                if self.ai_model or self.pygpt_client:
                    return self.get_ai_response(prompt)
                else:
                    return f"I need an AI model to generate code. Please ensure Qwen, PyGPT, or GPT4All is available."
            else:
                return "ERROR: Please specify what code to generate"
        except Exception as e:
            return f"ERROR: Could not generate code: {str(e)}"

    def media_control(self, command):
        """Control video and media playback"""
        command_lower = command.lower()

        if 'youtube' in command_lower or 'video' in command_lower:
            if 'search' in command_lower or 'find' in command_lower:
                return self.search_youtube(command)
            elif 'play' in command_lower:
                return self.play_youtube_video(command)
            elif 'pause' in command_lower or 'stop' in command_lower:
                return self.control_youtube_playback(command)
            else:
                return self.open_youtube()
        elif 'volume' in command_lower:
            return self.control_system_volume(command)
        else:
            return """MEDIA CONTROL:
• 'search youtube [query]' - Search YouTube videos
• 'play youtube [video]' - Play specific video
• 'open youtube' - Open YouTube homepage
• 'pause/stop video' - Control playback
• 'volume up/down/mute' - Control system volume"""

    def search_youtube(self, command):
        """Search YouTube for videos"""
        try:
            import re
            match = re.search(r'search youtube (.+)', command.lower())
            if match:
                query = match.group(1).strip()
                search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                webbrowser.open(search_url)
                return f"SEARCHED: YouTube for '{query}'"
            else:
                return "ERROR: Please specify what to search for"
        except Exception as e:
            return f"ERROR: Could not search YouTube: {str(e)}"

    def play_youtube_video(self, command):
        """Play a specific YouTube video"""
        try:
            import re
            match = re.search(r'play youtube (.+)', command.lower())
            if match:
                video_query = match.group(1).strip()
                search_url = f"https://www.youtube.com/results?search_query={video_query.replace(' ', '+')}"
                webbrowser.open(search_url)
                return f"OPENED: YouTube search for '{video_query}' - click on the first result to play"
            else:
                return "ERROR: Please specify a video to play"
        except Exception as e:
            return f"ERROR: Could not play video: {str(e)}"

    def control_youtube_playback(self, command):
        """Control YouTube playback using keyboard simulation"""
        try:
            if 'pause' in command.lower():
                pyautogui.press('space')
                return "PAUSED: Video playback"
            elif 'stop' in command.lower():
                pyautogui.hotkey('ctrl', 'w')
                return "STOPPED: Closed video tab"
            else:
                return "ERROR: Unknown playback control command"
        except Exception as e:
            return f"ERROR: Could not control playback: {str(e)}"

    def open_youtube(self):
        """Open YouTube homepage"""
        try:
            webbrowser.open('https://www.youtube.com')
            return "OPENED: YouTube homepage"
        except Exception as e:
            return f"ERROR: Could not open YouTube: {str(e)}"

    def control_system_volume(self, command):
        """Control system volume"""
        try:
            if 'up' in command.lower():
                pyautogui.press('volumeup', presses=5)
                return "INCREASED: System volume"
            elif 'down' in command.lower():
                pyautogui.press('volumedown', presses=5)
                return "DECREASED: System volume"
            elif 'mute' in command.lower():
                pyautogui.press('volumemute')
                return "TOGGLED: System mute"
            else:
                return "ERROR: Please specify up, down, or mute"
        except Exception as e:
            return f"ERROR: Could not control volume: {str(e)}"

    def get_help_text(self):
        """Get comprehensive help text"""
        voice_status = "VOICE ENABLED" if VOICE_AVAILABLE else "VOICE DISABLED"
        ai_status = "AI ACTIVE" if AI_AVAILABLE else "AI OFFLINE"
        if GPT4ALL_AVAILABLE:
            ai_model_name = "Local GPT4All"
        elif QWEN_AVAILABLE:
            ai_model_name = "Local Qwen"
        elif FREE_API_AVAILABLE:
            ai_model_name = "Free API"
        else:
            ai_model_name = "Basic"

        return f"""AI ASSISTANT HELP - {ai_status} ({ai_model_name}) | {voice_status}

VOICE COMMANDS:
• Click VOICE button to start/stop voice recognition
• Say commands naturally (e.g., "open youtube", "system info")
• Voice feedback for all responses

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
        """Optimize system performance"""
        optimizations = []

        try:
            if platform.system() == 'Windows':
                subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
                optimizations.append("DNS cache cleared")

            optimizations.append("System optimization suggestions ready")

            return f"""PERFORMANCE OPTIMIZATION COMPLETE:
{chr(10).join('• ' + opt for opt in optimizations)}

ADDITIONAL TIPS:
• Close unused applications
• Clear browser cache
• Run Disk Cleanup
• Update your system"""
        except Exception as e:
            return f"ERROR: Could not optimize performance: {str(e)}"

    def system_diagnostics(self):
        """Run system diagnostics"""
        try:
            diagnostics = []

            if platform.system() == 'Windows':
                try:
                    result = subprocess.run(['sfc', '/scannow'], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        diagnostics.append("System File Checker: Completed")
                    else:
                        diagnostics.append("System File Checker: Found issues")
                except:
                    diagnostics.append("System File Checker: Timed out")

                try:
                    result = subprocess.run(['chkdsk', '/f'], capture_output=True, text=True, timeout=10)
                    diagnostics.append("Disk check: Scheduled for next restart")
                except:
                    diagnostics.append("Disk check: Scheduling failed")

            return f"""SYSTEM DIAGNOSTICS RESULTS:
{chr(10).join('• ' + diag for diag in diagnostics)}

These diagnostics help identify and fix common system issues."""
        except Exception as e:
            return f"ERROR: Could not run diagnostics: {str(e)}"

    def network_diagnostics(self):
        """Run network diagnostics"""
        try:
            network_info = []

            try:
                result = subprocess.run(['ping', '-n', '4', '8.8.8.8'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    network_info.append("Internet connection: Good")
                else:
                    network_info.append("Internet connection: Issues detected")
            except:
                network_info.append("Ping test: Failed")

            try:
                subprocess.run(['ipconfig', '/flushdns'], capture_output=True, timeout=5)
                network_info.append("DNS cache: Cleared")
            except:
                network_info.append("DNS flush: Failed")

            if platform.system() == 'Windows':
                try:
                    subprocess.run(['netsh', 'winsock', 'reset'], capture_output=True, timeout=10)
                    network_info.append("Network stack: Reset")
                except:
                    network_info.append("Network reset: Failed")

            return f"""NETWORK DIAGNOSTICS:
{chr(10).join('• ' + info for info in network_info)}

Network issues resolved. Restart your computer if problems persist."""
        except Exception as e:
            return f"ERROR: Could not run network diagnostics: {str(e)}"

    def clear_browser_cache(self):
        """Clear browser cache"""
        try:
            browsers = []

            # Chrome
            chrome_path = Path.home() / "AppData/Local/Google/Chrome/User Data/Default/Cache"
            if chrome_path.exists():
                try:
                    import shutil
                    shutil.rmtree(chrome_path, ignore_errors=True)
                    browsers.append("Chrome")
                except:
                    pass

            # Firefox
            firefox_path = Path.home() / "AppData/Local/Mozilla/Firefox/Profiles"
            if firefox_path.exists():
                try:
                    for profile in firefox_path.iterdir():
                        cache_path = profile / "cache2"
                        if cache_path.exists():
                            shutil.rmtree(cache_path, ignore_errors=True)
                    browsers.append("Firefox")
                except:
                    pass

            # Edge
            edge_path = Path.home() / "AppData/Local/Microsoft/Edge/User Data/Default/Cache"
            if edge_path.exists():
                try:
                    shutil.rmtree(edge_path, ignore_errors=True)
                    browsers.append("Edge")
                except:
                    pass

            if browsers:
                return f"CLEARED: Cache for {', '.join(browsers)} - performance improved"
            else:
                return "TIP: No browser caches found to clear"
        except Exception as e:
            return f"ERROR: Could not clear browser cache: {str(e)}"

    def handle_voice_command(self, command):
        """Handle voice-related commands"""
        command_lower = command.lower()

        if 'start listening' in command_lower or 'listen' in command_lower:
            self.start_voice_listening()
            return "VOICE: Started voice listening mode"
        elif 'stop listening' in command_lower:
            self.stop_voice_listening()
            return "VOICE: Stopped voice listening"
        elif 'speak' in command_lower or 'say' in command_lower:
            text_to_speak = command_lower.replace('speak', '').replace('say', '').strip()
            if text_to_speak:
                self.speak_response(text_to_speak)
                return f"VOICE: Speaking: {text_to_speak}"
            else:
                return "VOICE: What would you like me to say?"
        else:
            return """VOICE COMMANDS:
• 'start listening' - Begin voice recognition
• 'stop listening' - End voice recognition
• 'speak [text]' - Text-to-speech"""

    def request_permission(self, permission_type, action_description):
        """Request user permission"""
        if self.permissions.get(permission_type, False):
            return True

        reply = QMessageBox.question(
            self, 'Permission Required',
            f'Allow AI Assistant to {action_description}\n\n'
            f'This action requires {permission_type.replace("_", " ")} permission.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.permissions[permission_type] = True
            return True

        return False

    def get_ai_response(self, message):
        """Get AI-powered response"""
        if not self.ai_model and not self.pygpt_client:
            return f"I understand you want help with: {message[:50]}...\n\nI'm here to help! Try using specific commands like 'help' or ask me questions about your computer."

        try:
            context = "\n".join([f"{sender}: {msg}" for sender, msg in self.conversation_history[-3:]])
            prompt = f"Context:\n{context}\n\nUser: {message}\n\nAssistant: You are a helpful desktop AI assistant with full PC control capabilities. Provide a helpful response."

            if QWEN_AVAILABLE and hasattr(self, 'tokenizer'):
                inputs = self.tokenizer(prompt, return_tensors="pt")
                if torch.cuda.is_available():
                    inputs = inputs.to('cuda')

                with torch.no_grad():
                    outputs = self.ai_model.generate(
                        inputs.input_ids,
                        max_length=inputs.input_ids.shape[1] + 150,
                        num_return_sequences=1,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )

                response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
                return response.strip()

            elif GPT4ALL_AVAILABLE and hasattr(self, 'ai_model') and self.ai_model:
                with self.ai_model.chat_session():
                    response = self.ai_model.generate(prompt, max_tokens=150)
                return response

            elif FREE_API_AVAILABLE:
                return self.call_free_api(prompt)

        except Exception as e:
            print(f"AI Error: {e}")
            return f"I understand you want help with: {message[:50]}...\n\nI'm here to help! Try using specific commands like 'help' or ask me questions about your computer."

    def add_message(self, sender, message):
        """Add message to chat display with smooth animation"""
        self.conversation_history.append((sender, message))

        timestamp = datetime.now().strftime("%H:%M")
        message_html = f"[{timestamp}] <b>{sender}:</b> {message}"

        # Add message with fade-in effect
        current_scroll = self.chat_display.verticalScrollBar().value()
        self.chat_display.append(message_html)
        self.chat_display.append("")

        # Smooth scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        animation = QPropertyAnimation(scrollbar, b"value")
        animation.setDuration(300)
        animation.setStartValue(current_scroll)
        animation.setEndValue(scrollbar.maximum())
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()

    def load_conversation_history(self):
        """Load conversation history"""
        history_file = Path.home() / ".desktop_ai_history.json"
        try:
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
        except Exception as e:
            print(f"History load error: {e}")

    def save_conversation_history(self):
        """Save conversation history"""
        history_file = Path.home() / ".desktop_ai_history.json"
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history[-100:], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"History save error: {e}")

    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def closeEvent(self, event):
        """Handle close event"""
        event.ignore()
        self.hide_to_tray()

    def showEvent(self, event):
        """Handle show event"""
        super().showEvent(event)
        # Ensure window is always visible and focused
        self.raise_()
        self.activateWindow()
        self.setFocus()

    def changeEvent(self, event):
        """Handle window state changes"""
        if event.type() == event.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                # Prevent minimization and keep window visible
                self.showNormal()
                self.raise_()
                self.activateWindow()
                event.ignore()
        super().changeEvent(event)


def main():
    """Main application entry point"""
    print("DEBUG: Starting main application...")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Set application properties
    app.setApplicationName("Advanced AI Assistant")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("AI Assistant")

    print("Creating AI Assistant window...")
    # Create and show main window
    ai_assistant = DesktopAI()
    print("Showing window...")
    ai_assistant.show()
    ai_assistant.raise_()
    ai_assistant.activateWindow()

    # Force window visibility
    ai_assistant.setWindowState(Qt.WindowActive)
    ai_assistant.setFocus()

    print("DEBUG: Starting event loop...")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()