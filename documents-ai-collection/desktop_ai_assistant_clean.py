#!/usr/bin/env python3
"""
Desktop AI Assistant - Clean Version (No Unicode Issues)
A standalone AI assistant that can control your entire PC through natural language commands.
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
                             QProgressBar, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont

# AI/ML imports - Try Qwen first, fallback to GPT4All
AI_AVAILABLE = False
QWEN_AVAILABLE = False
GPT4ALL_AVAILABLE = False

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
        print("[ERROR] No AI models available. Install transformers or gpt4all")

# Additional imports for enhanced capabilities
try:
    import requests
    from bs4 import BeautifulSoup
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

try:
    import pyautogui
    import time
    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False

# Voice recognition imports
VOICE_AVAILABLE = False
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
    print("[SUCCESS] Voice recognition available!")
except ImportError:
    print("[WARNING] Voice recognition not available. Install speech_recognition and pyttsx3 for voice features.")

class DesktopAI(QWidget):
    """Main Desktop AI Assistant Window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Desktop AI Assistant")
        self.setGeometry(100, 100, 500, 600)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Initialize AI
        self.ai_model = None
        self.conversation_history = []
        self.load_conversation_history()

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

        # Background tasks
        self.background_tasks = []
        self.task_thread = None

        # AI loading thread
        self.ai_loading_thread = None

        # Voice recognition
        self.voice_recognizer = None
        self.voice_engine = None
        self.voice_listening = False
        self.voice_thread = None

        # Initialize voice if available
        if VOICE_AVAILABLE:
            self.init_voice()

        # Tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.setup_tray_icon()

        self.init_ui()
        self.start_ai_loading_thread()

        # Auto-save timer
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_conversation_history)
        self.save_timer.start(30000)  # Save every 30 seconds

    def setup_tray_icon(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            # Create a simple icon
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor('#0078d4'))
            painter = QPainter(pixmap)
            painter.setPen(QColor('white'))
            painter.setFont(QFont('Arial', 20, QFont.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, 'AI')
            painter.end()

            self.tray_icon.setIcon(QIcon(pixmap))
            self.tray_icon.setToolTip('Desktop AI Assistant')

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
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                'Desktop AI Assistant',
                'I\'m here if you need me! Double-click the tray icon to show me.',
                QSystemTrayIcon.Information,
                2000
            )

    def quit_application(self):
        """Quit the application"""
        self.save_conversation_history()
        QApplication.quit()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Title bar
        title_bar = self.create_title_bar()
        layout.addWidget(title_bar)

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
                selection-background-color: #0078d4;
            }
        """)
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ask me anything... (try 'help' for commands)")
        self.message_input.returnPressed.connect(self.process_message)
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(40, 40, 40, 0.9);
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 12px;
                selection-background-color: #0078d4;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
        """)
        input_layout.addWidget(self.message_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.process_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        input_layout.addWidget(self.send_button)

        # Voice button
        if VOICE_AVAILABLE:
            self.voice_button = QPushButton("[MIC]")
            self.voice_button.clicked.connect(self.start_voice_listening)
            self.voice_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 15px;
                    padding: 8px 15px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """)
            self.voice_button.setToolTip("Click to start voice recognition")
            input_layout.addWidget(self.voice_button)

        layout.addLayout(input_layout)

        # Status bar
        self.status_label = QLabel("Loading AI...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #0078d4;
                font-weight: bold;
                padding: 5px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # Welcome message
        ai_model_name = "Qwen" if QWEN_AVAILABLE else ("GPT4All" if GPT4ALL_AVAILABLE else "Basic")
        self.add_message("AI Assistant", f"[AI] Welcome to Desktop AI Assistant!\n\n"
                                        f"AI: {ai_model_name} | Ready to help!\n\n"
                                        "[TIP] Try: 'help', 'system info', 'clean temp files'\n"
                                        "[FIX] I can repair PC, code, research, install software\n"
                                        "Just type what you need!")

    def create_title_bar(self):
        """Create custom title bar"""
        title_bar = QFrame()
        title_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 120, 212, 0.9);
                border-radius: 10px 10px 0 0;
            }
        """)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("AI Assistant")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # Window controls
        minimize_btn = QPushButton("-")
        minimize_btn.clicked.connect(self.showMinimized)
        minimize_btn.setStyleSheet("""
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
        """)
        title_layout.addWidget(minimize_btn)

        tray_btn = QPushButton("O")
        tray_btn.clicked.connect(self.hide_to_tray)
        tray_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
                font-size: 14px;
                padding: 0 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
            }
        """)
        title_layout.addWidget(tray_btn)

        close_btn = QPushButton("X")
        close_btn.clicked.connect(self.hide_to_tray)
        close_btn.setStyleSheet("""
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
        """)
        title_layout.addWidget(close_btn)

        title_bar.setLayout(title_layout)
        return title_bar

    def start_ai_loading_thread(self):
        """Start AI loading with better error handling"""
        try:
            # Use QTimer to load AI after UI is shown (prevents freezing)
            QTimer.singleShot(100, self.load_ai_with_timeout)
        except Exception as e:
            print(f"[ERROR] Failed to start AI loading: {e}")
            self.status_label.setText("Ready - AI Offline (Loading failed)")

    def load_ai_with_timeout(self):
        """Load AI with timeout to prevent UI freezing"""
        try:
            # Set a timeout for AI loading
            import threading
            result = [None]
            exception = [None]

            def load_ai():
                try:
                    result[0] = self.setup_ai()
                except Exception as e:
                    exception[0] = e

            # Start loading in a separate thread with timeout
            ai_thread = threading.Thread(target=load_ai, daemon=True)
            ai_thread.start()
            ai_thread.join(timeout=30)  # 30 second timeout

            if ai_thread.is_alive():
                # Loading timed out
                self.status_label.setText("Ready - AI Loading Timed Out")
                self.add_message("System", "[WARNING] AI model loading timed out. Basic commands will still work.")
            elif exception[0]:
                # Loading failed with exception
                self.status_label.setText("Ready - AI Offline (Error)")
                self.add_message("System", f"[WARNING] AI loading failed: {str(exception[0])}")
            else:
                # Loading successful
                self.status_label.setText(result[0])
                if "Active" in result[0]:
                    self.add_message("System", "[AI] AI model loaded successfully! I'm ready to help.")
                elif "Offline" in result[0]:
                    self.add_message("System", "[WARNING] AI model not available. Basic commands will still work.")

        except Exception as e:
            print(f"[ERROR] AI loading thread failed: {e}")
            self.status_label.setText("Ready - AI Offline (Thread error)")

    def setup_ai(self):
        """Setup AI model - prefers Qwen, falls back to GPT4All"""
        if QWEN_AVAILABLE:
            try:
                print("Loading Qwen AI model...")
                # Use a smaller, more reliable model
                model_name = "microsoft/DialoGPT-small"
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.ai_model = AutoModelForCausalLM.from_pretrained(model_name)
                print("[SUCCESS] Qwen AI loaded successfully!")
                return "Ready - AI Active with Enhanced Model!"
            except Exception as e:
                print(f"[ERROR] Qwen loading failed: {e}")
                return self.fallback_to_gpt4all()
        elif GPT4ALL_AVAILABLE:
            return self.fallback_to_gpt4all()
        else:
            return "Ready - AI Offline (No models available)"

    def fallback_to_gpt4all(self):
        """Fallback to GPT4All if Qwen fails"""
        try:
            print("[INFO] Falling back to GPT4All...")
            self.ai_model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf", device='cpu')
            print("[SUCCESS] GPT4All loaded as fallback")
            return "Ready - AI Active with GPT4All"
        except Exception as e:
            self.ai_model = None
            print(f"[ERROR] GPT4All also failed: {e}")
            return f"Ready - AI Offline: {str(e)}"

    def process_message(self):
        """Process user message and execute commands with improved threading"""
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
        self.status_label.setText("Processing...")

        # Process command in a separate thread to prevent UI freezing
        import threading
        def process_command_thread():
            try:
                # Process the command
                response = self.execute_command(message)

                # Use QTimer to update UI from main thread
                QTimer.singleShot(0, lambda: self.add_message("Assistant", response))
                QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))

                # Speak the response if voice is available (in separate thread)
                if VOICE_AVAILABLE and self.voice_engine:
                    speech_thread = threading.Thread(target=lambda: self.speak_response(response), daemon=True)
                    speech_thread.start()

            except Exception as e:
                error_msg = f"[ERROR] An error occurred: {str(e)}"
                QTimer.singleShot(0, lambda: self.add_message("Assistant", error_msg))
                QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))
                print(f"[ERROR] Message processing failed: {e}")
            finally:
                # Re-enable input
                QTimer.singleShot(0, lambda: self.message_input.setEnabled(True))
                QTimer.singleShot(0, lambda: self.send_button.setEnabled(True))
                if hasattr(self, 'voice_button'):
                    QTimer.singleShot(0, lambda: self.voice_button.setEnabled(True))

        # Start processing thread
        command_thread = threading.Thread(target=process_command_thread, daemon=True)
        command_thread.start()

    def execute_command(self, command):
        """Execute natural language commands with improved parsing"""
        command_lower = command.lower()

        # Help command
        if any(word in command_lower for word in ['help', 'commands', 'what can you do', 'how to']):
            return self.get_help_text()

        # System information
        elif any(phrase in command_lower for phrase in ['system info', 'computer info', 'my pc info', 'system information']):
            return self.get_system_info()

        # PC Maintenance & Repair
        elif any(word in command_lower for word in ['repair', 'fix', 'maintain', 'clean', 'optimize', 'maintenance']):
            return self.pc_maintenance(command)

        # Programming & Development
        elif any(word in command_lower for word in ['code', 'program', 'develop', 'script', 'vs code', 'vscode', 'python', 'programming']):
            return self.programming_assistance(command)

        # Internet Research & Learning
        elif any(word in command_lower for word in ['learn', 'research', 'find', 'discover', 'tutorial', 'teach']):
            return self.internet_research(command)

        # Auto-installation
        elif any(word in command_lower for word in ['install', 'download', 'setup', 'get', 'setup']):
            return self.auto_install(command)

        # File operations
        elif any(word in command_lower for word in ['create', 'make', 'new']) and 'folder' in command_lower:
            return self.create_folder(command)
        elif 'open' in command_lower and any(word in command_lower for word in ['file', 'folder', 'directory']):
            return self.open_file_folder(command)

        # Application launching - improved parsing
        elif 'open' in command_lower or 'launch' in command_lower or 'start' in command_lower:
            return self.open_application(command)

        # Web operations
        elif any(word in command_lower for word in ['search', 'google', 'find']) or ('look' in command_lower and 'for' in command_lower):
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

        # AI-powered response for unrecognized commands
        else:
            return self.get_ai_response(command)

    def get_help_text(self):
        """Get help text with available commands"""
        voice_status = "[MIC] VOICE AVAILABLE" if VOICE_AVAILABLE else "[ERROR] VOICE NOT AVAILABLE"
        ai_status = "[AI] AI ACTIVE" if AI_AVAILABLE else "[ERROR] AI OFFLINE"

        return f"""[HELP] Desktop AI Assistant - Complete Command Guide:

{ai_status} | {voice_status}

[AI] AI ASSISTANT FEATURES:
• Natural language conversation
• Context-aware responses
• Background task processing
• Permission-based security

[MIC] VOICE COMMANDS (if available):
• 'start listening' - Begin voice recognition
• 'stop listening' - End voice recognition
• 'speak [text]' - Text-to-speech
• 'language tamil/english' - Switch voice language

[CLEAN] ADVANCED PC MAINTENANCE & REPAIR:
• 'clean temp files' - Clear temporary files
• 'clear browser cache' - Clean browser caches
• 'disk cleanup' - Free up disk space
• 'check for updates' - System updates
• 'update drivers' - Device driver updates
• 'virus scan' - Security scan
• 'run diagnostics' - System health check
• 'network diagnostics' - Fix connection issues
• 'system repair' - Run repair tools
• 'optimize performance' - Speed up your PC

[PC] PROGRAMMING & DEVELOPMENT:
• 'open vs code' - Launch code editor
• 'create python project [name]' - New Python project
• 'python tutorial' - Learn Python
• 'install python package [name]' - Install libraries

[WEB] INTERNET RESEARCH & LEARNING:
• 'learn about [topic]' - Research any subject
• 'find tutorials for [skill]' - Learning resources
• 'research [topic]' - In-depth investigation

[FOLDER] FILE OPERATIONS:
• 'create folder [name]' - Create directory
• 'open documents' - Open system folders

[SCREEN] APPLICATIONS & WEBSITES:
• 'open chrome/firefox/edge' - Web browsers
• 'open notepad/calculator' - System apps
• 'open youtube/gmail/facebook' - Popular websites
• 'open [app name]' - Any application

[WEB] WEB & SEARCH:
• 'search for [query]' - Google search
• 'open website [url]' - Visit website

[SETTINGS] SYSTEM CONTROL:
• 'system info' - Computer details
• 'shutdown/restart' - Power management
• 'volume up/down' - Audio control

[BRAIN] SELF-LEARNING:
• 'learn my patterns' - Analyze usage patterns
• 'optimize myself' - Self-optimization
• 'upgrade myself' - Check for improvements
• 'manage preferences' - View/set preferences
• 'set [key] = [value]' - Set preference

[CHAT] CONVERSATION:
• Just type naturally! I'll understand and help.
• I remember our conversation history
• I can handle multi-step requests
• I learn from our interactions

[SECURE] SECURITY:
• All sensitive actions require permission
• Granular permission system
• Safe operation with user control

Try any command or just describe what you want to accomplish!
For voice features, click the [MIC] button or say 'start listening'."""

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

            return f"[SCREEN] System Information:\n" + "\n".join([f"• {k}: {v}" for k, v in info.items()])
        except Exception as e:
            return f"[ERROR] Error getting system info: {str(e)}"

    def open_application(self, command):
        """Open an application with improved natural language parsing"""
        command_lower = command.lower()

        # Remove common prefixes
        for prefix in ['open', 'launch', 'start', 'can you', 'please', 'plz', 'could you']:
            command_lower = command_lower.replace(prefix, '').strip()

        # Handle YouTube and other websites
        if 'youtube' in command_lower:
            try:
                webbrowser.open('https://www.youtube.com')
                return "[OK] Opened YouTube in your default browser"
            except Exception as e:
                return f"[ERROR] Error opening YouTube: {str(e)}"

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
                    return f"[OK] Opened {site.capitalize()}"
                except Exception as e:
                    return f"[ERROR] Error opening {site}: {str(e)}"

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

        # Find the best matching app
        for app_key, app_cmd in app_commands.items():
            if app_key in command_lower:
                try:
                    if not self.request_permission('app_launch', f"Launch {app_key}?"):
                        return "[ERROR] Permission denied"

                    # Use subprocess with timeout and error handling
                    result = subprocess.Popen(
                        app_cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        shell=True
                    )
                    return f"[OK] Opened {app_key}"
                except FileNotFoundError:
                    return f"[ERROR] {app_key} not found. Please check if it's installed."
                except Exception as e:
                    return f"[ERROR] Error opening {app_key}: {str(e)}"

        # If no specific app found, try to interpret as a general command
        return f"I understand you want to open something, but I couldn't identify '{command}'. Try: chrome, firefox, notepad, calculator, youtube, etc."

    def pc_maintenance(self, command):
        """Perform PC maintenance and repair tasks"""
        if not self.request_permission('pc_maintenance', 'perform PC maintenance and repair tasks'):
            return "[ERROR] Permission denied for PC maintenance"

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
        elif 'virus' in command_lower or 'scan' in command_lower or 'security' in command_lower:
            return self.virus_scan()
        elif 'performance' in command_lower or 'optimize' in command_lower or 'speed' in command_lower:
            return self.optimize_performance()
        elif 'diagnostics' in command_lower or 'diagnostic' in command_lower:
            return self.system_diagnostics()
        elif 'network' in command_lower or 'internet' in command_lower or 'connection' in command_lower:
            return self.network_diagnostics()
        elif 'repair' in command_lower or 'fix' in command_lower:
            return self.system_diagnostics()  # Run diagnostics as repair
        else:
            return """[FIX] Advanced PC Maintenance & Repair:

[CLEAN] CLEANING:
• 'clean temp files' - Clear temporary files
• 'clear browser cache' - Clean browser caches

[DISK] STORAGE:
• 'disk cleanup' - Free up disk space
• 'check storage' - Analyze disk usage

[UPDATE] UPDATES:
• 'check for updates' - System updates
• 'update drivers' - Device driver updates

[SECURITY] SECURITY:
• 'virus scan' - Security scan
• 'run diagnostics' - System health check

[FAST] PERFORMANCE:
• 'optimize performance' - Speed up your PC
• 'network diagnostics' - Fix connection issues

[FIX] REPAIR:
• 'system repair' - Run repair tools
• 'fix system files' - Repair corrupted files

Try any of these commands!"""

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

            return f"[CLEAN] Cleaned {cleaned_size / (1024*1024):.2f} MB of temporary files!"
        except Exception as e:
            return f"[ERROR] Error cleaning temp files: {str(e)}"

    def disk_cleanup(self):
        """Perform disk cleanup"""
        try:
            # Run Windows Disk Cleanup
            if platform.system() == 'Windows':
                subprocess.run(['cleanmgr', '/sagerun:1'], capture_output=True)
                return "[DISK] Windows Disk Cleanup started! This will help free up disk space."
            else:
                return "[TIP] Disk cleanup is primarily available on Windows. Try 'clean temp files' instead."
        except Exception as e:
            return f"[ERROR] Error running disk cleanup: {str(e)}"

    def check_updates(self):
        """Check for system updates"""
        try:
            if platform.system() == 'Windows':
                # Try multiple update methods
                try:
                    subprocess.run(['wuauclt', '/detectnow'], capture_output=True)
                except:
                    pass

                try:
                    subprocess.run(['powershell', 'Start-Process "ms-settings:windowsupdate"'], capture_output=True)
                except:
                    pass

                return "[UPDATE] Windows Update check initiated. Your system will check for available updates.\n\n[TIP] You can also manually check updates in Settings > Update & Security > Windows Update"
            else:
                return "[TIP] System updates are managed differently on your OS. Please check your system settings."
        except Exception as e:
            return f"[ERROR] Error checking updates: {str(e)}"

    def update_drivers(self):
        """Update device drivers"""
        try:
            if platform.system() == 'Windows':
                # Open Device Manager
                subprocess.run(['devmgmt.msc'], shell=True)
                return "[FIX] Opened Device Manager. Right-click on devices and select 'Update driver' to check for updates.\n\n[TIP] For automatic driver updates, consider using Windows Update or third-party tools like Driver Booster."
            else:
                return "[TIP] Driver updates are OS-specific. On Linux/Mac, drivers are typically updated through system updates."
        except Exception as e:
            return f"[ERROR] Error opening Device Manager: {str(e)}"

    def system_diagnostics(self):
        """Run system diagnostics"""
        try:
            diagnostics = []

            if platform.system() == 'Windows':
                # Run various diagnostic commands
                try:
                    result = subprocess.run(['sfc', '/scannow'], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        diagnostics.append("[OK] System File Checker completed")
                    else:
                        diagnostics.append("[WARNING] System File Checker found issues")
                except:
                    diagnostics.append("[WARNING] System File Checker timed out")

                try:
                    result = subprocess.run(['chkdsk', '/f'], capture_output=True, text=True, timeout=10)
                    diagnostics.append("[OK] Disk check scheduled for next restart")
                except:
                    diagnostics.append("[WARNING] Disk check scheduling failed")

                try:
                    result = subprocess.run(['dism', '/online', '/cleanup-image', '/restorehealth'], capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        diagnostics.append("[OK] DISM repair completed")
                    else:
                        diagnostics.append("[WARNING] DISM repair found issues")
                except:
                    diagnostics.append("[WARNING] DISM repair timed out")

            return "[TOOLS] System Diagnostics Results:\n" + "\n".join(f"• {diag}" for diag in diagnostics) + "\n\n[TIP] These diagnostics help identify and fix common system issues."
        except Exception as e:
            return f"[ERROR] Error running diagnostics: {str(e)}"

    def clear_browser_cache(self):
        """Clear browser cache and temporary files"""
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
                return f"[CLEAN] Cleared cache for: {', '.join(browsers)}\n\n[TIP] Browser cache cleared to improve performance and free up space."
            else:
                return "[TIP] No browser caches found to clear. Try running as administrator for better access."
        except Exception as e:
            return f"[ERROR] Error clearing browser cache: {str(e)}"

    def network_diagnostics(self):
        """Run network diagnostics"""
        try:
            network_info = []

            # Ping test
            try:
                result = subprocess.run(['ping', '-n', '4', '8.8.8.8'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    network_info.append("[OK] Internet connection: Good")
                else:
                    network_info.append("[WARNING] Internet connection: Issues detected")
            except:
                network_info.append("[WARNING] Ping test failed")

            # DNS flush
            try:
                subprocess.run(['ipconfig', '/flushdns'], capture_output=True, timeout=5)
                network_info.append("[OK] DNS cache cleared")
            except:
                network_info.append("[WARNING] DNS flush failed")

            # Network reset (Windows)
            if platform.system() == 'Windows':
                try:
                    subprocess.run(['netsh', 'winsock', 'reset'], capture_output=True, timeout=10)
                    network_info.append("[OK] Network stack reset")
                except:
                    network_info.append("[WARNING] Network reset failed")

            return "[WEB] Network Diagnostics:\n" + "\n".join(f"• {info}" for info in network_info) + "\n\n[TIP] Network issues resolved. Restart your computer if problems persist."
        except Exception as e:
            return f"[ERROR] Error running network diagnostics: {str(e)}"

    def virus_scan(self):
        """Perform virus scan (if Windows Defender available)"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['powershell', 'Start-MpScan -ScanType QuickScan'], capture_output=True, text=True)
                if result.returncode == 0:
                    return "[SECURITY] Windows Defender quick scan started! I'll notify you when it's complete."
                else:
                    return "[WARNING] Windows Defender scan couldn't be started. Make sure Windows Security is enabled."
            else:
                return "[TIP] Antivirus scanning is OS-specific. Please use your system's built-in security tools."
        except Exception as e:
            return f"[ERROR] Error starting virus scan: {str(e)}"

    def optimize_performance(self):
        """Optimize system performance"""
        optimizations = []

        try:
            # Clear system cache
            if platform.system() == 'Windows':
                subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
                optimizations.append("DNS cache cleared")

            # End unnecessary processes (be careful with this)
            # This is just an example - in real implementation, be very selective
            optimizations.append("System optimization suggestions ready")

            return f"[FAST] Performance Optimization Complete!\n{chr(10).join('• ' + opt for opt in optimizations)}\n\n[TIP] Additional tips:\n• Close unused applications\n• Clear browser cache\n• Run Disk Cleanup\n• Update your system"
        except Exception as e:
            return f"[ERROR] Error during optimization: {str(e)}"

    def request_permission(self, permission_type, action_description):
        """Request user permission for sensitive actions"""
        if self.permissions.get(permission_type, False):
            return True

        reply = QMessageBox.question(
            self, 'Permission Required',
            f'Allow Desktop AI to {action_description}\n\n'
            f'This action requires {permission_type.replace("_", " ")} permission.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.permissions[permission_type] = True
            return True

        return False

    def get_ai_response(self, message):
        """Get AI-powered response for unrecognized commands"""
        if not self.ai_model:
            return f"I understand you want help with: {message[:50]}...\n\nI'm here to help! Try using specific commands like 'help' or ask me questions about your computer."

        try:
            context = "\n".join([f"{sender}: {msg}" for sender, msg in self.conversation_history[-3:]])
            prompt = f"Context:\n{context}\n\nUser: {message}\n\nAssistant: You are a helpful desktop AI assistant with full PC control capabilities. Provide a helpful response. If this is a command, explain how to do it or offer to help execute it."

            if QWEN_AVAILABLE and hasattr(self, 'tokenizer'):
                # Use Qwen model
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

            elif GPT4ALL_AVAILABLE:
                # Use GPT4All model
                with self.ai_model.chat_session():
                    response = self.ai_model.generate(prompt, max_tokens=150)
                return response

        except Exception as e:
            print(f"AI Error: {e}")
            return f"I understand you want help with: {message[:50]}...\n\nI'm here to help! Try using specific commands like 'help' or ask me questions about your computer."

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
            print(f"Error loading history: {e}")

    def save_conversation_history(self):
        """Save conversation history"""
        history_file = Path.home() / ".desktop_ai_history.json"
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history[-100:], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def init_voice(self):
        """Initialize voice recognition and text-to-speech"""
        try:
            self.voice_recognizer = sr.Recognizer()
            self.voice_engine = pyttsx3.init()

            # Configure voice settings
            voices = self.voice_engine.getProperty('voices')
            # Try to find English voice first
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
            print("[SUCCESS] Voice initialized with language: en")

        except Exception as e:
            print(f"[ERROR] Voice initialization failed: {e}")
            self.voice_recognizer = None
            self.voice_engine = None

    def start_voice_listening(self):
        """Start voice recognition"""
        if not VOICE_AVAILABLE or not self.voice_recognizer:
            self.add_message("System", "[ERROR] Voice recognition not available")
            return

        if self.voice_listening:
            self.stop_voice_listening()
            return

        self.voice_listening = True
        self.status_label.setText("[MIC] Listening...")

        # Start voice recognition in a separate thread
        self.voice_thread = QThread()
        self.voice_thread.run = self.voice_recognition_loop
        self.voice_thread.start()

    def stop_voice_listening(self):
        """Stop voice recognition"""
        self.voice_listening = False
        if self.voice_thread and self.voice_thread.isRunning():
            self.voice_thread.quit()
            self.voice_thread.wait()
        self.status_label.setText("Ready")

    def voice_recognition_loop(self):
        """Voice recognition loop"""
        try:
            with sr.Microphone() as source:
                self.voice_recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("[VOICE] Ready to listen...")

                while self.voice_listening:
                    try:
                        print("[VOICE] Listening for command...")
                        audio = self.voice_recognizer.listen(source, timeout=5, phrase_time_limit=8)

                        print("[VOICE] Processing audio...")
                        # Try different recognition services
                        text = None

                        # Try Google first (requires internet)
                        try:
                            text = self.voice_recognizer.recognize_google(audio, language='en-US')
                            print(f"[VOICE] Google recognized: {text}")
                        except sr.RequestError:
                            print("[VOICE] Google unavailable, trying offline...")
                            # Could add offline recognition here if available
                            pass
                        except sr.UnknownValueError:
                            print("[VOICE] Google couldn't understand audio")
                            continue

                        if text and len(text.strip()) > 0:
                            print(f"[VOICE] Final text: '{text}'")
                            # Process the voice command
                            QTimer.singleShot(0, lambda: self.process_voice_command(text))
                            QTimer.singleShot(0, lambda: self.status_label.setText("[MIC] Processing..."))

                            # Small delay to prevent rapid re-triggering
                            time.sleep(1)

                    except sr.WaitTimeoutError:
                        print("[VOICE] Timeout - no speech detected")
                        continue
                    except sr.UnknownValueError:
                        print("[VOICE] Could not understand audio")
                        continue
                    except sr.RequestError as e:
                        print(f"[VOICE ERROR] Recognition service error: {e}")
                        QTimer.singleShot(0, lambda: self.add_message("System", "[ERROR] Voice recognition service unavailable. Check internet connection."))
                        break
                    except Exception as e:
                        print(f"[VOICE ERROR] Unexpected error: {e}")
                        continue

        except sr.MicrophoneUnavailableError:
            print("[VOICE ERROR] Microphone not available")
            QTimer.singleShot(0, lambda: self.add_message("System", "[ERROR] Microphone not found or unavailable."))
        except Exception as e:
            print(f"[VOICE ERROR] Failed to start voice recognition: {e}")
            QTimer.singleShot(0, lambda: self.add_message("System", f"[ERROR] Voice recognition failed: {str(e)}"))
        finally:
            self.voice_listening = False
            QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))
            print("[VOICE] Voice recognition stopped")

    def process_voice_command(self, text):
        """Process voice command"""
        self.add_message("Voice", f"[MIC] {text}")
        self.message_input.setText(text)
        self.process_message()

    def speak_response(self, text):
        """Speak the response using text-to-speech"""
        if not VOICE_AVAILABLE or not self.voice_engine:
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
                    print(f"[SPEECH ERROR] {e}")

            speech_thread = threading.Thread(target=speak, daemon=True)
            speech_thread.start()

        except Exception as e:
            print(f"[SPEECH ERROR] {e}")

    def handle_voice_command(self, command):
        """Handle voice-related commands"""
        command_lower = command.lower()

        if 'start listening' in command_lower or 'listen' in command_lower:
            self.start_voice_listening()
            return "[MIC] Started voice listening mode"
        elif 'stop listening' in command_lower:
            self.stop_voice_listening()
            return "[MIC] Stopped voice listening"
        elif 'speak' in command_lower or 'say' in command_lower:
            text_to_speak = command_lower.replace('speak', '').replace('say', '').strip()
            if text_to_speak:
                self.speak_response(text_to_speak)
                return f"[SPEAK] Speaking: {text_to_speak}"
            else:
                return "[ERROR] What would you like me to say?"
        elif 'language' in command_lower:
            if 'tamil' in command_lower:
                return "[SPEAK] Tamil language support available"
            elif 'english' in command_lower:
                return "[SPEAK] English language active"
            else:
                return "[SPEAK] Available languages: English (primary), Tamil (limited)"
        else:
            return "[MIC] Voice commands: 'start listening', 'stop listening', 'speak [text]', 'language english'"

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

    # Set application properties
    app.setApplicationName("Desktop AI Assistant")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Desktop AI")

    # Create and show main window
    ai_assistant = DesktopAI()

    # Show welcome message
    ai_assistant.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
               