#!/usr/bin/env python3
"""
AI Desktop Suite Client - Lightweight
Connects to the centralized AI API server
"""

import sys
import os
import time
import threading
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QLineEdit, QLabel,
                             QSystemTrayIcon, QMenu, QAction, QMessageBox,
                             QProgressBar, QFrame, QScrollArea, QGridLayout,
                             QGroupBox, QComboBox, QSlider, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint, QRect, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen, QBrush

class VirtualKeyboard(QWidget):
    """Advanced Virtual Keyboard with Gesture Support"""
    key_pressed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(800, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.keys = [
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '⌫'],
            ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
            ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'", 'Enter'],
            ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Shift'],
            ['Ctrl', 'Alt', 'Space', 'Alt', 'Ctrl']
        ]

        self.caps_lock = False
        self.shift_pressed = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        for row in self.keys:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(3)

            for key in row:
                btn = QPushButton(key)
                btn.setFixedSize(45, 45)
                btn.clicked.connect(lambda checked, k=key: self.on_key_click(k))

                if key in ['⌫', 'Enter', 'Tab', 'Caps', 'Shift', 'Ctrl', 'Alt', 'Space']:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4a90e2;
                            color: white;
                            border: none;
                            border-radius: 5px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #357abd;
                        }
                        QPushButton:pressed {
                            background-color: #2c5aa0;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #f0f0f0;
                            color: #333;
                            border: 1px solid #ccc;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #e0e0e0;
                        }
                        QPushButton:pressed {
                            background-color: #d0d0d0;
                        }
                    """)

                row_layout.addWidget(btn)

            layout.addLayout(row_layout)

        self.setLayout(layout)

    def on_key_click(self, key):
        if key == 'Caps':
            self.caps_lock = not self.caps_lock
        elif key == 'Shift':
            self.shift_pressed = not self.shift_pressed
        elif key == '⌫':
            self.key_pressed.emit('BACKSPACE')
        elif key == 'Enter':
            self.key_pressed.emit('ENTER')
        elif key == 'Space':
            self.key_pressed.emit(' ')
        elif key == 'Tab':
            self.key_pressed.emit('TAB')
        else:
            if self.caps_lock or self.shift_pressed:
                key = key.upper()
            else:
                key = key.lower()

            self.key_pressed.emit(key)

            if self.shift_pressed:
                self.shift_pressed = False

class DrawingCanvas(QWidget):
    """Interactive Drawing Canvas for AI Screen"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(600, 400)
        self.drawing = False
        self.last_point = QPoint()
        self.lines = []
        self.current_line = []

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), QColor(20, 20, 20))

        pen = QPen(QColor(0, 255, 0), 3, Qt.SolidLine)
        painter.setPen(pen)

        for line in self.lines:
            if len(line) > 1:
                for i in range(len(line) - 1):
                    painter.drawLine(line[i], line[i + 1])

        if len(self.current_line) > 1:
            for i in range(len(self.current_line) - 1):
                painter.drawLine(self.current_line[i], self.current_line[i + 1])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()
            self.current_line = [event.pos()]

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.current_line.append(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            if len(self.current_line) > 1:
                self.lines.append(self.current_line)
            self.current_line = []

    def clear_canvas(self):
        self.lines = []
        self.current_line = []
        self.update()

class AIDesktopClient(QWidget):
    """Lightweight AI Desktop Client that connects to API server"""

    def __init__(self, api_url="http://localhost:3000"):
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] AIDesktopClient __init__ started")
        super().__init__()
        self.api_url = api_url
        self.session_id = f"desktop_{int(time.time())}"

        self.setWindowTitle("AI Desktop Suite - Client")
        self.setGeometry(50, 50, 1200, 800)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Threading and queue management
        self.task_queue = []
        self.response_queue = []

        # Voice and AI state
        self.voice_recognizer = None
        self.voice_engine = None
        self.virtual_keyboard_visible = False
        self.conversation_history = []
        self.current_mode = "chat"

        # Performance monitoring
        self.last_activity = time.time()
        self.task_count = 0

        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Basic setup completed")

        # Initialize components - delay heavy ones
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Starting delayed initialization")
        QTimer.singleShot(100, self.delayed_init)  # Delay heavy init by 100ms

        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] AIDesktopClient __init__ completed")

    def delayed_init(self):
        """Delayed initialization for heavy components"""
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Delayed init started")
        self.init_voice_system()
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Voice system initialized")
        self.setup_tray_icon()
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Tray icon setup")
        self.init_client_ui()
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Client UI initialized")

        # Start background processing
        self.start_background_worker()
        self.start_performance_monitor()
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Background threads started")

        # Auto-save timer
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_conversation_history)
        self.save_timer.start(30000)
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Save timer started")

        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Delayed init completed")

    def init_voice_system(self):
        """Initialize voice system"""
        try:
            import speech_recognition as sr
            import pyttsx3
            self.voice_recognizer = sr.Recognizer()
            self.voice_engine = pyttsx3.init()

            voices = self.voice_engine.getProperty('voices')
            if voices:
                english_voice = None
                for voice in voices:
                    if 'english' in voice.name.lower() or 'en' in voice.name.lower():
                        english_voice = voice
                        break

                if english_voice:
                    self.voice_engine.setProperty('voice', english_voice.id)

            self.voice_engine.setProperty('rate', 180)
            self.voice_engine.setProperty('volume', 0.8)

        except ImportError:
            print("[CLIENT] Voice system not available")

    def init_client_ui(self):
        """Initialize lightweight client UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Title bar with controls
        title_bar = self.create_title_bar()
        layout.addWidget(title_bar)

        # Mode selector
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Chat", "Draw", "Code", "Research", "Voice"])
        self.mode_combo.currentTextChanged.connect(self.change_mode)
        mode_layout.addWidget(self.mode_combo)

        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Main content area
        self.content_stack = QVBoxLayout()

        # Chat interface
        self.chat_widget = self.create_chat_interface()
        self.content_stack.addWidget(self.chat_widget)

        # Drawing canvas
        self.drawing_canvas = DrawingCanvas()
        self.drawing_canvas.hide()
        self.content_stack.addWidget(self.drawing_canvas)

        # Virtual keyboard
        self.virtual_keyboard = VirtualKeyboard()
        self.virtual_keyboard.hide()
        self.virtual_keyboard.key_pressed.connect(self.on_virtual_key_press)
        self.content_stack.addWidget(self.virtual_keyboard)

        layout.addLayout(self.content_stack)

        # Status bar
        self.status_label = QLabel("Ready - Connected to AI API Server")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-weight: bold;
                padding: 5px;
                background-color: rgba(0, 0, 0, 0.7);
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def create_title_bar(self):
        """Create title bar with controls"""
        title_bar = QFrame()
        title_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 120, 212, 0.9);
                border-radius: 10px 10px 0 0;
            }
        """)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("🤖 AI Desktop Client")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # Control buttons
        keyboard_btn = QPushButton("⌨️")
        keyboard_btn.clicked.connect(self.toggle_virtual_keyboard)
        keyboard_btn.setToolSheet(self.get_button_style("#28a745"))
        title_layout.addWidget(keyboard_btn)

        voice_btn = QPushButton("🎤")
        voice_btn.clicked.connect(self.start_voice_recognition)
        voice_btn.setStyleSheet(self.get_button_style("#007bff"))
        title_layout.addWidget(voice_btn)

        minimize_btn = QPushButton("−")
        minimize_btn.clicked.connect(self.showMinimized)
        minimize_btn.setStyleSheet(self.get_title_button_style())
        title_layout.addWidget(minimize_btn)

        close_btn = QPushButton("×")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(self.get_title_button_style())
        title_layout.addWidget(close_btn)

        title_bar.setLayout(title_layout)
        return title_bar

    def get_button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """

    def get_title_button_style(self):
        return """
            QPushButton {
                background: transparent;
                color: white;
                border: none;
                font-size: 16px;
                padding: 0 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
            }
        """

    def create_chat_interface(self):
        """Create chat interface"""
        chat_widget = QWidget()
        chat_layout = QVBoxLayout()

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(30, 30, 30, 0.9);
                color: #ffffff;
                border: 2px solid #0078d4;
                border-radius: 10px;
                padding: 10px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
            }
        """)
        chat_layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ask me anything...")
        self.message_input.returnPressed.connect(self.process_message_async)
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(40, 40, 40, 0.9);
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
        """)
        input_layout.addWidget(self.message_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.process_message_async)
        self.send_button.setStyleSheet(self.get_button_style("#0078d4"))
        input_layout.addWidget(self.send_button)

        chat_layout.addLayout(input_layout)
        chat_widget.setLayout(chat_layout)

        return chat_widget

    def toggle_virtual_keyboard(self):
        """Toggle virtual keyboard visibility"""
        if self.virtual_keyboard_visible:
            self.virtual_keyboard.hide()
            self.virtual_keyboard_visible = False
        else:
            self.virtual_keyboard.show()
            self.virtual_keyboard_visible = True

        self.adjustSize()

    def on_virtual_key_press(self, key):
        """Handle virtual keyboard input"""
        if key == 'BACKSPACE':
            current_text = self.message_input.text()
            self.message_input.setText(current_text[:-1])
        elif key == 'ENTER':
            self.process_message_async()
        elif key == 'TAB':
            pass
        else:
            current_text = self.message_input.text()
            self.message_input.setText(current_text + key)

    def change_mode(self, mode):
        """Change AI screen mode"""
        self.current_mode = mode.lower()

        # Hide all content
        self.chat_widget.hide()
        self.drawing_canvas.hide()
        self.virtual_keyboard.hide()

        # Show relevant content
        if self.current_mode == "chat":
            self.chat_widget.show()
        elif self.current_mode == "draw":
            self.drawing_canvas.show()
        elif self.current_mode == "voice":
            self.start_voice_recognition()

        self.status_label.setText(f"Mode: {mode}")

    def start_background_worker(self):
        """Start background worker thread"""
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Starting background worker thread")
        def worker():
            print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Background worker loop started")
            while True:
                try:
                    # Process tasks from queue
                    if self.task_queue:
                        task = self.task_queue.pop(0)
                        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Processing task: {task['type']}")
                        self.process_background_task(task)

                    time.sleep(0.1)

                except Exception as e:
                    print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Background worker error: {e}")
                    time.sleep(1)

        worker_thread = threading.Thread(target=worker, daemon=True, name="ClientWorker")
        worker_thread.start()
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Background worker thread started")

    def start_performance_monitor(self):
        """Monitor performance"""
        def monitor():
            while True:
                try:
                    current_time = time.time()

                    # Check for inactivity
                    if current_time - self.last_activity > 300:
                        print("[CLIENT] System inactive")

                    time.sleep(60)

                except Exception as e:
                    print(f"[CLIENT] Performance monitoring error: {e}")
                    time.sleep(60)

        monitor_thread = threading.Thread(target=monitor, daemon=True, name="PerformanceMonitor")
        monitor_thread.start()

    def process_message_async(self):
        """Process message asynchronously"""
        message = self.message_input.text().strip()
        if not message:
            return

        self.last_activity = time.time()
        self.task_count += 1

        # Update UI immediately
        self.add_message("You", message)
        self.message_input.clear()
        self.status_label.setText("Processing...")

        # Disable input during processing
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)

        # Submit to background processing
        self.task_queue.append({
            'type': 'message',
            'content': message,
            'timestamp': time.time()
        })

    def process_background_task(self, task):
        """Process task in background thread"""
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Starting task processing: {task['type']}")
        try:
            if task['type'] == 'message':
                print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Processing message: {task['content'][:30]}...")

                # Get response from API
                print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Calling get_ai_response")
                response = self.get_ai_response(task['content'])
                print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Received response: {response[:50]}...")

                # Update UI from main thread
                QTimer.singleShot(0, lambda: self.add_message("AI", response))
                QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))

                # Re-enable input elements
                QTimer.singleShot(0, lambda: self.message_input.setEnabled(True))
                QTimer.singleShot(0, lambda: self.send_button.setEnabled(True))

                # Speak response if voice is available
                if self.voice_engine and self.current_mode == "voice":
                    self.speak_response_safe(response)

        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Task processing error: {e}")
            error_msg = f"Error: {str(e)}"
            QTimer.singleShot(0, lambda: self.add_message("System", error_msg))
            QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))

            # Re-enable input elements on error
            QTimer.singleShot(0, lambda: self.message_input.setEnabled(True))
            QTimer.singleShot(0, lambda: self.send_button.setEnabled(True))
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Task processing completed")

    def get_ai_response(self, message):
        """Get response from AI API server"""
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] get_ai_response called with message: {message[:30]}...")
        try:
            payload = {
                'message': message,
                'session_id': self.session_id
            }

            print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Sending POST to {self.api_url}/chat")
            response = requests.post(f"{self.api_url}/chat", json=payload, timeout=10)
            print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Received response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                result = data.get('response', 'No response from server')
                print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Response data: {result[:50]}...")
                return result
            else:
                error_msg = f"Server error: {response.status_code}"
                print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] {error_msg}")
                return error_msg

        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {str(e)}. Is the API server running?"
            print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] {error_msg}")
            return error_msg

    def speak_response_safe(self, text):
        """Speak response safely"""
        if not self.voice_engine:
            return

        def speak():
            try:
                clean_text = text.replace('✅', 'success').replace('❌', 'error').replace('🤖', 'AI')
                clean_text = clean_text.replace('🎤', 'voice').replace('🗣️', 'speak').strip()

                if clean_text:
                    self.voice_engine.say(clean_text)
                    self.voice_engine.runAndWait()
            except Exception as e:
                print(f"[CLIENT] Speech error: {e}")

        speech_thread = threading.Thread(target=speak, daemon=True)
        speech_thread.start()

    def start_voice_recognition(self):
        """Start voice recognition"""
        if not self.voice_recognizer:
            self.add_message("System", "Voice recognition not available")
            return

        self.status_label.setText("🎤 Listening...")

        def recognize():
            try:
                import speech_recognition as sr

                with sr.Microphone() as source:
                    self.voice_recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.voice_recognizer.listen(source, timeout=5, phrase_time_limit=10)

                    # Try Google recognition
                    text = self.voice_recognizer.recognize_google(audio, language='en-US')

                    if text:
                        QTimer.singleShot(0, lambda: self.add_message("Voice", f"🎤 {text}"))
                        QTimer.singleShot(0, lambda: self.status_label.setText("🎤 Processing..."))

                        # Process the voice command
                        response = self.get_ai_response(text)
                        QTimer.singleShot(0, lambda: self.add_message("AI", response))
                        QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))

                        # Speak response
                        self.speak_response_safe(response)
                    else:
                        QTimer.singleShot(0, lambda: self.add_message("System", "Could not understand audio"))
                        QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))

            except Exception as e:
                QTimer.singleShot(0, lambda: self.add_message("System", f"Voice recognition error: {str(e)}"))
                QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))

        recognition_thread = threading.Thread(target=recognize, daemon=True)
        recognition_thread.start()

    def add_message(self, sender, message):
        """Add message to chat display"""
        timestamp = time.strftime("%H:%M:%S")
        self.chat_display.append(f"[{timestamp}] <b>{sender}:</b> {message}")
        self.chat_display.append("")

        # Auto scroll
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def setup_tray_icon(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor('#0078d4'))
            painter = QPainter(pixmap)
            painter.setPen(QColor('white'))
            painter.setFont(QFont('Arial', 20, QFont.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, 'AI')
            painter.end()

            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon(pixmap))
            self.tray_icon.setToolTip('AI Desktop Client')

            tray_menu = QMenu()
            show_action = QAction('Show Client', self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)

            quit_action = QAction('Quit', self)
            quit_action.triggered.connect(self.close)
            tray_menu.addAction(quit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()

    def save_conversation_history(self):
        """Save conversation history"""
        try:
            history_file = os.path.expanduser("~/.ai_desktop_client_history.json")
            with open(history_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(self.conversation_history[-100:], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[CLIENT] Failed to save history: {e}")

    def closeEvent(self, event):
        """Handle close event"""
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Close event triggered")
        self.save_conversation_history()
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Conversation history saved")
        # Quit the application to ensure it closes properly
        QApplication.instance().quit()
        event.accept()
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Application quit initiated")

def check_single_instance():
    """Check if another instance is already running"""
    import socket
    try:
        # Try to bind to a unique port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 65432))  # Unique port for this app
        sock.listen(1)
        return sock  # Return socket to keep it bound
    except socket.error:
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Another instance is already running")
        return None

def main():
    """Main application entry point"""
    print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Starting AI Desktop Client application")

    # Check for single instance
    instance_socket = check_single_instance()
    if instance_socket is None:
        print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Exiting: Another instance is running")
        QMessageBox.warning(None, "AI Desktop Client", "Another instance is already running.")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] QApplication created, QuitOnLastWindowClosed=False")

    # Set application properties
    app.setApplicationName("AI Desktop Client")
    app.setApplicationVersion("1.0")

    # Create and show main window
    print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Creating AIDesktopClient instance")
    client = AIDesktopClient()

    # Welcome message
    client.add_message("AI", "🤖 Welcome to AI Desktop Client!")
    client.add_message("AI", "🎯 Connected to lightweight AI API server")
    client.add_message("AI", "💡 Features: Chat | Draw | Voice | Web Search | Wikipedia | News")
    client.add_message("AI", "🌐 Try: 'search AI', 'wiki machine learning', 'news technology'")

    client.show()
    print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Client window shown")

    print(f"[{time.strftime('%H:%M:%S')}] [CLIENT] Entering app.exec_()")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()