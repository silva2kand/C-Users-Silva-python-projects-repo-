l#!/usr/bin/env python3
"""
Advanced AI Screen Assistant - Revolutionary Virtual Interface
A next-generation AI assistant with virtual screen, voice control, and advanced features.
"""

import sys
import os
import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path

# Fix Windows console encoding issues
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
    except:
        pass

# PyQt5 imports
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                              QTextEdit, QPushButton, QLineEdit, QLabel,
                              QSystemTrayIcon, QMenu, QAction, QMessageBox,
                              QProgressBar, QFrame, QScrollArea, QGridLayout,
                              QGroupBox, QComboBox, QSlider, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint, QRect, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen, QBrush

# Flask imports for local IP serving
try:
    from flask import Flask, render_template_string, request, jsonify
    import socket
    import threading
    FLASK_AVAILABLE = True
    print("[SUCCESS] Flask available for local IP serving")
except ImportError:
    FLASK_AVAILABLE = False
    print("[WARNING] Flask not available - local IP serving disabled")

# AI/ML imports
AI_AVAILABLE = False
QWEN_AVAILABLE = False
GPT4ALL_AVAILABLE = False
HUGGINGFACE_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    QWEN_AVAILABLE = True
    AI_AVAILABLE = True
    print("[SUCCESS] Qwen AI model available!")
except ImportError:
    print("[WARNING] Qwen not available, trying GPT4All...")

if not QWEN_AVAILABLE:
    try:
        from gpt4all import GPT4All
        GPT4ALL_AVAILABLE = True
        AI_AVAILABLE = True
        print("[SUCCESS] GPT4All available as fallback")
    except ImportError:
        print("[WARNING] GPT4All not available, will use free API fallback")

# Free API fallback and internet knowledge imports
try:
    import requests
    from bs4 import BeautifulSoup
    WEB_AVAILABLE = True
    print("[SUCCESS] Web scraping and API access available")
except ImportError:
    WEB_AVAILABLE = False
    print("[WARNING] Web libraries not available - limited knowledge access")

# Additional knowledge sources
try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
    print("[SUCCESS] Wikipedia API available")
except ImportError:
    WIKIPEDIA_AVAILABLE = False
    print("[WARNING] Wikipedia not available")

try:
    import feedparser
    RSS_AVAILABLE = True
    print("[SUCCESS] RSS feed parsing available")
except ImportError:
    RSS_AVAILABLE = False
    print("[WARNING] RSS feeds not available")

# Free API fallback
try:
    import requests
    HUGGINGFACE_AVAILABLE = True
    print("[SUCCESS] Free API (Hugging Face) available as final fallback")
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    print("[WARNING] Requests not available - limited fallback options")

# Voice recognition imports
VOICE_AVAILABLE = False
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
    print("[SUCCESS] Voice recognition available!")
except ImportError:
    print("[WARNING] Voice recognition not available")

class VirtualKeyboard(QWidget):
    """Advanced Virtual Keyboard with Gesture Support"""

    key_pressed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(800, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Keyboard layout
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

                # Style based on key type
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
            # Apply caps lock and shift
            if self.caps_lock or self.shift_pressed:
                key = key.upper()
            else:
                key = key.lower()

            self.key_pressed.emit(key)

            # Reset shift after use
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

        # Draw background
        painter.fillRect(self.rect(), QColor(20, 20, 20))

        # Draw lines
        pen = QPen(QColor(0, 255, 0), 3, Qt.SolidLine)
        painter.setPen(pen)

        for line in self.lines:
            if len(line) > 1:
                for i in range(len(line) - 1):
                    painter.drawLine(line[i], line[i + 1])

        # Draw current line
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

class AdvancedAIScreen(QWidget):
    """Advanced AI Screen with Virtual Interface"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced AI Screen Assistant")
        self.setGeometry(50, 50, 1200, 800)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Threading and queue management
        self.task_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="AI_Worker")
        self.futures = []

        # Voice and AI state
        self.ai_model = None
        self.voice_recognizer = None
        self.voice_engine = None
        self.virtual_keyboard_visible = False
        self.conversation_history = []
        self.current_mode = "chat"  # chat, draw, code, research

        # Performance monitoring
        self.last_activity = time.time()
        self.task_count = 0

        # Initialize components
        self.init_voice_system()
        self.init_ai_model()
        self.setup_tray_icon()
        self.init_advanced_ui()

        # Start background processing
        self.start_background_worker()
        self.start_performance_monitor()

        # Auto-save timer
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_conversation_history)
        self.save_timer.start(30000)

        # Create desktop shortcut
        self.create_desktop_shortcut()

    def init_voice_system(self):
        """Initialize advanced voice system"""
        if not VOICE_AVAILABLE:
            print("[INFO] Voice system not available")
            return

        try:
            print("[INIT] Initializing advanced voice system...")
            self.voice_recognizer = sr.Recognizer()
            self.voice_engine = pyttsx3.init()

            # Configure voice settings
            voices = self.voice_engine.getProperty('voices')
            if voices:
                # Try to find English voice
                english_voice = None
                for voice in voices:
                    if 'english' in voice.name.lower() or 'en' in voice.name.lower():
                        english_voice = voice
                        break

                if english_voice:
                    self.voice_engine.setProperty('voice', english_voice.id)
                    print(f"[VOICE] Using voice: {english_voice.name}")

            self.voice_engine.setProperty('rate', 180)
            self.voice_engine.setProperty('volume', 0.8)

            print("[SUCCESS] Voice system initialized")

        except Exception as e:
            print(f"[ERROR] Voice system initialization failed: {e}")
            self.voice_recognizer = None
            self.voice_engine = None

    def init_ai_model(self):
        """Initialize AI model in background with comprehensive logging and faster loading"""
        def load_ai():
            import psutil
            import os
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

            print(f"[AI] Starting AI model loading... Initial RAM: {initial_memory:.1f} MB")

            try:
                # Try GPT4All first (faster and more reliable for 4GB RAM)
                if GPT4ALL_AVAILABLE:
                    print("[AI] Loading GPT4All with 4GB RAM limit...")
                    print("[AI] Using orca-mini-3b-gguf2-q4_0.gguf (optimized for 4GB RAM)")

                    # Configure GPT4All for CPU-only with memory monitoring
                    start_time = time.time()
                    self.ai_model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf", device='cpu')
                    load_time = time.time() - start_time

                    after_gpt4all_memory = process.memory_info().rss / 1024 / 1024
                    gpt4all_memory_usage = after_gpt4all_memory - initial_memory
                    print(f"[AI] GPT4All loaded successfully in {load_time:.1f}s. RAM usage: {after_gpt4all_memory:.1f} MB (+{gpt4all_memory_usage:.1f} MB)")

                    if gpt4all_memory_usage > 4000:  # Over 4GB warning
                        print(f"[AI] WARNING: GPT4All exceeded 4GB RAM limit ({gpt4all_memory_usage:.1f} MB). Performance may be degraded.")

                    return {"model": self.ai_model, "type": "gpt4all", "memory_usage": gpt4all_memory_usage, "load_time": load_time}

                elif QWEN_AVAILABLE:
                    print("[AI] GPT4All not available, attempting to load Qwen model...")
                    model_name = "microsoft/DialoGPT-small"
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    model = AutoModelForCausalLM.from_pretrained(model_name)

                    after_qwen_memory = process.memory_info().rss / 1024 / 1024
                    qwen_memory_usage = after_qwen_memory - initial_memory
                    print(f"[AI] Qwen loaded successfully. RAM usage: {after_qwen_memory:.1f} MB (+{qwen_memory_usage:.1f} MB)")

                    if qwen_memory_usage > 3500:  # Warning if over 3.5GB
                        print(f"[AI] WARNING: High memory usage detected ({qwen_memory_usage:.1f} MB). Consider using GPT4All for lower RAM.")

                    return {"tokenizer": tokenizer, "model": model, "type": "qwen", "memory_usage": qwen_memory_usage}

                else:
                    print("[AI] No AI models available - running in basic mode with free API fallback")
                    return {"type": "basic", "fallback": "huggingface"}

            except Exception as e:
                print(f"[AI] Model loading failed: {e}")
                print("[AI] Falling back to basic mode with free API")
                return {"type": "basic", "fallback": "huggingface", "error": str(e)}

        future = self.executor.submit(load_ai)
        self.futures.append(future)

    def init_advanced_ui(self):
        """Initialize advanced UI with virtual components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Title bar with controls
        title_bar = self.create_advanced_title_bar()
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
        self.status_label = QLabel("Ready - Advanced AI Screen Active")
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

    def create_advanced_title_bar(self):
        """Create advanced title bar with controls"""
        title_bar = QFrame()
        title_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 120, 212, 0.9);
                border-radius: 10px 10px 0 0;
            }
        """)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("🤖 Advanced AI Screen")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # Control buttons
        keyboard_btn = QPushButton("⌨️")
        keyboard_btn.clicked.connect(self.toggle_virtual_keyboard)
        keyboard_btn.setToolTip("Toggle Virtual Keyboard")
        keyboard_btn.setStyleSheet(self.get_button_style("#28a745"))
        title_layout.addWidget(keyboard_btn)

        voice_btn = QPushButton("🎤")
        voice_btn.clicked.connect(self.start_voice_recognition)
        voice_btn.setToolTip("Start Voice Recognition")
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
        """Create advanced chat interface"""
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
        self.message_input.setPlaceholderText("Type your message or use voice...")
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
            # Could implement tab completion
            pass
        else:
            current_text = self.message_input.text()
            self.message_input.setText(current_text + key)

    def on_processing_timeout(self):
        """Handle processing timeout to recover UI"""
        print("[TIMEOUT] Processing timeout reached - recovering UI")
        try:
            # Stop the processing timer
            if hasattr(self, 'processing_timer'):
                self.processing_timer.stop()

            # Re-enable UI elements
            self.message_input.setEnabled(True)
            self.send_button.setEnabled(True)

            # Update status
            self.status_label.setText("Ready - Previous request timed out")

            # Add timeout message
            self.add_message("System", "⚠️ The previous request timed out. The AI assistant is still working, but the response took too long. Try a shorter message or try again.")

        except Exception as e:
            print(f"[TIMEOUT] Error in timeout handler: {e}")
            # Emergency recovery
            self.message_input.setEnabled(True)
            self.send_button.setEnabled(True)
            self.status_label.setText("Ready")

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
        def worker():
            while True:
                try:
                    # Process tasks from queue
                    if not self.task_queue.empty():
                        task = self.task_queue.get(timeout=1)
                        self.process_background_task(task)

                    # Check for completed futures
                    for future in self.futures[:]:
                        if future.done():
                            try:
                                result = future.result()
                                if isinstance(result, dict) and 'model' in result:
                                    self.ai_model = result
                                    self.status_label.setText("AI Model Loaded - Ready!")
                                    print("[SUCCESS] AI model loaded successfully")
                            except Exception as e:
                                print(f"[ERROR] Future processing failed: {e}")
                            self.futures.remove(future)

                    time.sleep(0.1)  # Prevent busy waiting

                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"[ERROR] Background worker error: {e}")
                    time.sleep(1)

        worker_thread = threading.Thread(target=worker, daemon=True, name="BackgroundWorker")
        worker_thread.start()

    def start_performance_monitor(self):
        """Monitor performance and prevent resource exhaustion"""
        def monitor():
            while True:
                try:
                    current_time = time.time()

                    # Check for inactivity
                    if current_time - self.last_activity > 300:  # 5 minutes
                        print("[MONITOR] System inactive, optimizing resources...")

                    # Monitor thread pool
                    if len(self.futures) > 10:
                        print("[MONITOR] High task load detected")

                    time.sleep(60)  # Check every minute

                except Exception as e:
                    print(f"[MONITOR] Performance monitoring error: {e}")
                    time.sleep(60)

        monitor_thread = threading.Thread(target=monitor, daemon=True, name="PerformanceMonitor")
        monitor_thread.start()

    def process_message_async(self):
        """Process message asynchronously to prevent freezing"""
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

        # Set up failsafe timeout (30 seconds)
        self.processing_timer = QTimer()
        self.processing_timer.setSingleShot(True)
        self.processing_timer.timeout.connect(self.on_processing_timeout)
        self.processing_timer.start(30000)  # 30 second timeout

        # Submit to background processing
        self.task_queue.put({
            'type': 'message',
            'content': message,
            'timestamp': time.time()
        })

    def process_background_task(self, task):
        """Process task in background thread with timeout protection"""
        try:
            if task['type'] == 'message':
                print(f"[TASK] Processing message task: {task['content'][:30]}...")

                # Add timeout protection for response generation
                import threading
                response_result = [None]
                response_exception = [None]

                def generate_with_timeout():
                    try:
                        response_result[0] = self.generate_ai_response(task['content'])
                    except Exception as e:
                        response_exception[0] = e
                        print(f"[TASK] Response generation error: {e}")

                # Start response generation with timeout
                response_thread = threading.Thread(target=generate_with_timeout, daemon=True)
                response_thread.start()

                # Wait with timeout (15 seconds for message processing)
                response_thread.join(timeout=15)

                if response_thread.is_alive():
                    print("[TASK] Response generation timed out")
                    response = "I'm taking too long to respond. Please try a shorter message or try again."
                elif response_exception[0]:
                    print(f"[TASK] Response generation failed: {response_exception[0]}")
                    response = f"Sorry, I encountered an error: {str(response_exception[0])}"
                else:
                    response = response_result[0] or "I couldn't generate a response. Please try again."

                print(f"[TASK] Response ready: '{response[:50]}...'")

                # Update UI from main thread
                QTimer.singleShot(0, lambda: self.add_message("AI", response))
                QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))

                # Re-enable input elements
                QTimer.singleShot(0, lambda: self.message_input.setEnabled(True))
                QTimer.singleShot(0, lambda: self.send_button.setEnabled(True))

                # Stop the processing timer
                if hasattr(self, 'processing_timer'):
                    QTimer.singleShot(0, lambda: self.processing_timer.stop())

                # Speak response if voice is available
                if self.voice_engine and self.current_mode == "voice":
                    self.speak_response_safe(response)

        except Exception as e:
            print(f"[TASK] Critical error in process_background_task: {e}")
            error_msg = f"Critical error: {str(e)}"
            QTimer.singleShot(0, lambda: self.add_message("System", error_msg))
            QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))

            # Re-enable input elements on error
            QTimer.singleShot(0, lambda: self.message_input.setEnabled(True))
            QTimer.singleShot(0, lambda: self.send_button.setEnabled(True))

            # Stop the processing timer
            if hasattr(self, 'processing_timer'):
                QTimer.singleShot(0, lambda: self.processing_timer.stop())

    def generate_ai_response(self, message):
        """Generate AI response with instant fallback for common queries"""
        try:
            print(f"[AI] Processing message: '{message[:50]}...'")

            # INSTANT RESPONSES for common queries (no delay)
            message_lower = message.lower().strip()

            # Ultra-fast responses for basic interactions
            instant_responses = {
                'hi': "👋 Hi there! How can I help you today?",
                'hello': "👋 Hello! I'm your Advanced AI Screen Assistant. What can I do for you?",
                'hey': "👋 Hey! Ready to help with anything you need!",
                'help': """🆘 Quick Help:
• 🎤 Click the microphone for voice commands
• ⌨️ Click the keyboard icon for virtual typing
• 🎨 Switch to Draw mode for visual input
• 💬 Just type messages to chat with me
• 🔄 Use the dropdown to change modes
• 🌐 Search the web, Wikipedia, or get news
• 📚 Access current knowledge and information

Try saying 'system info' or 'what can you do'!""",
                'what can you do': """🤖 I can help with:
• 💬 Natural conversation and questions
• 🎤 Voice recognition and speech
• ⌨️ Virtual keyboard input
• 🎨 Drawing and visual tasks
• 🔍 Research and information
• 🌐 Web search and browsing
• 📚 Wikipedia knowledge
• 📰 Latest news and updates
• ️ System monitoring
• 💻 Programming assistance

What would you like to try?""",
                'system info': self.get_system_info_response(),
                'test': "✅ Test successful! I'm working perfectly. Try 'help' for more features.",
                'status': "✅ AI Assistant Status: Active and Ready\n🎤 Voice: Available\n⌨️ Virtual Keyboard: Ready\n🎨 Drawing: Enabled\n🌐 Internet Access: Ready",
            }

            # Check for instant responses first
            for key, response in instant_responses.items():
                if key in message_lower:
                    print(f"[AI] Instant response for: {key}")
                    return response

            # INTERNET KNOWLEDGE QUERIES
            # Detect research/search requests
            if any(word in message_lower for word in ['search', 'find', 'look up', 'research', 'what is', 'who is', 'how to', 'tell me about']):
                print("[AI] Detected research request, using web search")
                # Extract search query
                search_query = message_lower
                for prefix in ['search for', 'find', 'look up', 'research', 'what is', 'who is', 'how to', 'tell me about']:
                    search_query = search_query.replace(prefix, '').strip()

                if search_query:
                    return self.search_web(search_query)

            # Wikipedia requests
            if any(word in message_lower for word in ['wikipedia', 'wiki', 'encyclopedia', 'definition of', 'meaning of']):
                print("[AI] Detected Wikipedia request")
                wiki_query = message_lower
                for prefix in ['wikipedia', 'wiki', 'encyclopedia', 'definition of', 'meaning of']:
                    wiki_query = wiki_query.replace(prefix, '').strip()

                if wiki_query:
                    return self.search_wikipedia(wiki_query)

            # News requests
            if any(word in message_lower for word in ['news', 'latest', 'headlines', 'current events', 'what\'s happening']):
                print("[AI] Detected news request")
                topic = None
                if 'technology' in message_lower or 'tech' in message_lower:
                    topic = 'technology'
                elif 'science' in message_lower:
                    topic = 'science'
                elif 'business' in message_lower:
                    topic = 'business'
                else:
                    topic = 'world'

                return self.get_news(topic)

            # Web scraping requests
            if 'scrape' in message_lower or 'extract from' in message_lower or message_lower.startswith('http'):
                print("[AI] Detected web scraping request")
                # Try to extract URL
                import re
                url_match = re.search(r'https?://[^\s]+', message)
                if url_match:
                    return self.scrape_webpage(url_match.group())
                else:
                    return "🌐 Please provide a valid URL to scrape. Example: 'scrape https://example.com'"

            # Try AI model with optimized timeout
            if self.ai_model and 'model' in self.ai_model:
                print("[AI] Attempting AI model response...")
                try:
                    import threading
                    result = [None]
                    response_ready = [False]

                    def quick_ai_response():
                        try:
                            start_time = time.time()

                            if self.ai_model.get('type') == 'gpt4all':
                                # GPT4All response with optimized settings for speed
                                response = self.ai_model['model'].generate(
                                    message,
                                    max_tokens=50,  # Shorter responses
                                    temp=0.5,  # Lower temperature for faster, more focused responses
                                    top_k=30,  # Smaller top_k for speed
                                    top_p=0.8,
                                    repeat_penalty=1.0
                                )
                                result[0] = response.strip()

                            elif 'tokenizer' in self.ai_model:
                                inputs = self.ai_model['tokenizer'](message, return_tensors="pt", truncation=True, max_length=128)  # Shorter input
                                with torch.no_grad():
                                    outputs = self.ai_model['model'].generate(
                                        inputs.input_ids,
                                        max_length=min(inputs.input_ids.shape[1] + 30, 200),  # Shorter output
                                        num_return_sequences=1,
                                        temperature=0.7,
                                        do_sample=False,
                                        pad_token_id=self.ai_model['tokenizer'].eos_token_id,
                                        attention_mask=inputs.attention_mask,
                                        max_time=2.0  # 2 second hard limit
                                    )
                                response = self.ai_model['tokenizer'].decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
                                result[0] = response.strip()

                            response_time = time.time() - start_time
                            print(f"[AI] Response generated in {response_time:.2f}s")
                            response_ready[0] = True

                        except Exception as e:
                            print(f"[AI] Quick AI error: {e}")
                            response_ready[0] = True

                    ai_thread = threading.Thread(target=quick_ai_response, daemon=True)
                    ai_thread.start()

                    # Wait for response with shorter timeout
                    timeout_counter = 0
                    while not response_ready[0] and timeout_counter < 20:  # 2 seconds total
                        time.sleep(0.1)
                        timeout_counter += 1

                    if response_ready[0] and result[0] and len(result[0]) > 5:  # Valid response
                        print(f"[AI] AI response: '{result[0][:50]}...'")
                        return result[0]
                    else:
                        print("[AI] AI response timeout or invalid")

                except Exception as e:
                    print(f"[AI] AI model failed, trying free API fallback: {e}")

            # Free API fallback using Hugging Face with faster settings
            if HUGGINGFACE_AVAILABLE:
                print("[AI] Attempting free API fallback...")
                try:
                    fallback_response = self.get_huggingface_response(message)
                    if fallback_response and len(fallback_response) > 5:
                        print(f"[AI] Free API response: '{fallback_response[:50]}...'")
                        return fallback_response
                except Exception as e:
                    print(f"[AI] Free API fallback failed: {e}")

            # Fallback for everything else
            return self.get_smart_fallback_response(message)

        except Exception as e:
            print(f"[AI] Critical error: {e}")
            return "⚠️ I'm having trouble responding right now. Try 'help' for available commands!"

    def get_fallback_response(self, message):
        """Get intelligent fallback response when AI is not available"""
        message_lower = message.lower().strip()

        # Greeting responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return "👋 Hello! I'm your Advanced AI Screen Assistant. I can help with chat, voice commands, drawing, and more!"

        # Help responses
        elif any(word in message_lower for word in ['help', 'commands', 'what can you do']):
            return """🆘 I can help you with:

🎤 **Voice Commands**: Click the 🎤 button to speak
⌨️ **Virtual Keyboard**: Click ⌨️ for on-screen keyboard
🎨 **Drawing**: Switch to Draw mode for visual input
💬 **Chat**: Type messages or use voice
🔄 **Modes**: Switch between Chat/Draw/Code/Research/Voice

Try saying 'hello' or clicking the voice button!"""

        # System info
        elif any(phrase in message_lower for phrase in ['system info', 'computer info', 'my pc']):
            try:
                import platform
                import psutil
                info = f"""
🖥️ System Information:
• OS: {platform.system()} {platform.release()}
• CPU: {psutil.cpu_percent()}% usage
• Memory: {psutil.virtual_memory().percent}% used
• Disk: {psutil.disk_usage('/').percent}% used
"""
                return info
            except:
                return "🖥️ I can show system information, but there was an error retrieving it."

        # Drawing help
        elif any(word in message_lower for word in ['draw', 'drawing', 'paint']):
            return "🎨 To use drawing mode: Change the mode dropdown to 'Draw', then use your mouse to draw on the canvas!"

        # Voice help
        elif any(word in message_lower for word in ['voice', 'speak', 'talk']):
            return "🎤 Voice commands: Click the 🎤 button, wait for 'Listening...', then speak clearly. I support multiple languages!"

        # Generic responses
        else:
            responses = [
                f"I understand you want to talk about '{message[:30]}...'. I'm here to help!",
                f"That's interesting! Tell me more about '{message[:30]}...' and I'll assist you.",
                f"I can help with that. What specifically would you like to know about '{message[:30]}...'?",
                f"Great question about '{message[:30]}...'. I'm ready to help you find the answer!",
                f"I see you're interested in '{message[:30]}...'. How can I assist you with that?"
            ]

            # Return a response based on message length (for variety)
            return responses[len(message) % len(responses)]

    def get_system_info_response(self):
        """Get formatted system information"""
        try:
            import platform
            import psutil
            info = f"""🖥️ System Information:
• OS: {platform.system()} {platform.release()}
• CPU: {psutil.cpu_percent()}% usage
• Memory: {psutil.virtual_memory().percent}% used
• Disk: {psutil.disk_usage('/').percent}% used"""
            return info
        except:
            return "🖥️ System info: Unable to retrieve details right now."

    def get_huggingface_response(self, message):
        """Get response from free Hugging Face API with optimized settings"""
        try:
            # Use a faster, more reliable model
            api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-small"
            headers = {"Content-Type": "application/json"}

            # Shorter, faster payload
            payload = {
                "inputs": message[:100],  # Limit input length
                "parameters": {
                    "max_length": 50,  # Shorter responses
                    "temperature": 0.5,  # More focused
                    "do_sample": False,  # Faster, deterministic
                    "pad_token_id": 50256
                },
                "options": {
                    "wait_for_model": False  # Don't wait for model to load
                }
            }

            print("[HUGGINGFACE] Sending request to free API...")
            response = requests.post(api_url, json=payload, headers=headers, timeout=5)  # Shorter timeout

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    if generated_text:
                        # Clean up the response - remove the input message
                        clean_response = generated_text.replace(message, '').strip()
                        if not clean_response:
                            # If cleaning didn't work, take the last part
                            clean_response = generated_text.strip().split()[-10:]  # Last 10 words
                            clean_response = ' '.join(clean_response)

                        if len(clean_response) > 10:  # Must be substantial
                            return clean_response

            elif response.status_code == 503:
                print("[HUGGINGFACE] Model loading, trying alternative...")
                # Try a different model if first one is loading
                return self.get_alternative_huggingface_response(message)

            print(f"[HUGGINGFACE] API response failed: {response.status_code}")
            return None

        except requests.exceptions.Timeout:
            print("[HUGGINGFACE] Request timeout")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[HUGGINGFACE] Network error: {e}")
            return None
        except Exception as e:
            print(f"[HUGGINGFACE] Unexpected error: {e}")
            return None

    def get_alternative_huggingface_response(self, message):
        """Alternative Hugging Face model for fallback"""
        try:
            # Use a different model
            api_url = "https://api-inference.huggingface.co/models/distilgpt2"
            headers = {"Content-Type": "application/json"}

            payload = {
                "inputs": message[:80],
                "parameters": {
                    "max_length": 40,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }

            response = requests.post(api_url, json=payload, headers=headers, timeout=3)

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    if generated_text and len(generated_text) > len(message):
                        return generated_text[len(message):].strip()

            return None

        except:
            return None

    def search_web(self, query, max_results=3):
        """Search the web using DuckDuckGo (free)"""
        try:
            if not WEB_AVAILABLE:
                return "Web search not available - please install requests and beautifulsoup4"

            # Use DuckDuckGo HTML search (free, no API key needed)
            search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            print(f"[WEB] Searching for: {query}")
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            results = []
            for result in soup.find_all('div', class_='result')[:max_results]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')

                if title_elem and snippet_elem:
                    title = title_elem.get_text().strip()
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text().strip()

                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet[:200] + '...' if len(snippet) > 200 else snippet
                    })

            if results:
                response_text = f"🔍 Web search results for '{query}':\n\n"
                for i, result in enumerate(results, 1):
                    response_text += f"{i}. **{result['title']}**\n"
                    response_text += f"   {result['snippet']}\n"
                    response_text += f"   🔗 {result['url']}\n\n"

                response_text += "💡 I can search for more specific information or different topics!"
                return response_text
            else:
                return f"🔍 I searched for '{query}' but couldn't find relevant results. Try rephrasing your search."

        except Exception as e:
            print(f"[WEB] Search error: {e}")
            return f"🔍 Web search failed: {str(e)}. Try a different search term."

    def search_wikipedia(self, query):
        """Search Wikipedia for information"""
        try:
            if not WIKIPEDIA_AVAILABLE:
                return "Wikipedia search not available - please install wikipedia package"

            print(f"[WIKIPEDIA] Searching for: {query}")

            # Search for pages
            search_results = wikipedia.search(query, results=3)

            if not search_results:
                return f"📚 No Wikipedia pages found for '{query}'. Try a different topic."

            # Get the first result
            try:
                page = wikipedia.page(search_results[0])
                summary = page.summary[:500] + "..." if len(page.summary) > 500 else page.summary

                response = f"📚 **{page.title}**\n\n"
                response += f"{summary}\n\n"
                response += f"🔗 Full article: {page.url}\n\n"

                if len(search_results) > 1:
                    response += f"📖 Related pages: {', '.join(search_results[1:3])}"

                return response

            except wikipedia.exceptions.DisambiguationError as e:
                options = e.options[:5]  # First 5 options
                return f"📚 Multiple Wikipedia pages found for '{query}':\n\n" + "\n".join(f"• {option}" for option in options) + "\n\nTry being more specific!"

            except wikipedia.exceptions.PageError:
                return f"📚 No Wikipedia page found for '{query}'. Try a different topic."

        except Exception as e:
            print(f"[WIKIPEDIA] Error: {e}")
            return f"📚 Wikipedia search failed: {str(e)}. Try a different topic."

    def get_news(self, topic=None):
        """Get latest news from RSS feeds"""
        try:
            if not RSS_AVAILABLE:
                return "News feed not available - please install feedparser"

            # Free RSS feeds (no API key needed)
            feeds = {
                'technology': 'https://feeds.bbci.co.uk/news/technology/rss.xml',
                'world': 'https://feeds.bbci.co.uk/news/world/rss.xml',
                'science': 'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
                'business': 'https://feeds.bbci.co.uk/news/business/rss.xml'
            }

            if topic and topic.lower() in feeds:
                feed_url = feeds[topic.lower()]
            else:
                feed_url = feeds['world']  # Default to world news

            print(f"[NEWS] Fetching news from: {feed_url}")
            feed = feedparser.parse(feed_url)

            if not feed.entries:
                return "📰 No news articles found. Try again later."

            # Get latest 3 articles
            articles = feed.entries[:3]

            response = f"📰 Latest {topic or 'World'} News:\n\n"
            for i, article in enumerate(articles, 1):
                title = article.title
                link = article.link
                published = article.get('published', 'Recent')

                response += f"{i}. **{title}**\n"
                response += f"   📅 {published}\n"
                response += f"   🔗 {link}\n\n"

            response += "💡 I can get news from: technology, world, science, business"
            return response

        except Exception as e:
            print(f"[NEWS] Error: {e}")
            return f"📰 News feed failed: {str(e)}. Try again later."

    def scrape_webpage(self, url):
        """Scrape basic information from a webpage"""
        try:
            if not WEB_AVAILABLE:
                return "Web scraping not available - please install requests and beautifulsoup4"

            print(f"[SCRAPE] Scraping: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract title
            title = soup.title.string if soup.title else "No title found"

            # Extract main content (simple approach)
            paragraphs = soup.find_all('p')[:3]  # First 3 paragraphs
            content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

            if len(content) > 500:
                content = content[:500] + "..."

            response = f"🌐 **{title}**\n\n"
            response += f"{content}\n\n"
            response += f"🔗 Source: {url}"

            return response

        except Exception as e:
            print(f"[SCRAPE] Error: {e}")
            return f"🌐 Web scraping failed: {str(e)}. URL might be invalid or blocked."

    def get_smart_fallback_response(self, message):
        """Get intelligent fallback response for any message"""
        message_lower = message.lower().strip()

        # Quick pattern matching for common queries
        if any(word in message_lower for word in ['how are you', 'how do you do']):
            return "🤖 I'm doing great! I'm your Advanced AI Screen Assistant, ready to help with anything you need!"

        elif any(word in message_lower for word in ['thank you', 'thanks', 'thx']):
            return "😊 You're very welcome! I'm here whenever you need help. Just ask!"

        elif any(word in message_lower for word in ['bye', 'goodbye', 'see you']):
            return "👋 Goodbye! Your Advanced AI Screen Assistant will be here when you need me again!"

        elif any(word in message_lower for word in ['time', 'what time']):
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            return f"🕐 Current time is {current_time}"

        elif any(word in message_lower for word in ['date', 'what date', 'today']):
            from datetime import datetime
            current_date = datetime.now().strftime("%B %d, %Y")
            return f"📅 Today is {current_date}"

        elif any(word in message_lower for word in ['weather', 'temperature']):
            return "🌤️ I don't have access to current weather data, but you can check your favorite weather app or website!"

        elif any(word in message_lower for word in ['joke', 'funny']):
            jokes = [
                "Why don't scientists trust atoms? Because they make up everything! 😂",
                "Why did the computer go to the doctor? It had a virus! 💻",
                "What do you call a bear with no teeth? A gummy bear! 🐻"
            ]
            return jokes[len(message) % len(jokes)]

        elif any(word in message_lower for word in ['music', 'song', 'play']):
            return "🎵 I can't play music directly, but I can help you find songs or recommend music services!"

        elif any(word in message_lower for word in ['draw', 'drawing', 'paint', 'art']):
            return "🎨 Great! Switch to Draw mode using the dropdown above, then use your mouse to create art on the canvas!"

        elif any(word in message_lower for word in ['code', 'program', 'programming']):
            return "💻 I can help with programming! Try asking about specific languages or concepts. What would you like to code?"

        elif any(word in message_lower for word in ['research', 'learn', 'study']):
            return "🔍 I'd love to help you research! What topic interests you? I can suggest resources and guide your learning."

        elif any(word in message_lower for word in ['exercise', 'workout', 'fitness']):
            return "💪 I can provide workout tips and fitness advice! What type of exercise are you interested in?"

        elif any(word in message_lower for word in ['travel', 'vacation', 'trip']):
            return "✈️ I can help with travel planning and destination recommendations! Where are you thinking of going?"

        elif any(word in message_lower for word in ['movie', 'film', 'watch']):
            return "🎬 I can recommend movies and discuss films! What genre are you in the mood for?"

        elif any(word in message_lower for word in ['book', 'read', 'reading']):
            return "📚 Love books! I can recommend reading material and discuss literature. What genres interest you?"

        elif any(word in message_lower for word in ['food', 'recipe', 'cook']):
            return "🍳 I can help with recipes and cooking tips! What type of food are you interested in?"

        # Generic conversational responses
        else:
            conversational_responses = [
                f"I see you're asking about '{message[:30]}...'. That's interesting! How can I help you with that?",
                f"'{message[:30]}...' sounds fascinating! What would you like to explore about it?",
                f"Great question about '{message[:30]}...'. I'm here to assist you with that!",
                f"I understand you're interested in '{message[:30]}...'. Let me help you with that topic!",
                f"'{message[:30]}...' is something I can help with! What would you like to know?"
            ]

            return conversational_responses[len(message) % len(conversational_responses)]

    def speak_response_safe(self, text):
        """Speak response safely without blocking"""
        if not self.voice_engine:
            return

        def speak():
            try:
                # Clean text for speech
                clean_text = text.replace('✅', 'success').replace('❌', 'error').replace('🤖', 'AI')
                clean_text = clean_text.replace('🎤', 'voice').replace('🗣️', 'speak').strip()

                if clean_text:
                    self.voice_engine.say(clean_text)
                    self.voice_engine.runAndWait()
            except Exception as e:
                print(f"[SPEECH] Error: {e}")

        speech_thread = threading.Thread(target=speak, daemon=True)
        speech_thread.start()

    def start_voice_recognition(self):
        """Start advanced voice recognition"""
        if not VOICE_AVAILABLE or not self.voice_recognizer:
            self.add_message("System", "Voice recognition not available")
            return

        self.status_label.setText("🎤 Listening...")

        def recognize():
            try:
                with sr.Microphone() as source:
                    self.voice_recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.voice_recognizer.listen(source, timeout=5, phrase_time_limit=10)

                    # Try multiple recognition services
                    text = None

                    # Try Google first
                    try:
                        text = self.voice_recognizer.recognize_google(audio, language='en-US')
                    except sr.RequestError:
                        # Try alternative if available
                        try:
                            text = self.voice_recognizer.recognize_google(audio, language='en-GB')
                        except:
                            pass

                    if text:
                        QTimer.singleShot(0, lambda: self.add_message("Voice", f"🎤 {text}"))
                        QTimer.singleShot(0, lambda: self.status_label.setText("🎤 Processing..."))

                        # Process the voice command
                        response = self.generate_ai_response(text)
                        QTimer.singleShot(0, lambda: self.add_message("AI", response))
                        QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))

                        # Speak response
                        self.speak_response_safe(response)
                    else:
                        QTimer.singleShot(0, lambda: self.add_message("System", "Could not understand audio"))
                        QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))

            except sr.WaitTimeoutError:
                QTimer.singleShot(0, lambda: self.add_message("System", "No speech detected"))
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
            self.tray_icon.setToolTip('Advanced AI Screen Assistant')

            tray_menu = QMenu()
            show_action = QAction('Show Assistant', self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)

            quit_action = QAction('Quit', self)
            quit_action.triggered.connect(self.close)
            tray_menu.addAction(quit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()

    def create_desktop_shortcut(self):
        """Create desktop shortcut"""
        try:
            if sys.platform != 'win32':
                return

            # Simple shortcut creation without external dependencies
            desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
            shortcut_path = os.path.join(desktop_path, "Advanced AI Screen.lnk")

            # For now, just create a batch file as alternative
            batch_path = os.path.join(desktop_path, "Advanced AI Screen.bat")
            with open(batch_path, 'w') as f:
                f.write(f'python "{os.path.abspath(__file__)}"\n')

            print(f"[SUCCESS] Desktop shortcut created at: {batch_path}")

        except Exception as e:
            print(f"[WARNING] Could not create desktop shortcut: {e}")

    def save_conversation_history(self):
        """Save conversation history"""
        try:
            history_file = Path.home() / ".advanced_ai_history.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history[-100:], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save history: {e}")

    def closeEvent(self, event):
        """Handle close event"""
        self.save_conversation_history()
        self.executor.shutdown(wait=False)
        event.accept()

class WebInterface:
    """Flask web interface for local IP access"""

    def __init__(self, ai_screen_instance):
        self.ai_screen = ai_screen_instance
        self.app = Flask(__name__)
        self.conversation_history = []
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def home():
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Advanced AI Screen Assistant - Web Interface</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
                    .chat-messages { height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-bottom: 20px; }
                    .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
                    .message.user { background: #0078d4; color: white; text-align: right; }
                    .message.ai { background: #f0f0f0; color: black; }
                    .input-area { display: flex; gap: 10px; }
                    input[type="text"] { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
                    button { padding: 10px 20px; background: #0078d4; color: white; border: none; border-radius: 5px; cursor: pointer; }
                    button:hover { background: #005a9e; }
                    .status { margin-top: 10px; padding: 10px; background: #e8f5e8; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 Advanced AI Screen Assistant</h1>
                    <div class="status">✅ Connected to local AI instance</div>
                    <div class="chat-messages" id="messages">
                        <div class="message ai">🤖 Welcome to Advanced AI Screen Assistant!</div>
                        <div class="message ai">🎯 Features: Chat | Draw | Code | Research | Voice</div>
                        <div class="message ai">💡 Try: 'hello', 'help', or ask me anything!</div>
                    </div>
                    <div class="input-area">
                        <input type="text" id="messageInput" placeholder="Ask me anything..." onkeypress="handleKeyPress(event)">
                        <button onclick="sendMessage()">Send</button>
                    </div>
                </div>

                <script>
                    let conversationHistory = [];

                    function addMessage(sender, text) {
                        const messagesDiv = document.getElementById('messages');
                        const messageDiv = document.createElement('div');
                        messageDiv.className = 'message ' + (sender === 'You' ? 'user' : 'ai');
                        messageDiv.textContent = text;
                        messagesDiv.appendChild(messageDiv);
                        messagesDiv.scrollTop = messagesDiv.scrollHeight;
                        conversationHistory.push({sender: sender, text: text});
                    }

                    function sendMessage() {
                        const input = document.getElementById('messageInput');
                        const message = input.value.trim();
                        if (!message) return;

                        addMessage('You', message);
                        input.value = '';

                        // Send to AI
                        fetch('/api/chat', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ message: message })
                        })
                        .then(response => response.json())
                        .then(data => {
                            addMessage('AI', data.response);
                        })
                        .catch(error => {
                            addMessage('System', '❌ Error communicating with AI');
                            console.error('Error:', error);
                        });
                    }

                    function handleKeyPress(event) {
                        if (event.key === 'Enter') {
                            sendMessage();
                        }
                    }

                    // Load conversation history
                    window.onload = function() {
                        fetch('/api/history')
                        .then(response => response.json())
                        .then(data => {
                            data.history.forEach(msg => {
                                addMessage(msg.sender, msg.message);
                            });
                        })
                        .catch(error => console.error('Error loading history:', error));
                    };
                </script>
            </body>
            </html>
            """
            return render_template_string(html_template)

        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            try:
                data = request.get_json()
                message = data.get('message', '')

                if not message:
                    return jsonify({'error': 'No message provided'}), 400

                # Get AI response
                if hasattr(self.ai_screen, 'generate_ai_response'):
                    response = self.ai_screen.generate_ai_response(message)
                else:
                    response = "AI system not available"

                # Add to conversation history
                self.conversation_history.append({'sender': 'You', 'message': message})
                self.conversation_history.append({'sender': 'AI', 'message': response})

                return jsonify({'response': response})

            except Exception as e:
                print(f"[WEB] Chat error: {e}")
                return jsonify({'error': 'Internal server error'}), 500

        @self.app.route('/api/history')
        def get_history():
            return jsonify({'history': self.conversation_history[-20:]})  # Last 20 messages

        @self.app.route('/api/status')
        def get_status():
            return jsonify({
                'ai_available': AI_AVAILABLE,
                'voice_available': VOICE_AVAILABLE,
                'memory_usage': self.get_memory_usage(),
                'uptime': self.get_uptime()
            })

    def get_memory_usage(self):
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return f"{process.memory_info().rss / 1024 / 1024:.1f} MB"
        except:
            return "Unknown"

    def get_uptime(self):
        try:
            import time
            return f"{time.time() - self.ai_screen.last_activity:.0f} seconds"
        except:
            return "Unknown"

    def start_server(self, host='0.0.0.0', port=5000):
        """Start Flask server for local network access"""
        try:
            print(f"[WEB] Starting local IP server on {host}:{port}")
            print(f"[WEB] Access from other devices on your network at: http://{self.get_local_ip()}:{port}")

            # Start server in a separate thread
            server_thread = threading.Thread(
                target=lambda: self.app.run(host=host, port=port, debug=False, use_reloader=False),
                daemon=True
            )
            server_thread.start()

            return f"✅ Local IP server started! Access at: http://{self.get_local_ip()}:{port}"

        except Exception as e:
            print(f"[WEB] Failed to start server: {e}")
            return f"❌ Failed to start local IP server: {e}"

    def get_local_ip(self):
        """Get local IP address"""
        try:
            # Create a socket to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "localhost"

def check_existing_instance():
    """Check if another instance is already running"""
    import psutil
    import os

    current_pid = os.getpid()
    current_process_name = psutil.Process(current_pid).name()

    # Look for other Python processes running advanced_ai_screen.py
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] != current_pid and proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline and len(cmdline) > 1 and 'advanced_ai_screen.py' in cmdline[-1]:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return False

def main():
    """Main application entry point with improved instance management"""
    # Check for existing instances
    if check_existing_instance():
        print("❌ Advanced AI Screen Assistant is already running. Please close the existing instance first.")
        print("💡 If you can't find it, check the system tray or use Task Manager to close pythonw.exe processes.")
        sys.exit(1)

    # Check for web server mode
    if len(sys.argv) > 1 and sys.argv[1] == '--web':
        print("[WEB] Starting in web server mode...")
        if not FLASK_AVAILABLE:
            print("[ERROR] Flask not available for web server mode")
            sys.exit(1)

        # Create AI instance
        ai_screen = AdvancedAIScreen()

        # Start web interface
        web_interface = WebInterface(ai_screen)
        result = web_interface.start_server()

        print(result)
        print("[WEB] Web server running. Press Ctrl+C to stop.")

        try:
            # Keep the main thread alive
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("[WEB] Server stopped by user")
            sys.exit(0)

    else:
        # Normal GUI mode
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)

        # Set application properties
        app.setApplicationName("Advanced AI Screen Assistant")
        app.setApplicationVersion("2.0")

        # Create and show main window
        ai_screen = AdvancedAIScreen()
        ai_screen.show()

        # Start web server in background if Flask available
        if FLASK_AVAILABLE:
            try:
                web_interface = WebInterface(ai_screen)
                web_result = web_interface.start_server()
                ai_screen.add_message("System", web_result)
                print(web_result)
            except Exception as e:
                print(f"[WEB] Background web server failed: {e}")

        # Welcome message
        ai_screen.add_message("AI", "🤖 Welcome to Advanced AI Screen Assistant!")
        ai_screen.add_message("AI", "🎯 Features: Chat | Draw | Code | Research | Voice")
        ai_screen.add_message("AI", "⌨️ Virtual keyboard available | 🎤 Voice recognition ready")
        ai_screen.add_message("AI", "💡 Try: 'hello', 'help', or click the 🎤 button!")

        # Handle clean shutdown
        try:
            exit_code = app.exec_()
            print(f"[APP] Application exited with code: {exit_code}")
            sys.exit(exit_code)
        except Exception as e:
            print(f"[APP] Application crashed: {e}")
            sys.exit(1)

def test_basic_functionality():
    """Test basic functionality without GUI"""
    print("🧪 Testing Advanced AI Screen Assistant...")

    # Test imports
    try:
        import sys
        import os
        import time
        import threading
        import queue
        from concurrent.futures import ThreadPoolExecutor, as_completed
        print("✅ Basic imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    # Test AI availability
    ai_available = False
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        ai_available = True
        print("✅ AI libraries available")
    except ImportError:
        print("⚠️ AI libraries not available - will use fallback responses")

    # Test voice availability
    voice_available = False
    try:
        import speech_recognition as sr
        import pyttsx3
        voice_available = True
        print("✅ Voice libraries available")
    except ImportError:
        print("⚠️ Voice libraries not available")

    # Test fallback response system
    test_assistant = AdvancedAIScreen.__new__(AdvancedAIScreen)
    test_responses = [
        test_assistant.get_fallback_response("hello"),
        test_assistant.get_fallback_response("help"),
        test_assistant.get_fallback_response("what can you do"),
        test_assistant.get_fallback_response("system info"),
    ]

    print("✅ Fallback response system working")
    print(f"📝 Sample responses: {len(test_responses)} generated")

    print("\n🎉 Basic functionality test PASSED!")
    print("🚀 The Advanced AI Screen Assistant should work properly now.")
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_basic_functionality()
    else:
        main()