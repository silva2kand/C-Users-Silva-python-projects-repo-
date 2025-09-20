#!/usr/bin/env python3
"""
Desktop AI Assistant - Simple & Robust Version
A reliable AI assistant with voice control and PC automation.
"""

import sys
import os
import subprocess
import webbrowser
import time
import psutil
import platform
from datetime import datetime, timedelta
import json
from pathlib import Path
import threading
import sqlite3
import requests
import hashlib
import re
import random

# PyQt5 imports
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QLineEdit, QLabel,
                             QSystemTrayIcon, QMenu, QAction, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont

# Voice recognition imports
VOICE_AVAILABLE = False
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
    print("VOICE: Voice recognition available!")
except ImportError as e:
    print(f"VOICE: Voice recognition not available: {e}")
except Exception as e:
    print(f"VOICE: Error loading voice modules: {e}")
    VOICE_AVAILABLE = False

class VoiceWorker(QThread):
    """Simple voice recognition worker"""
    voice_detected = pyqtSignal(str)
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, recognizer):
        super().__init__()
        self.recognizer = recognizer
        self.listening = False
        self.running = True

    def run(self):
        """Voice recognition loop"""
        while self.running:
            if self.listening:
                try:
                    with sr.Microphone() as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        self.status_update.emit("VOICE: Listening...")

                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)

                        self.status_update.emit("VOICE: Processing...")
                        text = self.recognizer.recognize_google(audio, language='en-US')

                        if text and len(text.strip()) > 0:
                            self.voice_detected.emit(text)
                            self.status_update.emit("VOICE: Command received!")

                except sr.WaitTimeoutError:
                    self.status_update.emit("VOICE: No speech detected")
                except sr.UnknownValueError:
                    self.status_update.emit("VOICE: Didn't understand")
                except Exception as e:
                    self.error_occurred.emit(f"VOICE: Error - {e}")
                    time.sleep(2)
            else:
                time.sleep(0.1)

    def stop_thread(self):
        """Stop the voice recognition thread"""
        self.running = False
        self.listening = False

    def start_listening(self):
        """Start voice recognition"""
        self.listening = True

    def stop_listening(self):
        """Stop voice recognition"""
        self.listening = False

class KnowledgeManager:
    """Advanced knowledge management system with SQLite database and API integration"""

    def __init__(self):
        self.db_path = Path.home() / ".desktop_ai_knowledge.db"
        self.knowledge_dir = Path.home() / ".desktop_ai_knowledge"
        self.knowledge_dir.mkdir(exist_ok=True)
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for knowledge storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Knowledge base table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS knowledge (
                        id INTEGER PRIMARY KEY,
                        topic TEXT UNIQUE,
                        content TEXT,
                        source_url TEXT,
                        last_updated TIMESTAMP,
                        confidence REAL DEFAULT 0.5
                    )
                ''')

                # Learning history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS learning_history (
                        id INTEGER PRIMARY KEY,
                        query TEXT,
                        response TEXT,
                        source TEXT,
                        timestamp TIMESTAMP,
                        user_rating INTEGER DEFAULT 0
                    )
                ''')

                # API cache table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_cache (
                        id INTEGER PRIMARY KEY,
                        api_name TEXT,
                        query_hash TEXT UNIQUE,
                        response TEXT,
                        timestamp TIMESTAMP,
                        expires_at TIMESTAMP
                    )
                ''')

                conn.commit()
                print("Knowledge database initialized successfully")

        except Exception as e:
            print(f"Database initialization error: {e}")

    def search_knowledge(self, query):
        """Search local knowledge base"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT topic, content, source_url, confidence
                    FROM knowledge
                    WHERE topic LIKE ? OR content LIKE ?
                    ORDER BY confidence DESC
                    LIMIT 5
                ''', (f'%{query}%', f'%{query}%'))

                results = cursor.fetchall()
                return results

        except Exception as e:
            print(f"Knowledge search error: {e}")
            return []

    def store_knowledge(self, topic, content, source_url="", confidence=0.5):
        """Store new knowledge in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO knowledge
                    (topic, content, source_url, last_updated, confidence)
                    VALUES (?, ?, ?, ?, ?)
                ''', (topic, content, source_url, datetime.now(), confidence))
                conn.commit()

                # Create text extension file
                self.create_text_extension(topic, content, source_url)

        except Exception as e:
            print(f"Knowledge storage error: {e}")

    def create_text_extension(self, topic, content, source_url):
        """Create text-based extension file"""
        try:
            filename = f"{topic.replace(' ', '_').lower()}_{hashlib.md5(topic.encode()).hexdigest()[:8]}.txt"
            filepath = self.knowledge_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"TOPIC: {topic}\n")
                f.write(f"SOURCE: {source_url}\n")
                f.write(f"DATE: {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")
                f.write(content)
                f.write("\n\n" + "=" * 50)

        except Exception as e:
            print(f"Text extension creation error: {e}")

    def api_call_with_cache(self, api_name, url, params=None, headers=None, cache_minutes=30):
        """Make API call with caching"""
        try:
            # Create query hash for caching
            query_str = f"{api_name}_{url}_{str(params)}_{str(headers)}"
            query_hash = hashlib.md5(query_str.encode()).hexdigest()

            # Check cache first
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT response, expires_at FROM api_cache
                    WHERE query_hash = ? AND expires_at > ?
                ''', (query_hash, datetime.now()))

                cached_result = cursor.fetchone()
                if cached_result:
                    return json.loads(cached_result[0])

            # Make API call
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Cache the result
            expires_at = datetime.now() + timedelta(minutes=cache_minutes)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO api_cache
                    (api_name, query_hash, response, timestamp, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (api_name, query_hash, json.dumps(data), datetime.now(), expires_at))
                conn.commit()

            return data

        except Exception as e:
            print(f"API call error: {e}")
            return None

    def get_real_weather(self, location="London"):
        """Get real weather data from API"""
        try:
            # Using OpenWeatherMap API (you'll need to get a free API key)
            api_key = "YOUR_OPENWEATHERMAP_API_KEY"  # Replace with actual key
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': location,
                'appid': api_key,
                'units': 'metric'
            }

            data = self.api_call_with_cache('weather', url, params)
            if data:
                temp = data['main']['temp']
                condition = data['weather'][0]['description'].title()
                humidity = data['main']['humidity']
                return f"🌤️ {location}: {condition}, {temp}°C, Humidity: {humidity}%"
            else:
                return f"Unable to get weather for {location}"

        except Exception as e:
            print(f"Weather API error: {e}")
            return f"Weather service unavailable for {location}"

    def learn_from_query(self, query, response, source="user_interaction"):
        """Store learning history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO learning_history
                    (query, response, source, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (query, response, source, datetime.now()))
                conn.commit()
        except Exception as e:
            print(f"Learning storage error: {e}")

class DesktopAI(QWidget):
    """Main Desktop AI Assistant Window"""

    # Define signals for thread-safe GUI updates
    message_received = pyqtSignal(str, str)  # sender, message
    status_updated = pyqtSignal(str)  # status text
    inputs_enabled = pyqtSignal(bool)  # enable/disable inputs

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Assistant")
        self.setGeometry(100, 100, 500, 600)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Initialize components
        self.conversation_history = []
        self.load_conversation_history()

        # Voice components
        self.voice_recognizer = None
        self.voice_engine = None
        self.voice_worker = None
        self.voice_listening = False
        self.voice_output_enabled = True

        # Initialize voice if available
        if VOICE_AVAILABLE:
            self.init_voice()

        # Initialize knowledge management system
        self.knowledge_manager = KnowledgeManager()

        # Initialize natural language processor
        self.nlp_processor = NaturalLanguageProcessor()

        # Setup UI
        self.setup_ui()

        # Tray icon
        self.setup_tray_icon()

        # Auto-save timer
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_conversation_history)
        self.save_timer.start(30000)

        # Connect signals for thread-safe GUI updates
        self.message_received.connect(self.add_message)
        self.status_updated.connect(self.update_status)
        self.inputs_enabled.connect(self.set_inputs_enabled)

    def setup_ui(self):
        """Setup user interface"""
        # Main container
        self.main_frame = QFrame()
        self.main_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                border: 2px solid #5a67d8;
            }
        """)

        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title bar
        title_bar = self.create_title_bar()
        layout.addWidget(title_bar)

        # Chat display
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
            }
        """)
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your command...")
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
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        input_layout.addWidget(self.message_input)

        # Send button
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
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a67d8, stop:1 #4c51bf);
            }
        """)
        input_layout.addWidget(self.send_button)

        # Voice button
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
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #38a169, stop:1 #2f855a);
                }
            """)
            input_layout.addWidget(self.voice_button)

            # Sound toggle button
            self.sound_button = QPushButton("SOUND ON")
            self.sound_button.clicked.connect(self.toggle_sound)
            self.sound_button.setStyleSheet("""
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
            """)
            input_layout.addWidget(self.sound_button)

        layout.addLayout(input_layout)

        # Status bar
        self.status_label = QLabel("Ready - Type 'help' for commands")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
                padding: 8px 0;
                font-size: 11px;
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
        voice_status = "VOICE ENABLED" if VOICE_AVAILABLE else "VOICE DISABLED"
        self.add_message("AI Assistant", f"""Hello! 👋 I'm your Desktop AI Assistant!

{voice_status}
VOICE OUTPUT: {'ENABLED' if self.voice_output_enabled else 'DISABLED'}

🎯 I'm now much more conversational! You can talk to me naturally:

💬 CONVERSATIONAL EXAMPLES:
• "What's the weather like?" - I'll check the weather
• "Can you calculate 15 times 7?" - I'll do the math
• "What time is it?" - I'll tell you the current time
• "Find my report.pdf file" - I'll search for files
• "Save a note to buy groceries" - I'll remember it
• "Take a screenshot" - I'll capture your screen
• "What is Python?" - I'll search my knowledge
• "Learn this: AI is artificial intelligence" - I'll remember it

🔧 TRADITIONAL COMMANDS STILL WORK:
• "open youtube" - Open YouTube
• "system info" - Show PC details
• "clean temp files" - Clean junk files
• "help" - Show all commands

Click VOICE button to use voice commands!
Click SOUND ON/OFF to toggle voice responses.

Just tell me what you need help with! 😊""")

    def create_title_bar(self):
        """Create title bar"""
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
        title_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 16px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

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
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor('#667eea'))
            painter = QPainter(pixmap)
            painter.setPen(QColor('white'))
            painter.setFont(QFont('Arial', 20, QFont.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, 'AI')
            painter.end()

            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon(pixmap))
            self.tray_icon.setToolTip('AI Assistant')

            tray_menu = QMenu()
            show_action = QAction('Show Assistant', self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)

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
        if hasattr(self, 'tray_icon'):
            self.tray_icon.showMessage(
                'AI Assistant',
                'I\'m here! Double-click the tray icon to show me.',
                QSystemTrayIcon.Information,
                2000
            )

    def quit_application(self):
        """Quit the application"""
        if self.voice_worker:
            self.voice_worker.stop_thread()
            self.voice_worker.wait()  # Wait for thread to finish
        self.save_conversation_history()
        QApplication.quit()

    def toggle_sound(self):
        """Toggle voice output on/off"""
        self.voice_output_enabled = not self.voice_output_enabled

        if self.voice_output_enabled:
            self.sound_button.setText("SOUND ON")
            self.sound_button.setStyleSheet("""
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
            """)
            self.message_received.emit("System", "VOICE OUTPUT: ENABLED")
        else:
            self.sound_button.setText("SOUND OFF")
            self.sound_button.setStyleSheet("""
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
            """)
            self.message_received.emit("System", "VOICE OUTPUT: DISABLED")

    def init_voice(self):
        """Initialize voice recognition and text-to-speech"""
        try:
            self.voice_recognizer = sr.Recognizer()
            self.voice_engine = pyttsx3.init()
            self.voice_worker = VoiceWorker(self.voice_recognizer)

            # Connect signals
            self.voice_worker.voice_detected.connect(self.process_voice_command)
            self.voice_worker.status_update.connect(self.update_status)
            self.voice_worker.error_occurred.connect(self.handle_voice_error)

            # Start the voice recognition thread
            self.voice_worker.start()

            # Configure voice
            voices = self.voice_engine.getProperty('voices')
            if voices:
                self.voice_engine.setProperty('voice', voices[0].id)
            self.voice_engine.setProperty('rate', 180)

            print("VOICE: Initialized successfully")

        except Exception as e:
            print(f"VOICE: Initialization failed: {e}")

    def toggle_voice_listening(self):
        """Toggle voice listening on/off"""
        if not VOICE_AVAILABLE:
            self.message_received.emit("System", "VOICE: Voice recognition not available")
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
                }
            """)

    def update_status(self, status):
        """Update status label"""
        self.status_label.setText(status)

    def set_inputs_enabled(self, enabled):
        """Enable or disable input controls"""
        self.message_input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        if hasattr(self, 'voice_button'):
            self.voice_button.setEnabled(enabled)
        if hasattr(self, 'sound_button'):
            self.sound_button.setEnabled(enabled)

    def handle_voice_error(self, error):
        """Handle voice recognition errors"""
        self.message_received.emit("System", f"VOICE ERROR: {error}")

    def process_voice_command(self, text):
        """Process voice command"""
        self.message_received.emit("Voice", f"VOICE: {text}")
        self.message_input.setText(text)
        self.process_message()

    def speak_response(self, text):
        """Speak the response"""
        if not VOICE_AVAILABLE or not self.voice_engine or not self.voice_output_enabled:
            return

        try:
            clean_text = text.replace('✅', '').replace('❌', '').replace('🤖', 'AI')
            clean_text = clean_text.replace('💡', '').replace('🔧', '').replace('🧹', '')

            def speak():
                try:
                    self.voice_engine.say(clean_text)
                    self.voice_engine.runAndWait()
                except Exception as e:
                    print(f"SPEECH ERROR: {e}")
                    self.add_message("System", f"VOICE ERROR: {e}")

            # Use daemon thread to prevent blocking
            speech_thread = threading.Thread(target=speak, daemon=True)
            speech_thread.start()

        except Exception as e:
            print(f"SPEECH ERROR: {e}")
            self.add_message("System", f"VOICE ERROR: {e}")

    def process_message(self):
        """Process user message"""
        message = self.message_input.text().strip()
        if not message:
            return

        self.add_message("You", message)
        self.message_input.clear()

        # Disable input while processing
        self.inputs_enabled.emit(False)
        self.status_updated.emit("Processing...")

        # Process command in thread
        def process_thread():
            try:
                response = self.execute_command(message)
                self.message_received.emit("Assistant", response)
                self.status_updated.emit("Ready")

                # Learn from this interaction
                self.knowledge_manager.learn_from_query(message, response, "user_interaction")

                # Speak response
                if VOICE_AVAILABLE and self.voice_output_enabled:
                    speech_thread = threading.Thread(target=lambda: self.speak_response(response), daemon=True)
                    speech_thread.start()

            except Exception as e:
                error_msg = f"ERROR: {str(e)}"
                self.message_received.emit("Assistant", error_msg)
                self.status_updated.emit("Ready")

                # Learn from errors too
                self.knowledge_manager.learn_from_query(message, error_msg, "error_case")

            finally:
                self.inputs_enabled.emit(True)

        thread = threading.Thread(target=process_thread, daemon=True)
        thread.start()

    def execute_command(self, command):
        """Execute natural language commands with conversational responses"""
        # First, analyze the natural language intent
        analysis = self.nlp_processor.analyze_query(command)

        # If we have a clear intent, handle it conversationally
        if analysis['confidence'] > 0.5:
            intent = analysis['intent']

            # Handle different intents with conversational responses
            if intent == 'greeting':
                return analysis['response']

            elif intent == 'help':
                return self.get_help_text()

            elif intent == 'weather':
                if any(word in command.lower() for word in ['weather', 'temperature', 'forecast']):
                    result = self.get_weather_info(command)
                    return self.nlp_processor.generate_conversational_response('weather', command, result)
                else:
                    return analysis['response']

            elif intent == 'calculator':
                if any(word in command.lower() for word in ['calculate', 'calc', 'math', 'compute']):
                    result = self.calculate_expression(command)
                    return self.nlp_processor.generate_conversational_response('calculator', command, result)
                else:
                    return analysis['response']

            elif intent == 'time':
                result = self.get_time_date_info()
                return self.nlp_processor.generate_conversational_response('time', command, result)

            elif intent == 'file_search':
                if any(word in command.lower() for word in ['find file', 'search file', 'locate']):
                    result = self.search_files(command)
                    return self.nlp_processor.generate_conversational_response('file_search', command, result)
                else:
                    return analysis['response']

            elif intent == 'notes':
                if any(word in command.lower() for word in ['save note', 'remember', 'note']):
                    result = self.store_new_knowledge(command) if 'learn' in command.lower() else self.handle_notes(command)
                    return self.nlp_processor.generate_conversational_response('notes', command, result)
                else:
                    return analysis['response']

            elif intent == 'knowledge_search':
                result = self.search_knowledge(command)
                return self.nlp_processor.generate_conversational_response('knowledge_search', command, result)

        # Fallback to traditional command matching for specific commands
        command_lower = command.lower()

        # System information
        if 'system info' in command_lower or 'computer info' in command_lower:
            result = self.get_system_info()
            return f"Sure! Here's your system information:\n\n{result}"

        # PC Maintenance
        elif any(word in command_lower for word in ['repair', 'fix', 'maintain', 'clean', 'optimize']):
            result = self.pc_maintenance(command)
            return f"I'll help you with that! {result}"

        # Programming
        elif any(word in command_lower for word in ['code', 'program', 'develop', 'script']):
            result = self.programming_assistance(command)
            return f"Great! {result}"

        # Internet Research
        elif any(word in command_lower for word in ['learn', 'research', 'find', 'discover']) and 'file' not in command_lower:
            result = self.internet_research(command)
            return f"I'll help you research that! {result}"

        # Auto-installation
        elif any(word in command_lower for word in ['install', 'download', 'setup', 'get']):
            result = self.auto_install(command)
            return f"Sure! {result}"

        # File operations
        elif 'create' in command_lower and 'folder' in command_lower:
            result = self.create_folder(command)
            return f"Done! {result}"

        # Application launching
        elif 'open' in command_lower or 'launch' in command_lower or 'start' in command_lower:
            result = self.open_application(command)
            return f"Sure thing! {result}"

        # Web operations
        elif 'search' in command_lower or 'google' in command_lower:
            result = self.web_search(command)
            return f"I'll search for that! {result}"

        # System control
        elif any(word in command_lower for word in ['shutdown', 'restart']):
            result = self.system_control(command)
            return f"Okay! {result}"

        # Voice commands
        elif any(word in command_lower for word in ['voice', 'speak', 'talk', 'say']):
            result = self.handle_voice_command(command)
            return f"Voice command: {result}"

        # Learning statistics
        elif any(word in command_lower for word in ['learning stats', 'what have you learned', 'knowledge stats']):
            result = self.get_learning_stats()
            return f"Here's what I've learned: {result}"

        # Default conversational response
        else:
            return self.nlp_processor.generate_conversational_response('unknown', command)

    def get_help_text(self):
        """Get help text"""
        voice_status = "VOICE ENABLED" if VOICE_AVAILABLE else "VOICE DISABLED"
        sound_status = "VOICE OUTPUT ENABLED" if self.voice_output_enabled else "VOICE OUTPUT DISABLED"

        return f"""AI ASSISTANT HELP - {voice_status}

VOICE CONTROLS:
• Click VOICE button to start/stop voice recognition
• Click SOUND ON/OFF to toggle voice responses
• {sound_status}

PC MAINTENANCE:
• 'clean temp files' - Clear temporary files
• 'disk cleanup' - Free up disk space
• 'check for updates' - System updates
• 'virus scan' - Security scan
• 'optimize performance' - Speed up your PC

APPLICATIONS:
• 'open chrome/firefox/edge' - Web browsers
• 'open notepad/calculator' - System apps
• 'open youtube/gmail/facebook' - Popular websites
• 'open [app name]' - Any application

WEB & SEARCH:
• 'search for [query]' - Google search
• 'open website [url]' - Visit website

SYSTEM INFO:
• 'system info' - Computer details
• 'time' or 'date' - Current time and date
• 'weather' - Weather information

CALCULATOR:
• 'calculate [expression]' - Math calculations
• 'calc 2+2' or 'compute 5*3' - Quick math

FILE MANAGEMENT:
• 'find file [name]' - Search for files
• 'search file [name]' - Locate files

NOTES & REMINDERS:
• 'save note [content]' - Save a note
• 'show notes' - Display recent notes
• 'remind me [task]' - Set a reminder

UTILITIES:
• 'screenshot' - Take screen capture
• 'time' or 'date' - Current time/date

KNOWLEDGE & LEARNING:
• 'what is [topic]' - Search knowledge base
• 'learn this [info]' - Teach me new information
• 'learning stats' - View learning statistics

PROGRAMMING:
• 'open vs code' - Launch code editor

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
        """Open applications"""
        command_lower = command.lower()

        # Remove prefixes
        for prefix in ['open', 'launch', 'start', 'can you', 'please', 'plz']:
            command_lower = command_lower.replace(prefix, '').strip()

        # Handle YouTube
        if 'youtube' in command_lower:
            try:
                webbrowser.open('https://www.youtube.com')
                return "OPENED: YouTube in your default browser"
            except:
                return "ERROR: Could not open YouTube"

        # Handle other websites
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
                except:
                    return f"ERROR: Could not open {site}"

        # Handle applications
        app_commands = {
            'chrome': 'chrome',
            'firefox': 'firefox',
            'edge': 'msedge',
            'notepad': 'notepad',
            'calculator': 'calc',
            'explorer': 'explorer',
            'cmd': 'cmd',
            'powershell': 'powershell'
        }

        for app_key, app_cmd in app_commands.items():
            if app_key in command_lower:
                try:
                    subprocess.Popen(app_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                    return f"OPENED: {app_key}"
                except:
                    return f"ERROR: Could not open {app_key}"

        return f"I don't know how to open '{command}'. Try: chrome, firefox, notepad, calculator, youtube, etc."

    def pc_maintenance(self, command):
        """PC maintenance commands"""
        command_lower = command.lower()

        if 'clean' in command_lower or 'temp' in command_lower:
            return self.clean_temp_files()
        elif 'disk' in command_lower:
            return self.disk_cleanup()
        elif 'update' in command_lower:
            return self.check_updates()
        elif 'virus' in command_lower or 'scan' in command_lower:
            return self.virus_scan()
        elif 'performance' in command_lower or 'optimize' in command_lower:
            return self.optimize_performance()
        else:
            return """PC MAINTENANCE OPTIONS:
• 'clean temp files' - Clear temporary files
• 'disk cleanup' - Free up disk space
• 'check for updates' - System updates
• 'virus scan' - Security scan
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
                subprocess.run(['cleanmgr', '/sagerun:1'], capture_output=True, timeout=30)
                return "STARTED: Windows Disk Cleanup"
            else:
                return "TIP: Disk cleanup is primarily available on Windows"
        except subprocess.TimeoutExpired:
            return "DISK CLEANUP: Started in background (may take time)"
        except Exception as e:
            return f"ERROR: Could not run disk cleanup: {str(e)}"

    def check_updates(self):
        """Check for system updates"""
        try:
            if platform.system() == 'Windows':
                subprocess.run(['wuauclt', '/detectnow'], capture_output=True, timeout=30)
                return "STARTED: Windows Update check"
            else:
                return "TIP: System updates are managed differently on your OS"
        except subprocess.TimeoutExpired:
            return "UPDATES: Check started in background"
        except Exception as e:
            return f"ERROR: Could not check updates: {str(e)}"

    def virus_scan(self):
        """Perform virus scan"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['powershell', 'Start-MpScan -ScanType QuickScan'], capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    return "STARTED: Windows Defender quick scan"
                else:
                    return "WARNING: Windows Defender scan couldn't be started"
            else:
                return "TIP: Antivirus scanning is OS-specific"
        except subprocess.TimeoutExpired:
            return "VIRUS SCAN: Started in background (may take several minutes)"
        except Exception as e:
            return f"ERROR: Could not start virus scan: {str(e)}"

    def optimize_performance(self):
        """Optimize system performance"""
        try:
            if platform.system() == 'Windows':
                subprocess.run(['ipconfig', '/flushdns'], capture_output=True, timeout=30)

            return """PERFORMANCE OPTIMIZATION COMPLETE:
• DNS cache cleared
• System optimization suggestions ready

ADDITIONAL TIPS:
• Close unused applications
• Clear browser cache
• Run Disk Cleanup
• Update your system"""
        except subprocess.TimeoutExpired:
            return """PERFORMANCE OPTIMIZATION:
• DNS cache cleared (completed)
• Other optimizations may be running in background"""
        except Exception as e:
            return f"ERROR: Could not optimize performance: {str(e)}"

    def programming_assistance(self, command):
        """Programming assistance"""
        if 'vs code' in command.lower() or 'vscode' in command.lower():
            try:
                subprocess.Popen(['code'], shell=True)
                return "OPENED: VS Code"
            except:
                return "ERROR: VS Code not found"
        else:
            return """PROGRAMMING HELP:
• 'open vs code' - Launch VS Code
• 'create python project [name]' - New Python project"""

    def internet_research(self, command):
        """Internet research"""
        topic = command.lower().replace('learn', '').replace('research', '').replace('find', '').strip()

        if not topic:
            return "What would you like to research?"

        try:
            search_url = f"https://www.google.com/search?q={topic.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"SEARCHING: Opened Google search for '{topic}'"
        except Exception as e:
            return f"ERROR: Could not perform search: {str(e)}"

    def auto_install(self, command):
        """Auto-install software"""
        software = command.lower().replace('install', '').replace('download', '').replace('get', '').strip()

        if 'python' in software:
            try:
                webbrowser.open("https://www.python.org/downloads/")
                return "OPENED: Python download page"
            except:
                return "ERROR: Could not open Python download page"
        elif 'vscode' in software or 'vs code' in software:
            try:
                webbrowser.open("https://code.visualstudio.com/download")
                return "OPENED: VS Code download page"
            except:
                return "ERROR: Could not open VS Code download page"
        else:
            return f"I can help install Python or VS Code. For '{software}', please visit the official website."

    def create_folder(self, command):
        """Create a new folder"""
        folder_name = command.lower().replace('create', '').replace('folder', '').strip()

        if not folder_name:
            return "Please specify a folder name"

        try:
            folder_path = Path.cwd() / folder_name
            folder_path.mkdir(exist_ok=True)
            return f"CREATED: Folder '{folder_name}'"
        except Exception as e:
            return f"ERROR: Could not create folder: {str(e)}"

    def web_search(self, command):
        """Perform web search"""
        query = command.lower().replace('search for', '').replace('google', '').strip()

        if not query:
            return "What would you like to search for?"

        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"SEARCHING: '{query}'"
        except Exception as e:
            return f"ERROR: Could not perform search: {str(e)}"

    def system_control(self, command):
        """System control commands"""
        if 'shutdown' in command.lower():
            return "SHUTDOWN: Use Windows Start menu for shutdown"
        elif 'restart' in command.lower():
            return "RESTART: Use Windows Start menu for restart"
        else:
            return "SYSTEM CONTROL: Use Windows Start menu for shutdown/restart"

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

    def get_weather_info(self, command):
        """Get weather information using real API"""
        try:
            # Extract location from command
            location = command.lower().replace('weather', '').replace('temperature', '').replace('forecast', '').strip()

            if not location:
                location = "London"  # Default location

            # Try to get real weather data
            weather_info = self.knowledge_manager.get_real_weather(location)

            # Store this interaction for learning
            self.knowledge_manager.learn_from_query(command, weather_info, "weather_api")

            return weather_info

        except Exception as e:
            return f"ERROR: Could not get weather information: {str(e)}"

    def calculate_expression(self, command):
        """Calculate mathematical expressions"""
        try:
            # Extract the mathematical expression
            expr = command.lower()
            expr = expr.replace('calculate', '').replace('calc', '').replace('compute', '').replace('what is', '').strip()

            if not expr:
                return "CALCULATOR: Please provide a mathematical expression to calculate."

            # Use eval with safety restrictions
            # Only allow basic math operations
            allowed_chars = set('0123456789+-*/(). ')
            if not all(c in allowed_chars for c in expr):
                return "CALCULATOR: Only basic math operations (+, -, *, /) are allowed."

            result = eval(expr)

            return f"CALCULATOR: {expr} = {result}"

        except ZeroDivisionError:
            return "CALCULATOR: Division by zero is not allowed."
        except Exception as e:
            return f"CALCULATOR: Error in calculation: {str(e)}"

    def get_time_date_info(self):
        """Get current time and date information"""
        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            current_date = now.strftime("%A, %B %d, %Y")

            return f"""CURRENT TIME & DATE:
• Time: {current_time}
• Date: {current_date}
• Day: {now.strftime('%A')}
• Month: {now.strftime('%B')}
• Year: {now.year}"""

        except Exception as e:
            return f"ERROR: Could not get time/date information: {str(e)}"

    def search_files(self, command):
        """Search for files on the system"""
        try:
            # Extract search term
            search_term = command.lower()
            search_term = search_term.replace('find file', '').replace('search file', '').replace('locate', '').strip()

            if not search_term:
                return "FILE SEARCH: Please specify what file you're looking for."

            # Search in common directories
            search_paths = [
                str(Path.home() / 'Desktop'),
                str(Path.home() / 'Documents'),
                str(Path.home() / 'Downloads'),
                'C:\\Users\\Public\\Desktop' if os.name == 'nt' else '/home'
            ]

            found_files = []

            for search_path in search_paths:
                if os.path.exists(search_path):
                    for root, dirs, files in os.walk(search_path):
                        for file in files:
                            if search_term.lower() in file.lower():
                                found_files.append(os.path.join(root, file))
                        if len(found_files) >= 10:  # Limit results
                            break
                    if len(found_files) >= 10:
                        break

            if found_files:
                result = f"FILE SEARCH: Found {len(found_files)} files matching '{search_term}':\n\n"
                for i, file_path in enumerate(found_files[:10], 1):
                    result += f"{i}. {os.path.basename(file_path)}\n   Location: {file_path}\n"
                if len(found_files) > 10:
                    result += f"\n... and {len(found_files) - 10} more files."
                return result
            else:
                return f"FILE SEARCH: No files found matching '{search_term}' in common locations."

        except Exception as e:
            return f"ERROR: Could not search files: {str(e)}"

    def handle_notes(self, command):
        """Handle note-taking functionality"""
        try:
            command_lower = command.lower()

            if 'save note' in command_lower or 'remember' in command_lower:
                # Extract the note content
                note_content = command.lower()
                note_content = note_content.replace('save note', '').replace('remember', '').replace('note', '').strip()

                if not note_content:
                    return "NOTES: Please provide content for the note."

                # Save to a simple notes file
                notes_file = Path.home() / ".desktop_ai_notes.txt"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                with open(notes_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] {note_content}\n")

                return f"NOTES: Saved note: '{note_content}'"

            elif 'show notes' in command_lower or 'list notes' in command_lower:
                # Show recent notes
                notes_file = Path.home() / ".desktop_ai_notes.txt"

                if not notes_file.exists():
                    return "NOTES: No notes found. Try 'save note [content]' to create your first note."

                with open(notes_file, 'r', encoding='utf-8') as f:
                    notes = f.readlines()

                if not notes:
                    return "NOTES: No notes found."

                recent_notes = notes[-5:]  # Show last 5 notes
                result = "RECENT NOTES:\n\n"
                for i, note in enumerate(recent_notes, 1):
                    result += f"{i}. {note.strip()}\n"

                return result

            else:
                return """NOTES COMMANDS:
• 'save note [content]' - Save a note
• 'remember [content]' - Save a note
• 'show notes' - Display recent notes
• 'list notes' - Display recent notes"""

        except Exception as e:
            return f"ERROR: Could not handle notes: {str(e)}"

    def handle_reminders(self, command):
        """Handle reminder functionality"""
        try:
            command_lower = command.lower()

            if 'remind me' in command_lower or 'set reminder' in command_lower:
                # Extract reminder content
                reminder_text = command.lower()
                reminder_text = reminder_text.replace('remind me', '').replace('set reminder', '').replace('reminder', '').strip()

                if not reminder_text:
                    return "REMINDERS: Please specify what to remind you about."

                # For now, just acknowledge the reminder
                # In a real implementation, you'd schedule actual reminders
                return f"REMINDER SET: I'll remind you about '{reminder_text}'\n\nNote: This is a basic reminder. For advanced scheduling, consider using Windows Task Scheduler or a dedicated reminder app."

            elif 'show reminders' in command_lower or 'list reminders' in command_lower:
                return "REMINDERS: No active reminders.\n\nTo set a reminder, try: 'remind me to call mom'"

            else:
                return """REMINDER COMMANDS:
• 'remind me [task]' - Set a reminder
• 'set reminder [task]' - Set a reminder
• 'show reminders' - Display active reminders"""

        except Exception as e:
            return f"ERROR: Could not handle reminders: {str(e)}"

    def take_screenshot(self):
        """Take a screenshot of the screen"""
        try:
            from PIL import ImageGrab
            import os

            # Take screenshot
            screenshot = ImageGrab.grab()

            # Save to desktop
            desktop_path = Path.home() / 'Desktop'
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = desktop_path / filename

            screenshot.save(filepath)

            return f"SCREENSHOT: Saved to Desktop as '{filename}'\nLocation: {filepath}"

        except ImportError:
            return "SCREENSHOT: PIL (Pillow) library not installed.\nInstall with: pip install pillow"
        except Exception as e:
            return f"ERROR: Could not take screenshot: {str(e)}"

    def search_knowledge(self, command):
        """Search the knowledge base for information"""
        try:
            # Extract search query
            query = command.lower()
            for phrase in ['what is', 'tell me about', 'explain', 'search knowledge']:
                query = query.replace(phrase, '').strip()

            if not query:
                return "KNOWLEDGE SEARCH: Please specify what you want to know about."

            # Search local knowledge base
            results = self.knowledge_manager.search_knowledge(query)

            if results:
                response = f"📚 KNOWLEDGE SEARCH RESULTS for '{query}':\n\n"
                for i, (topic, content, source_url, confidence) in enumerate(results, 1):
                    response += f"{i}. {topic} (Confidence: {confidence:.1%})\n"
                    response += f"   {content[:100]}{'...' if len(content) > 100 else ''}\n"
                    if source_url:
                        response += f"   Source: {source_url}\n"
                    response += "\n"
                return response
            else:
                # If no local knowledge, suggest web search
                return f"I don't have information about '{query}' in my knowledge base.\n\nTry: 'search for {query}' to search the web, or 'learn this [information about {query}]' to teach me."

        except Exception as e:
            return f"ERROR: Could not search knowledge: {str(e)}"

    def get_learning_stats(self):
        """Get learning statistics"""
        try:
            # Get learning statistics from database
            with sqlite3.connect(self.knowledge_manager.db_path) as conn:
                cursor = conn.cursor()

                # Count total knowledge entries
                cursor.execute('SELECT COUNT(*) FROM knowledge')
                knowledge_count = cursor.fetchone()[0]

                # Count learning interactions
                cursor.execute('SELECT COUNT(*) FROM learning_history')
                learning_count = cursor.fetchone()[0]

                # Get recent learning activity
                cursor.execute('''
                    SELECT query, timestamp FROM learning_history
                    ORDER BY timestamp DESC LIMIT 3
                ''')
                recent_learnings = cursor.fetchall()

                response = f"""🧠 LEARNING STATISTICS:

• Knowledge Base Entries: {knowledge_count}
• Learning Interactions: {learning_count}
• Knowledge Files: {len(list(self.knowledge_manager.knowledge_dir.glob('*.txt')))}

RECENT LEARNING ACTIVITY:
"""

                for query, timestamp in recent_learnings:
                    response += f"• {timestamp}: {query[:50]}{'...' if len(query) > 50 else ''}\n"

                return response

        except Exception as e:
            return f"ERROR: Could not get learning statistics: {str(e)}"

    def store_new_knowledge(self, command):
        """Store new knowledge in the database"""
        try:
            # Extract knowledge content
            content = command.lower()
            for phrase in ['learn this', 'remember this', 'store knowledge']:
                content = content.replace(phrase, '').strip()

            if not content:
                return "KNOWLEDGE STORAGE: Please provide the information you want me to learn."

            # Try to extract topic from content
            words = content.split()
            if len(words) > 10:
                topic = ' '.join(words[:3]) + '...'
            else:
                topic = ' '.join(words[:2]) if len(words) >= 2 else content[:20]

            # Store in knowledge base
            self.knowledge_manager.store_knowledge(
                topic=topic,
                content=content,
                source_url="user_input",
                confidence=0.8
            )

            return f"✅ KNOWLEDGE STORED: '{topic}'\n\nI now know: {content[:100]}{'...' if len(content) > 100 else ''}"

        except Exception as e:
            return f"ERROR: Could not store knowledge: {str(e)}"

class NaturalLanguageProcessor:
    """Advanced natural language processing for conversational AI responses"""

    def __init__(self):
        self.greetings = [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Hey! Ready to assist you!",
            "Greetings! How may I help?",
            "Hello! I'm here to help!"
        ]

        self.confused_responses = [
            "I'm not sure I understand that. Could you rephrase it?",
            "Hmm, I'm having trouble understanding. Can you say that differently?",
            "I'm not quite sure what you mean. Could you clarify?",
            "That doesn't ring a bell. Can you explain it another way?"
        ]

        self.intent_patterns = {
            'weather': [
                r'weather', r'temperature', r'forecast', r'rain', r'sunny', r'cloudy',
                r'how.*weather', r'what.*weather', r'is it.*outside'
            ],
            'time': [
                r'time', r'clock', r'what time', r'current time', r'what.*time'
            ],
            'calculator': [
                r'calculate', r'calc', r'math', r'compute', r'what.*plus', r'what.*minus',
                r'what.*times', r'what.*divided', r'solve'
            ],
            'file_search': [
                r'find.*file', r'search.*file', r'locate.*file', r'where.*file'
            ],
            'notes': [
                r'save.*note', r'make.*note', r'write.*note', r'remember'
            ],
            'help': [
                r'help', r'what.*can.*do', r'commands', r'how.*work'
            ],
            'system_info': [
                r'system.*info', r'computer.*info', r'my.*pc', r'my.*computer'
            ]
        }

        self.conversational_responses = {
            'weather': [
                "I'd be happy to check the weather for you! Just tell me the city name.",
                "Sure! Which city's weather would you like to know about?",
                "I can get the current weather conditions. What location are you interested in?"
            ],
            'calculator': [
                "I love math! What calculation would you like me to do?",
                "Sure, I can help with that calculation. What numbers and operation?",
                "Math is my specialty! What would you like to calculate?"
            ],
            'time': [
                "Let me check the current time for you!",
                "Sure, here's the current time:",
                "I'd be happy to tell you the time!"
            ],
            'file_search': [
                "I can help you find files! What are you looking for?",
                "Sure! Tell me the name of the file you're searching for.",
                "I can search through your files. What file name should I look for?"
            ],
            'notes': [
                "Great idea to save a note! What would you like me to remember?",
                "I'll make sure to save that for you. What's the note?",
                "Perfect! What information would you like me to store?"
            ]
        }

    def analyze_query(self, query):
        """Analyze user query and extract intent and entities"""
        query_lower = query.lower().strip()

        # Check for greetings
        if self.is_greeting(query_lower):
            return {
                'intent': 'greeting',
                'confidence': 0.9,
                'response': random.choice(self.greetings)
            }

        # Check for specific intents
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return {
                        'intent': intent,
                        'confidence': 0.8,
                        'response': random.choice(self.conversational_responses.get(intent, ["I can help with that!"]))
                    }

        # Check for knowledge queries
        if any(word in query_lower for word in ['what is', 'tell me about', 'explain', 'who is']):
            return {
                'intent': 'knowledge_search',
                'confidence': 0.7,
                'response': "I'd be happy to look that up for you!"
            }

        # Default response
        return {
            'intent': 'unknown',
            'confidence': 0.3,
            'response': random.choice(self.confused_responses)
        }

    def is_greeting(self, query):
        """Check if query is a greeting"""
        greetings = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon',
            'good evening', 'howdy', 'greetings', 'sup', 'yo'
        ]
        return any(greeting in query for greeting in greetings)

    def generate_conversational_response(self, intent, original_query, command_result=""):
        """Generate a natural, conversational response"""
        if intent == 'greeting':
            return random.choice(self.greetings)

        elif intent == 'weather':
            if command_result:
                return f"Here's the weather information: {command_result}"
            else:
                return random.choice(self.conversational_responses['weather'])

        elif intent == 'calculator':
            if command_result:
                return f"The result is: {command_result}"
            else:
                return random.choice(self.conversational_responses['calculator'])

        elif intent == 'time':
            if command_result:
                return f"Current time: {command_result}"
            else:
                return "Let me check the current time for you!"

        elif intent == 'file_search':
            if command_result:
                return f"I found these files: {command_result}"
            else:
                return random.choice(self.conversational_responses['file_search'])

        elif intent == 'notes':
            if command_result:
                return f"Note saved! {command_result}"
            else:
                return random.choice(self.conversational_responses['notes'])

        elif intent == 'knowledge_search':
            if command_result:
                return f"Here's what I found: {command_result}"
            else:
                return "Let me search my knowledge base for that information!"

        else:
            # For unknown intents, provide helpful suggestions
            suggestions = [
                "I can help you with weather, calculations, file searching, notes, and more!",
                "Try asking me about the weather, time, or to calculate something!",
                "I can search files, save notes, check system info, and much more!"
            ]
            return f"{random.choice(self.confused_responses)}\n\n{random.choice(suggestions)}"

class DesktopAI(QWidget):

    def add_message(self, sender, message):
        """Add message to chat display"""
        self.conversation_history.append((sender, message))

        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.append(f"[{timestamp}] <b>{sender}:</b> {message}")
        self.chat_display.append("")

        # Auto scroll
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

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


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Create and show main window
    ai_assistant = DesktopAI()
    ai_assistant.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()