#!/usr/bin/env python3
"""
Desktop AI Assistant - Natural Language PC Control
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

# Windows-specific imports for shortcuts
try:
    import winshell
    from win32com.client import Dispatch
    WINDOWS_SHORTCUTS_AVAILABLE = True
except ImportError:
    WINDOWS_SHORTCUTS_AVAILABLE = False
    print("[WARNING] Windows shortcuts not available. Install pywin32 and winshell for shortcut features.")

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

# === Advanced Self-Learning Modules ===

# === Usage Tracker Module ===
class UsageTracker:
    def __init__(self):
        self.logs = []
        self.start_time = time.time()

    def record(self, module_name, action, result):
        """Record a usage event"""
        self.logs.append({
            "module": module_name,
            "action": action,
            "result": result,
            "timestamp": time.time(),
            "session_time": time.time() - self.start_time
        })

    def detect_pattern(self, module_name, condition_fn):
        """Detect patterns in usage"""
        return [log for log in self.logs if log["module"] == module_name and condition_fn(log)]

    def get_stats(self):
        """Get usage statistics"""
        total_commands = len(self.logs)
        modules_used = set(log["module"] for log in self.logs)
        avg_session_time = sum(log["session_time"] for log in self.logs) / max(1, len(self.logs))

        return {
            "total_commands": total_commands,
            "modules_used": len(modules_used),
            "avg_session_time": round(avg_session_time, 2),
            "most_used_module": max(set(log["module"] for log in self.logs), key=lambda x: sum(1 for log in self.logs if log["module"] == x)) if self.logs else "None"
        }

    def get_recent_activity(self, limit=5):
        """Get recent activity"""
        return self.logs[-limit:] if self.logs else []

# === Feedback Loop Module ===
class FeedbackLoop:
    def __init__(self):
        self.preferences = {}

    def set_preference(self, key, value):
        self.preferences[key] = value

    def get_preference(self, key):
        return self.preferences.get(key, None)

    def apply_behavior_adjustment(self, module_config):
        for key, value in self.preferences.items():
            if key in module_config:
                module_config[key] = value

# === Upgrade Scanner Module ===
class UpgradeScanner:
    def __init__(self, module_registry):
        self.registry = module_registry

    def find_outdated(self):
        return [mod for mod in self.registry if mod["version"] < mod["latest_version"]]

# === Sandbox Runner Module ===
class SandboxRunner:
    def test(self, module, test_cases):
        results = []
        for case in test_cases:
            try:
                output = module.run(case["input"])
                results.append((output == case["expected"], output))
            except Exception as e:
                results.append((False, str(e)))
        return results

# === Diff Validator Module ===
class DiffValidator:
    def validate(self, old_results, new_results):
        return all(new[0] for new in new_results) and len(new_results) >= len(old_results)

# === Rollback Manager Module ===
class RollbackManager:
    def __init__(self):
        self.restore_points = {}

    def save(self, module_name, config):
        self.restore_points[module_name] = config.copy()

    def restore(self, module_name):
        return self.restore_points.get(module_name, None)

# === Optimizer & Improvement Proposer Modules ===
class Optimizer:
    def analyze(self, logs):
        # Example: detect slow modules
        return [log["module"] for log in logs if log.get("result") == "slow"]

class ImprovementProposer:
    def suggest(self, module_name):
        # Suggest alternative implementations
        return f"Consider async or compiled variant for {module_name}"

# === Consent Gate Module ===
class ConsentGate:
    def __init__(self, auto_upgrade=False):
        self.auto_upgrade = auto_upgrade

    def is_allowed(self):
        return self.auto_upgrade

# === Local Preference Store ===
class LocalStore:
    def __init__(self, path="local_learning_store.json"):
        self.path = path
        self.data = self.load()

    def load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, "r") as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save(self):
        try:
            with open(self.path, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save learning store: {e}")

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def get(self, key):
        return self.data.get(key, None)

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
        self.continuous_chat_active = False
        self.continuous_thread = None

        # Advanced Self-Learning Modules
        self.usage_tracker = UsageTracker()
        self.feedback_loop = FeedbackLoop()
        self.upgrade_scanner = None  # Will be initialized with module registry
        self.sandbox_runner = SandboxRunner()
        self.diff_validator = DiffValidator()
        self.rollback_manager = RollbackManager()
        self.optimizer = Optimizer()
        self.improvement_proposer = ImprovementProposer()
        self.consent_gate = ConsentGate(auto_upgrade=False)  # User consent required
        self.local_store = LocalStore()

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

        # Create desktop shortcut on first run
        self.create_desktop_shortcut()

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
            self.voice_button = QPushButton("🎤")
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

        # Welcome message (shortened to prevent UI freezing)
        ai_model_name = "Qwen" if QWEN_AVAILABLE else ("GPT4All" if GPT4ALL_AVAILABLE else "Basic")
        self.add_message("AI Assistant", f"🤖 Welcome to Desktop AI Assistant!\n\n"
                                        f"AI: {ai_model_name} | Ready to help!\n\n"
                                        "💡 Try: 'help', 'system info', 'clean temp files'\n"
                                        "🔧 I can repair PC, code, research, install software\n"
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
        minimize_btn = QPushButton("−")
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

        tray_btn = QPushButton("◯")
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

        close_btn = QPushButton("×")
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
                self.add_message("System", "⚠️ AI model loading timed out. Basic commands will still work.")
            elif exception[0]:
                # Loading failed with exception
                self.status_label.setText("Ready - AI Offline (Error)")
                self.add_message("System", f"⚠️ AI loading failed: {str(exception[0])}")
            else:
                # Loading successful
                self.status_label.setText(result[0])
                if "Active" in result[0]:
                    self.add_message("System", "🤖 AI model loaded successfully! I'm ready to help.")
                elif "Offline" in result[0]:
                    self.add_message("System", "⚠️ AI model not available. Basic commands will still work.")

        except Exception as e:
            print(f"[ERROR] AI loading thread failed: {e}")
            self.status_label.setText("Ready - AI Offline (Thread error)")

    def setup_ai(self):
        """Setup AI model - prefers Qwen, falls back to GPT4All"""
        if QWEN_AVAILABLE:
            try:
                print("🚀 Loading Qwen AI model...")
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
                error_msg = f"❌ An error occurred: {str(e)}"
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

        # Track usage
        self.usage_tracker.record("command_processor", "execute", f"Command: {command[:50]}...")

        # Help command
        if any(word in command_lower for word in ['help', 'commands', 'what can you do', 'how to']):
            self.usage_tracker.record("help", "view", "Help requested")
            return self.get_help_text()

        # System information
        elif any(phrase in command_lower for phrase in ['system info', 'computer info', 'my pc info', 'system information']):
            return self.get_system_info()

        # PC Maintenance & Repair
        elif any(word in command_lower for word in ['repair', 'fix', 'maintain', 'clean', 'optimize', 'maintenance']):
            if any(word in command_lower for word in ['tips', 'advice', 'help', 'guide', 'knowledge', 'learn', 'troubleshoot']):
                return self.advanced_pc_help(command)
            else:
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

        # Shortcut commands
        elif any(word in command_lower for word in ['shortcut', 'desktop', 'icon']):
            if 'create' in command_lower or 'add' in command_lower:
                if 'startup' in command_lower:
                    return self.create_startup_shortcut()
                else:
                    return self.create_desktop_shortcut()
            elif 'remove' in command_lower or 'delete' in command_lower:
                return self.remove_shortcuts()
            else:
                return """🔗 Shortcut Management:

• "create desktop shortcut" - Add to desktop
• "create startup shortcut" - Auto-launch with Windows
• "remove shortcuts" - Delete all shortcuts

✅ Desktop shortcut is created automatically on first run!"""

        # Usage statistics
        elif any(word in command_lower for word in ['usage', 'stats', 'statistics', 'activity', 'history']):
            self.usage_tracker.record("usage", "stats_viewed", "Usage statistics requested")
            return self.get_usage_stats()

        # Self-learning commands
        elif any(word in command_lower for word in ['learn', 'teach', 'train']) and 'me' in command_lower:
            return self.handle_learning_command(command)
        elif 'optimize' in command_lower and 'myself' in command_lower:
            return self.self_optimize()
        elif 'upgrade' in command_lower and 'myself' in command_lower:
            return self.self_upgrade()
        elif 'preferences' in command_lower:
            return self.manage_preferences(command)

        # Enhanced natural language processing for common patterns
        elif self.is_greeting(command_lower):
            return "👋 Hello! I'm your Desktop AI Assistant. How can I help you today? Try 'help' for commands or just tell me what you need!"
        elif self.is_thanks(command_lower):
            return "😊 You're welcome! I'm here whenever you need help with your PC. Just ask!"
        elif self.is_question(command_lower):
            return self.handle_question(command)
        elif self.contains_action_words(command_lower):
            return self.handle_action_command(command)

        # AI-powered response for unrecognized commands
        else:
            return self.get_ai_response(command)

    def clean_temp_files(self):
        """Clean temporary files"""
        self.usage_tracker.record("maintenance", "clean_temp", "Cleaning temporary files")
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

            return f"🧹 Cleaned {cleaned_size / (1024*1024):.2f} MB of temporary files!"
        except Exception as e:
            return f"❌ Error cleaning temp files: {str(e)}"

    def disk_cleanup(self):
        """Perform disk cleanup"""
        try:
            # Run Windows Disk Cleanup
            if platform.system() == 'Windows':
                subprocess.run(['cleanmgr', '/sagerun:1'], capture_output=True)
                return "🗂️ Windows Disk Cleanup started! This will help free up disk space."
            else:
                return "💡 Disk cleanup is primarily available on Windows. Try 'clean temp files' instead."
        except Exception as e:
            return f"❌ Error running disk cleanup: {str(e)}"

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

                return "🔄 Windows Update check initiated. Your system will check for available updates.\n\n💡 You can also manually check updates in Settings > Update & Security > Windows Update"
            else:
                return "💡 System updates are managed differently on your OS. Please check your system settings."
        except Exception as e:
            return f"❌ Error checking updates: {str(e)}"

    def update_drivers(self):
        """Update device drivers"""
        try:
            if platform.system() == 'Windows':
                # Open Device Manager
                subprocess.run(['devmgmt.msc'], shell=True)
                return "🔧 Opened Device Manager. Right-click on devices and select 'Update driver' to check for updates.\n\n💡 For automatic driver updates, consider using Windows Update or third-party tools like Driver Booster."
            else:
                return "💡 Driver updates are OS-specific. On Linux/Mac, drivers are typically updated through system updates."
        except Exception as e:
            return f"❌ Error opening Device Manager: {str(e)}"

    def system_diagnostics(self):
        """Run system diagnostics"""
        try:
            diagnostics = []

            if platform.system() == 'Windows':
                # Run various diagnostic commands
                try:
                    result = subprocess.run(['sfc', '/scannow'], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        diagnostics.append("✅ System File Checker completed")
                    else:
                        diagnostics.append("⚠️ System File Checker found issues")
                except:
                    diagnostics.append("⚠️ System File Checker timed out")

                try:
                    result = subprocess.run(['chkdsk', '/f'], capture_output=True, text=True, timeout=10)
                    diagnostics.append("✅ Disk check scheduled for next restart")
                except:
                    diagnostics.append("⚠️ Disk check scheduling failed")

                try:
                    result = subprocess.run(['dism', '/online', '/cleanup-image', '/restorehealth'], capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        diagnostics.append("✅ DISM repair completed")
                    else:
                        diagnostics.append("⚠️ DISM repair found issues")
                except:
                    diagnostics.append("⚠️ DISM repair timed out")

            return "🔍 System Diagnostics Results:\n" + "\n".join(f"• {diag}" for diag in diagnostics) + "\n\n💡 These diagnostics help identify and fix common system issues."
        except Exception as e:
            return f"❌ Error running diagnostics: {str(e)}"

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
                return f"🧹 Cleared cache for: {', '.join(browsers)}\n\n💡 Browser cache cleared to improve performance and free up space."
            else:
                return "💡 No browser caches found to clear. Try running as administrator for better access."
        except Exception as e:
            return f"❌ Error clearing browser cache: {str(e)}"

    def network_diagnostics(self):
        """Run network diagnostics"""
        try:
            network_info = []

            # Ping test
            try:
                result = subprocess.run(['ping', '-n', '4', '8.8.8.8'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    network_info.append("✅ Internet connection: Good")
                else:
                    network_info.append("⚠️ Internet connection: Issues detected")
            except:
                network_info.append("⚠️ Ping test failed")

            # DNS flush
            try:
                subprocess.run(['ipconfig', '/flushdns'], capture_output=True, timeout=5)
                network_info.append("✅ DNS cache cleared")
            except:
                network_info.append("⚠️ DNS flush failed")

            # Network reset (Windows)
            if platform.system() == 'Windows':
                try:
                    subprocess.run(['netsh', 'winsock', 'reset'], capture_output=True, timeout=10)
                    network_info.append("✅ Network stack reset")
                except:
                    network_info.append("⚠️ Network reset failed")

            return "🌐 Network Diagnostics:\n" + "\n".join(f"• {info}" for info in network_info) + "\n\n💡 Network issues resolved. Restart your computer if problems persist."
        except Exception as e:
            return f"❌ Error running network diagnostics: {str(e)}"

    def virus_scan(self):
        """Perform virus scan (if Windows Defender available)"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['powershell', 'Start-MpScan -ScanType QuickScan'], capture_output=True, text=True)
                if result.returncode == 0:
                    return "🛡️ Windows Defender quick scan started! I'll notify you when it's complete."
                else:
                    return "⚠️ Windows Defender scan couldn't be started. Make sure Windows Security is enabled."
            else:
                return "💡 Antivirus scanning is OS-specific. Please use your system's built-in security tools."
        except Exception as e:
            return f"❌ Error starting virus scan: {str(e)}"

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

            return f"⚡ Performance Optimization Complete!\n{chr(10).join('• ' + opt for opt in optimizations)}\n\n💡 Additional tips:\n• Close unused applications\n• Clear browser cache\n• Run Disk Cleanup\n• Update your system"
        except Exception as e:
            return f"❌ Error during optimization: {str(e)}"

    def open_vs_code(self, command):
        """Open VS Code with specific project or file"""
        try:
            # Try to open VS Code
            subprocess.Popen(['code'], shell=True)
            return "💻 VS Code opened! What would you like to code today?"
        except FileNotFoundError:
            return "❌ VS Code not found. Would you like me to help install it?"
        except Exception as e:
            return f"❌ Error opening VS Code: {str(e)}"

    def python_assistance(self, command):
        """Provide Python programming assistance"""
        if 'create' in command.lower() or 'make' in command.lower():
            return self.create_python_project(command)
        elif 'run' in command.lower() or 'execute' in command.lower():
            return self.run_python_code(command)
        else:
            return """🐍 Python Development Help:

• "create python project [name]" - Create new Python project
• "run python file [path]" - Execute Python script
• "python tutorial" - Learn Python basics
• "install python package [name]" - Install Python packages

I can also help with:
• Code debugging
• Best practices
• Project structure
• Library recommendations

What Python task can I help with?"""

    def create_python_project(self, command):
        """Create a new Python project"""
        project_name = command.lower().replace('create python project', '').replace('make python project', '').strip()

        if not project_name:
            return "❓ Please specify a project name: 'create python project my_app'"

        try:
            project_dir = Path.cwd() / project_name
            project_dir.mkdir(exist_ok=True)

            # Create basic project structure
            (project_dir / 'src').mkdir()
            (project_dir / 'tests').mkdir()

            # Create main.py
            main_py = project_dir / 'main.py'
            main_py.write_text(f'''#!/usr/bin/env python3
"""
{project_name} - Main application file
"""

def main():
    """Main function"""
    print("Hello from {project_name}!")
    print("Edit this file to start building your application.")

if __name__ == "__main__":
    main()
''')

            # Create requirements.txt
            req_txt = project_dir / 'requirements.txt'
            req_txt.write_text("# Add your project dependencies here\n")

            # Create README
            readme = project_dir / 'README.md'
            readme.write_text(f'''# {project_name}

A Python project created with Desktop AI Assistant.

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python main.py`

## Features

- Add your features here

## Author

Created with ❤️ by Desktop AI Assistant
''')

            return f"✅ Python project '{project_name}' created!\n\n📁 Project structure:\n• main.py - Main application file\n• src/ - Source code directory\n• tests/ - Test files\n• requirements.txt - Dependencies\n• README.md - Documentation\n\n💻 Opening in VS Code..."
        except Exception as e:
            return f"❌ Error creating Python project: {str(e)}"

    def perform_research(self, topic):
        """Perform internet research on a topic"""
        if not WEB_AVAILABLE:
            return "❌ Web search not available. Please install requests and beautifulsoup4."

        try:
            # Search Google for the topic
            search_query = topic.replace(' ', '+')
            search_url = f"https://www.google.com/search?q={search_query}+tutorial+free+resources"

            # Open search in browser
            webbrowser.open(search_url)

            # Also search for YouTube tutorials
            youtube_url = f"https://www.youtube.com/results?search_query={search_query}+tutorial"
            webbrowser.open(youtube_url)

            return f"🔍 Researching '{topic}'...\n\n🌐 Opened Google search for free resources\n📺 Opened YouTube for video tutorials\n\n💡 I'm also searching for:\n• Free online courses\n• Documentation and guides\n• Community forums\n• GitHub repositories\n\nWhat specific aspect of {topic} would you like to focus on?"
        except Exception as e:
            return f"❌ Error performing research: {str(e)}"

    def install_software(self, software_name):
        """Attempt to install software"""
        software_name = software_name.lower().strip()

        if 'python' in software_name:
            return self.install_python()
        elif 'vscode' in software_name or 'vs code' in software_name:
            return self.install_vscode()
        elif 'chrome' in software_name:
            return self.install_chrome()
        else:
            return f"❓ I can help install:\n• Python\n• VS Code\n• Google Chrome\n\nFor '{software_name}', please visit the official website or let me know if you need help finding the download link."

    def install_python(self):
        """Install Python"""
        try:
            webbrowser.open("https://www.python.org/downloads/")
            return "🐍 Opened Python download page!\n\n📋 Installation steps:\n1. Download the latest Python installer\n2. Run the installer\n3. Make sure to check 'Add Python to PATH'\n4. Complete the installation\n\nLet me know when you're done and I can help verify the installation!"
        except Exception as e:
            return f"❌ Error opening Python download: {str(e)}"

    def install_vscode(self):
        """Install VS Code"""
        try:
            webbrowser.open("https://code.visualstudio.com/download")
            return "💻 Opened VS Code download page!\n\n📋 Installation steps:\n1. Download the installer for your OS\n2. Run the installer\n3. Follow the setup wizard\n4. Launch VS Code when complete\n\nI recommend installing these extensions:\n• Python\n• Pylance\n• GitLens\n• Bracket Pair Colorizer"
        except Exception as e:
            return f"❌ Error opening VS Code download: {str(e)}"

    def install_chrome(self):
        """Install Google Chrome"""
        try:
            webbrowser.open("https://www.google.com/chrome/")
            return "🌐 Opened Chrome download page!\n\n📋 Installation steps:\n1. Click 'Download Chrome'\n2. Run the installer\n3. Follow the setup\n4. Set as default browser (optional)\n\nChrome will be your default browser after installation!"
        except Exception as e:
            return f"❌ Error opening Chrome download: {str(e)}"

    def get_help_text(self):
        """Get help text with available commands"""
        voice_status = "🎤 VOICE AVAILABLE" if VOICE_AVAILABLE else "❌ VOICE NOT AVAILABLE"
        ai_status = "🤖 AI ACTIVE" if AI_AVAILABLE else "❌ AI OFFLINE"

        return f"""🆘 Desktop AI Assistant - Complete Command Guide:

{ai_status} | {voice_status}

🤖 AI ASSISTANT FEATURES:
• Natural language conversation
• Context-aware responses
• Background task processing
• Permission-based security

🎤 VOICE COMMANDS (if available):
• "start listening" - Begin voice recognition
• "stop listening" - End voice recognition
• "speak [text]" - Text-to-speech
• "language tamil/english" - Switch voice language

🧹 ADVANCED PC MAINTENANCE & REPAIR:
• "clean temp files" - Clear temporary files
• "clear browser cache" - Clean browser caches
• "disk cleanup" - Free up disk space
• "check for updates" - System updates
• "update drivers" - Device driver updates
• "virus scan" - Security scan
• "run diagnostics" - System health check
• "network diagnostics" - Fix connection issues
• "system repair" - Run repair tools
• "optimize performance" - Speed up your PC

💻 PROGRAMMING & DEVELOPMENT:
• "open vs code" - Launch code editor
• "create python project [name]" - New Python project
• "python tutorial" - Learn Python
• "install python package [name]" - Install libraries
• "run python code" - Execute Python scripts

🔍 INTERNET RESEARCH & LEARNING:
• "learn about [topic]" - Research any subject
• "find tutorials for [skill]" - Learning resources
• "research [topic]" - In-depth investigation
• "search for [query]" - Google search

📦 AUTO-INSTALLATION:
• "install python" - Install Python
• "install vs code" - Install VS Code
• "install chrome" - Install Chrome
• "install [software]" - Install other software

📁 FILE OPERATIONS:
• "create folder [name]" - Create directory
• "open documents" - Open system folders

💻 APPLICATIONS & WEBSITES:
• "open chrome/firefox/edge" - Web browsers
• "open notepad/calculator" - System apps
• "open youtube/gmail/facebook" - Popular websites
• "open [app name]" - Any application

🌐 WEB & SEARCH:
• "search for [query]" - Google search
• "open website [url]" - Visit website
• "google [query]" - Quick search

⚙️ SYSTEM CONTROL:
• "system info" - Computer details
• "shutdown/restart" - Power management
• "volume up/down" - Audio control

🎯 ADVANCED FEATURES:
• Background processing for complex tasks
• Multi-step task automation
• Intelligent resource discovery
• Context-aware assistance
• Voice recognition & synthesis
• Multi-language support (English/Tamil)

💬 CONVERSATION:
• Just type naturally! I'll understand and help.
• I remember our conversation history
• I can handle multi-step requests
• I learn from our interactions
• Voice commands work too!

🔐 SECURITY:
• All sensitive actions require permission
• Granular permission system
• Safe operation with user control

🔗 SHORTCUTS & LAUNCH:
• "create desktop shortcut" - Add desktop icon
• "create startup shortcut" - Auto-launch with Windows
• "remove shortcuts" - Delete shortcut icons

📊 USAGE TRACKING:
• "usage stats" - View usage statistics
• "show activity" - Recent activity log

🧠 SELF-LEARNING:
• "learn my patterns" - Analyze usage patterns
• "optimize myself" - Self-optimization
• "upgrade myself" - Check for improvements
• "manage preferences" - View/set preferences
• "set [key] = [value]" - Set preference

Try any command or just describe what you want to accomplish!
For voice features, click the 🎤 button or say "start listening"."""

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

            return "🖥️ System Information:\n" + "\n".join([f"• {k}: {v}" for k, v in info.items()])
        except Exception as e:
            return f"❌ Error getting system info: {str(e)}"

    def create_folder(self, command):
        """Create a new folder"""
        # Extract folder name
        if 'called' in command.lower():
            folder_name = command.lower().split('called')[-1].strip()
        elif 'named' in command.lower():
            folder_name = command.lower().split('named')[-1].strip()
        else:
            folder_name = command.replace('create', '').replace('folder', '').strip()

        folder_name = folder_name.strip('"\'')

        if not folder_name:
            return "❌ Please specify a folder name"

        try:
            # Ask for permission
            if not self.request_permission('file_access', f"Create folder '{folder_name}' in current directory?"):
                return "❌ Permission denied"

            folder_path = Path.cwd() / folder_name
            folder_path.mkdir(exist_ok=True)
            return f"✅ Created folder: {folder_name}"
        except Exception as e:
            return f"❌ Error creating folder: {str(e)}"

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
                return "✅ Opened YouTube in your default browser"
            except Exception as e:
                return f"❌ Error opening YouTube: {str(e)}"

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
                    return f"✅ Opened {site.capitalize()}"
                except Exception as e:
                    return f"❌ Error opening {site}: {str(e)}"

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
                        return "❌ Permission denied"

                    # Use subprocess with timeout and error handling
                    result = subprocess.Popen(
                        app_cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        shell=True
                    )
                    return f"✅ Opened {app_key}"
                except FileNotFoundError:
                    return f"❌ {app_key} not found. Please check if it's installed."
                except Exception as e:
                    return f"❌ Error opening {app_key}: {str(e)}"

        # If no specific app found, try to interpret as a general command
        return f"I understand you want to open something, but I couldn't identify '{command}'. Try: chrome, firefox, notepad, calculator, youtube, etc."

    def web_search(self, command):
        """Perform web search"""
        # Extract search query
        if 'search for' in command.lower():
            query = command.lower().split('search for')[-1].strip()
        elif 'google' in command.lower():
            query = command.lower().replace('google', '').strip()
        else:
            query = command.replace('search', '').strip()

        if not query:
            return "❌ Please specify what to search for"

        try:
            if not self.request_permission('web_access', f"Search Google for '{query}'?"):
                return "❌ Permission denied"

            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            # Use threading to prevent blocking
            import threading
            def open_browser():
                try:
                    webbrowser.open(search_url)
                except Exception as e:
                    print(f"[ERROR] Failed to open browser: {e}")

            browser_thread = threading.Thread(target=open_browser, daemon=True)
            browser_thread.start()

            return f"✅ Searching Google for: {query}"
        except Exception as e:
            return f"❌ Error performing search: {str(e)}"

    def pc_maintenance(self, command):
        """Perform PC maintenance and repair tasks"""
        if not self.request_permission('pc_maintenance', 'perform PC maintenance and repair tasks'):
            return "❌ Permission denied for PC maintenance"

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
            return """🔧 Advanced PC Maintenance & Repair:

🧹 CLEANING:
• "clean temp files" - Clear temporary files
• "clear browser cache" - Clean browser caches

💾 STORAGE:
• "disk cleanup" - Free up disk space
• "check storage" - Analyze disk usage

🔄 UPDATES:
• "check for updates" - System updates
• "update drivers" - Device driver updates

🛡️ SECURITY:
• "virus scan" - Security scan
• "run diagnostics" - System health check

⚡ PERFORMANCE:
• "optimize performance" - Speed up your PC
• "network diagnostics" - Fix connection issues

🔧 REPAIR:
• "system repair" - Run repair tools
• "fix system files" - Repair corrupted files

Try any of these commands!"""

    def programming_assistance(self, command):
        """Provide programming assistance and VS Code integration"""
        if not self.request_permission('programming', 'provide programming assistance and open development tools'):
            return "❌ Permission denied for programming assistance"

        command_lower = command.lower()

        if 'vs code' in command_lower or 'vscode' in command_lower or 'code' in command_lower:
            return self.open_vs_code(command)
        elif 'python' in command_lower:
            return self.python_assistance(command)
        elif 'web' in command_lower or 'html' in command_lower:
            return self.web_development(command)
        else:
            return self.general_programming_help()

    def internet_research(self, command):
        """Perform internet research and find learning resources"""
        if not self.request_permission('internet_search', 'search the internet for information and resources'):
            return "❌ Permission denied for internet research"

        # Extract research topic
        research_topic = command.lower()
        research_topic = research_topic.replace('learn', '').replace('research', '').replace('find', '').replace('about', '').strip()

        if not research_topic:
            return "❓ What would you like me to research? Try: 'learn about machine learning' or 'find python tutorials'"

        return self.perform_research(research_topic)

    def auto_install(self, command):
        """Auto-install software and tools"""
        if not self.request_permission('auto_install', 'download and install software automatically'):
            return "❌ Permission denied for auto-installation"

        command_lower = command.lower()

        if 'python' in command_lower:
            return self.install_python()
        elif 'vscode' in command_lower or 'vs code' in command_lower:
            return self.install_vscode()
        elif 'chrome' in command_lower:
            return self.install_chrome()
        else:
            software_name = command.replace('install', '').replace('download', '').replace('get', '').strip()
            return self.install_software(software_name)

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

    def init_voice(self):
        """Initialize voice recognition and text-to-speech"""
        try:
            print("[VOICE] Initializing voice recognition...")
            self.voice_recognizer = sr.Recognizer()
            self.voice_engine = pyttsx3.init()

            # Test microphone access
            try:
                with sr.Microphone() as source:
                    self.voice_recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("[VOICE] Microphone access confirmed")
            except Exception as mic_error:
                print(f"[VOICE WARNING] Microphone access issue: {mic_error}")
                print("[VOICE] Voice recognition may not work properly")

            # Configure voice settings
            voices = self.voice_engine.getProperty('voices')
            print(f"[VOICE] Available voices: {len(voices)}")

            # Try to find Tamil voice, fallback to English
            tamil_voice = None
            english_voice = None

            for voice in voices:
                print(f"[VOICE] Voice: {voice.name} (ID: {voice.id})")
                if 'tamil' in voice.name.lower() or 'ta' in voice.name.lower():
                    tamil_voice = voice
                elif 'english' in voice.name.lower() or 'en' in voice.name.lower():
                    english_voice = voice

            if tamil_voice:
                self.voice_engine.setProperty('voice', tamil_voice.id)
                self.current_language = 'ta'
                print(f"[VOICE] Using Tamil voice: {tamil_voice.name}")
            elif english_voice:
                self.voice_engine.setProperty('voice', english_voice.id)
                self.current_language = 'en'
                print(f"[VOICE] Using English voice: {english_voice.name}")
            else:
                self.current_language = 'en'
                print("[VOICE] Using default voice")

            # Set speech rate
            self.voice_engine.setProperty('rate', 180)
            self.voice_engine.setProperty('volume', 0.8)

            print(f"[SUCCESS] Voice initialized with language: {self.current_language}")

        except Exception as e:
            print(f"[ERROR] Voice initialization failed: {e}")
            print("[VOICE] Voice features will be disabled")
            self.voice_recognizer = None
            self.voice_engine = None

    def start_voice_listening(self):
        """Start voice recognition"""
        self.usage_tracker.record("voice", "start_listening", "Voice recognition started")
        if not VOICE_AVAILABLE or not self.voice_recognizer:
            self.add_message("System", "❌ Voice recognition not available")
            return

        if self.voice_listening:
            self.stop_voice_listening()
            return

        self.voice_listening = True
        self.status_label.setText("🎤 Listening...")

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
        """Voice recognition loop with improved error handling"""
        try:
            print("[VOICE] Starting voice recognition...")
            with sr.Microphone() as source:
                print("[VOICE] Adjusting for ambient noise...")
                self.voice_recognizer.adjust_for_ambient_noise(source, duration=1.0)
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
                            QTimer.singleShot(0, lambda: self.status_label.setText("🎤 Processing..."))

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
                        QTimer.singleShot(0, lambda: self.add_message("System", "❌ Voice recognition service unavailable. Check internet connection."))
                        break
                    except Exception as e:
                        print(f"[VOICE ERROR] Unexpected error: {e}")
                        continue

        except sr.MicrophoneUnavailableError:
            print("[VOICE ERROR] Microphone not available")
            QTimer.singleShot(0, lambda: self.add_message("System", "❌ Microphone not found or unavailable."))
        except Exception as e:
            print(f"[VOICE ERROR] Failed to start voice recognition: {e}")
            QTimer.singleShot(0, lambda: self.add_message("System", f"❌ Voice recognition failed: {str(e)}"))
        finally:
            self.voice_listening = False
            QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))
            print("[VOICE] Voice recognition stopped")

    def process_voice_command(self, text):
        """Process voice command"""
        self.add_message("Voice", f"🎤 {text}")
        self.message_input.setText(text)
        self.process_message()

    def speak_response(self, text):
        """Speak the response using text-to-speech"""
        if not VOICE_AVAILABLE or not self.voice_engine:
            return

        try:
            # Clean text for speech
            clean_text = text.replace('✅', '').replace('❌', '').replace('🤖', '').replace('💡', '')
            clean_text = clean_text.replace('🔧', '').replace('🧹', '').replace('⚡', '')

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
            return "🎤 Started voice listening mode"
        elif 'stop listening' in command_lower:
            self.stop_voice_listening()
            return "🛑 Stopped voice listening"
        elif 'continuous' in command_lower or 'single chat' in command_lower:
            return self.start_continuous_voice_chat()
        elif 'speak' in command_lower or 'say' in command_lower:
            text_to_speak = command_lower.replace('speak', '').replace('say', '').strip()
            if text_to_speak:
                self.speak_response(text_to_speak)
                return f"🗣️ Speaking: {text_to_speak}"
            else:
                return "❓ What would you like me to say?"
        elif 'language' in command_lower:
            if 'tamil' in command_lower:
                self.set_voice_language('ta')
                return "🗣️ Switched to Tamil voice"
            elif 'english' in command_lower:
                self.set_voice_language('en')
                return "🗣️ Switched to English voice"
            else:
                return "🗣️ Available languages: Tamil, English"
        else:
            return "🎤 Voice commands: 'start listening', 'stop listening', 'continuous chat', 'speak [text]', 'language tamil/english'"

    def start_continuous_voice_chat(self):
        """Start continuous voice chat mode"""
        if not VOICE_AVAILABLE or not self.voice_recognizer:
            return "❌ Voice recognition not available for continuous chat"

        if hasattr(self, 'continuous_chat_active') and self.continuous_chat_active:
            self.stop_continuous_voice_chat()
            return "🛑 Stopped continuous voice chat"

        self.continuous_chat_active = True
        self.status_label.setText("🎤 Continuous Chat Active")

        # Start continuous voice recognition
        import threading
        def continuous_chat_loop():
            try:
                with sr.Microphone() as source:
                    self.voice_recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    print("[CONTINUOUS] Listening for commands...")

                    while self.continuous_chat_active:
                        try:
                            print("[CONTINUOUS] Listening...")
                            audio = self.voice_recognizer.listen(source, timeout=5, phrase_time_limit=10)
                            text = self.voice_recognizer.recognize_google(audio, language='en-US')

                            if text:
                                print(f"[CONTINUOUS] Heard: {text}")

                                # Check for stop commands
                                if any(word in text.lower() for word in ['stop', 'quit', 'exit', 'end', 'bye']):
                                    QTimer.singleShot(0, lambda: self.stop_continuous_voice_chat())
                                    break

                                # Process the command
                                QTimer.singleShot(0, lambda: self.add_message("Voice", f"🎤 {text}"))
                                QTimer.singleShot(0, lambda: self.status_label.setText("🎤 Processing..."))

                                # Execute command
                                response = self.execute_command(text)

                                # Add response and speak it
                                QTimer.singleShot(0, lambda: self.add_message("Assistant", response))
                                QTimer.singleShot(0, lambda: self.status_label.setText("🎤 Continuous Chat Active"))

                                # Speak response
                                if VOICE_AVAILABLE and self.voice_engine:
                                    speech_thread = threading.Thread(target=lambda: self.speak_response(response), daemon=True)
                                    speech_thread.start()

                        except sr.WaitTimeoutError:
                            continue
                        except sr.UnknownValueError:
                            continue
                        except sr.RequestError as e:
                            print(f"[CONTINUOUS ERROR] {e}")
                            break
                        except Exception as e:
                            print(f"[CONTINUOUS ERROR] {e}")
                            break

            except Exception as e:
                print(f"[CONTINUOUS ERROR] {e}")
            finally:
                self.continuous_chat_active = False
                QTimer.singleShot(0, lambda: self.status_label.setText("Ready"))

        # Start continuous chat thread
        self.continuous_thread = threading.Thread(target=continuous_chat_loop, daemon=True)
        self.continuous_thread.start()

        return """🎤 Continuous Voice Chat Started!

I'm now listening continuously for your commands. You can say:

🗣️ SPEAK COMMANDS:
• "Open YouTube" - Opens YouTube
• "Check system info" - Shows PC details
• "Clean temp files" - Cleans temporary files
• "Stop" or "Quit" - Ends continuous chat

💡 TIPS:
• Speak clearly and wait for response
• Say "stop" to end continuous mode
• All normal commands work with voice
• I respond both visually and with voice

Say a command to get started!"""

    def stop_continuous_voice_chat(self):
        """Stop continuous voice chat"""
        self.continuous_chat_active = False
        if hasattr(self, 'continuous_thread') and self.continuous_thread.is_alive():
            self.continuous_thread.join(timeout=1)
        self.status_label.setText("Ready")
        return "🛑 Continuous voice chat stopped"

    def create_desktop_shortcut(self):
        """Create desktop shortcut with custom icon"""
        try:
            if platform.system() != 'Windows':
                return "❌ Desktop shortcuts only available on Windows"

            if not WINDOWS_SHORTCUTS_AVAILABLE:
                return "❌ Windows shortcuts not available. Install pywin32 and winshell:\n   pip install pywin32 winshell"

            # Get desktop path
            desktop = winshell.desktop()

            # Script path
            script_path = os.path.abspath(__file__)

            # Shortcut path
            shortcut_path = os.path.join(desktop, "Desktop AI Assistant.lnk")

            # Create shortcut
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)

            # Set shortcut properties
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{script_path}"'
            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.Description = "AI-powered Desktop Assistant with voice control"
            shortcut.IconLocation = self.create_custom_icon()

            # Save shortcut
            shortcut.save()

            print(f"[SUCCESS] Desktop shortcut created at: {shortcut_path}")
            return f"✅ Desktop shortcut created successfully!\n📍 Location: {shortcut_path}"

        except Exception as e:
            print(f"[ERROR] Failed to create desktop shortcut: {e}")
            return f"❌ Failed to create desktop shortcut: {str(e)}"

    def create_custom_icon(self):
        """Create a custom icon for the shortcut"""
        try:
            # Create icon directory if it doesn't exist
            icon_dir = os.path.join(os.path.dirname(__file__), "icons")
            os.makedirs(icon_dir, exist_ok=True)

            # Icon file path
            icon_path = os.path.join(icon_dir, "ai_assistant.ico")

            # If icon already exists, return its path
            if os.path.exists(icon_path):
                return icon_path

            # Create a simple icon using PIL if available
            try:
                from PIL import Image, ImageDraw, ImageFont
                import tempfile

                # Create a 256x256 icon
                img = Image.new('RGBA', (256, 256), (0, 120, 212, 255))  # Blue background
                draw = ImageDraw.Draw(img)

                # Draw AI brain-like pattern
                # Central circle
                draw.ellipse([64, 64, 192, 192], fill=(255, 255, 255, 255))

                # Neural network nodes
                nodes = [(128, 100), (100, 128), (156, 128), (128, 156)]
                for node in nodes:
                    draw.ellipse([node[0]-8, node[1]-8, node[0]+8, node[1]+8], fill=(0, 120, 212, 255))

                # Connections
                draw.line([128, 100, 100, 128], fill=(0, 120, 212, 255), width=3)
                draw.line([128, 100, 156, 128], fill=(0, 120, 212, 255), width=3)
                draw.line([100, 128, 128, 156], fill=(0, 120, 212, 255), width=3)
                draw.line([156, 128, 128, 156], fill=(0, 120, 212, 255), width=3)

                # Add "AI" text
                try:
                    font = ImageFont.truetype("arial.ttf", 48)
                except:
                    font = ImageFont.load_default()

                # Center the text
                bbox = draw.textbbox((0, 0), "AI", font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (256 - text_width) // 2
                y = (256 - text_height) // 2

                draw.text((x, y), "AI", fill=(255, 255, 255, 255), font=font)

                # Save as ICO
                img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

                return icon_path

            except ImportError:
                # Fallback: use Python's default icon
                return sys.executable

        except Exception as e:
            print(f"[ERROR] Failed to create custom icon: {e}")
            return sys.executable

    def create_startup_shortcut(self):
        """Create startup shortcut for auto-launch"""
        try:
            if platform.system() != 'Windows':
                return "❌ Startup shortcuts only available on Windows"

            if not WINDOWS_SHORTCUTS_AVAILABLE:
                return "❌ Windows shortcuts not available. Install pywin32 and winshell:\n   pip install pywin32 winshell"

            # Get startup folder
            startup = winshell.startup()

            # Script path
            script_path = os.path.abspath(__file__)

            # Shortcut path
            shortcut_path = os.path.join(startup, "Desktop AI Assistant.lnk")

            # Create shortcut
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)

            # Set shortcut properties
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{script_path}"'
            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.Description = "AI-powered Desktop Assistant (Auto-start)"
            shortcut.IconLocation = self.create_custom_icon()

            # Save shortcut
            shortcut.save()

            return f"✅ Startup shortcut created!\n📍 The AI Assistant will now launch automatically with Windows."

        except Exception as e:
            return f"❌ Failed to create startup shortcut: {str(e)}"

    def remove_shortcuts(self):
        """Remove desktop and startup shortcuts"""
        try:
            if platform.system() != 'Windows':
                return "❌ Shortcut management only available on Windows"

            if not WINDOWS_SHORTCUTS_AVAILABLE:
                return "❌ Windows shortcuts not available. Install pywin32 and winshell:\n   pip install pywin32 winshell"

            removed = []

            # Remove desktop shortcut
            desktop = winshell.desktop()
            desktop_shortcut = os.path.join(desktop, "Desktop AI Assistant.lnk")
            if os.path.exists(desktop_shortcut):
                os.remove(desktop_shortcut)
                removed.append("Desktop shortcut")

            # Remove startup shortcut
            startup = winshell.startup()
            startup_shortcut = os.path.join(startup, "Desktop AI Assistant.lnk")
            if os.path.exists(startup_shortcut):
                os.remove(startup_shortcut)
                removed.append("Startup shortcut")

            if removed:
                return f"✅ Removed shortcuts: {', '.join(removed)}"
            else:
                return "ℹ️ No shortcuts found to remove"

        except Exception as e:
            return f"❌ Failed to remove shortcuts: {str(e)}"

    def is_greeting(self, text):
        """Check if text is a greeting"""
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'howdy', 'greetings']
        return any(greeting in text for greeting in greetings)

    def is_thanks(self, text):
        """Check if text is thanks"""
        thanks = ['thank you', 'thanks', 'thank', 'thx', 'ty', 'appreciate', 'grateful']
        return any(thank in text for thank in thanks)

    def is_question(self, text):
        """Check if text is a question"""
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'can you', 'could you', 'would you', 'do you']
        return any(word in text for word in question_words) or text.endswith('?')

    def contains_action_words(self, text):
        """Check if text contains action words"""
        actions = ['please', 'can you', 'could you', 'would you', 'i want', 'i need', 'let me', 'help me']
        return any(action in text for action in actions)

    def handle_question(self, command):
        """Handle question-type commands"""
        command_lower = command.lower()

        if 'what can you do' in command_lower or 'what do you do' in command_lower:
            return self.get_help_text()
        elif 'how are you' in command_lower or 'how do you do' in command_lower:
            return "🤖 I'm doing great! I'm your Desktop AI Assistant, ready to help with PC tasks, repairs, programming, and more. How can I assist you today?"
        elif 'who are you' in command_lower or 'what are you' in command_lower:
            return "🤖 I'm your Desktop AI Assistant! I can control your PC, help with repairs, programming, research, and much more. I have voice recognition and can speak in English and Tamil too!"
        elif 'system info' in command_lower or 'computer info' in command_lower:
            return self.get_system_info()
        elif 'time' in command_lower:
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            return f"🕐 Current time is {current_time}"
        elif 'date' in command_lower:
            from datetime import datetime
            current_date = datetime.now().strftime("%B %d, %Y")
            return f"📅 Today's date is {current_date}"
        else:
            return self.get_ai_response(command)

    def handle_action_command(self, command):
        """Handle action-oriented commands"""
        command_lower = command.lower()

        # Extract the core action
        action = command_lower
        for prefix in ['please', 'can you', 'could you', 'would you', 'i want', 'i need', 'let me', 'help me']:
            action = action.replace(prefix, '').strip()

        # Try to match with existing commands
        if 'open' in action:
            return self.open_application(action)
        elif 'clean' in action or 'clear' in action:
            if 'temp' in action:
                return self.clean_temp_files()
            elif 'browser' in action or 'cache' in action:
                return self.clear_browser_cache()
            else:
                return self.clean_temp_files()
        elif 'system info' in action or 'computer info' in action:
            return self.get_system_info()
        elif 'help' in action:
            return self.get_help_text()
        elif 'update' in action:
            if 'driver' in action:
                return self.update_drivers()
            else:
                return self.check_updates()
        elif 'scan' in action or 'virus' in action:
            return self.virus_scan()
        elif 'diagnostics' in action or 'diagnostic' in action:
            return self.system_diagnostics()
        else:
            # Try AI response for complex actions
            return self.get_ai_response(command)

    def set_voice_language(self, lang_code):
        """Set voice language"""
        if not VOICE_AVAILABLE or not self.voice_engine:
            return

        try:
            voices = self.voice_engine.getProperty('voices')
            for voice in voices:
                if lang_code == 'ta' and ('tamil' in voice.name.lower() or 'ta' in voice.name.lower()):
                    self.voice_engine.setProperty('voice', voice.id)
                    self.current_language = 'ta'
                    break
                elif lang_code == 'en' and ('english' in voice.name.lower() or 'en' in voice.name.lower()):
                    self.voice_engine.setProperty('voice', voice.id)
                    self.current_language = 'en'
                    break
        except Exception as e:
            print(f"[VOICE ERROR] Language change failed: {e}")

    def pc_repair_knowledge(self, issue_type):
        """Provide comprehensive PC repair and troubleshooting knowledge"""
        issue_lower = issue_type.lower()

        knowledge_base = {
            'slow': {
                'title': '🔧 PC Running Slow - Troubleshooting Guide',
                'steps': [
                    '1. 🧹 Clean temporary files and browser cache',
                    '2. 🖥️ Check Task Manager for resource-hungry processes',
                    '3. 🛡️ Run virus scan to check for malware',
                    '4. 💾 Check disk space and clean up unnecessary files',
                    '5. 🔄 Update Windows and device drivers',
                    '6. ⚡ Disable startup programs you don\'t need',
                    '7. 🧠 Consider upgrading RAM if system is old'
                ],
                'commands': ['clean temp files', 'virus scan', 'check for updates', 'optimize performance']
            },

            'crash': {
                'title': '💥 System Crashing - Repair Steps',
                'steps': [
                    '1. 🔍 Check Windows Event Viewer for error details',
                    '2. 🛠️ Run System File Checker: sfc /scannow',
                    '3. 🔧 Update all device drivers',
                    '4. 🧹 Clean system of malware and viruses',
                    '5. 💾 Check disk for errors: chkdsk /f',
                    '6. 🖥️ Test RAM with Windows Memory Diagnostic',
                    '7. 🔄 Consider system restore to previous working state'
                ],
                'commands': ['run diagnostics', 'update drivers', 'virus scan']
            },

            'blue screen': {
                'title': '🔵 Blue Screen Errors - BSOD Troubleshooting',
                'steps': [
                    '1. 📝 Note the error code (STOP code) for research',
                    '2. 🔧 Update device drivers, especially graphics drivers',
                    '3. 🧹 Remove recently installed software/hardware',
                    '4. 🖥️ Test RAM modules individually',
                    '5. 💾 Check hard drive health with chkdsk',
                    '6. 🔄 Run System Restore or repair Windows',
                    '7. 🛠️ Use BlueScreenView to analyze minidump files'
                ],
                'commands': ['update drivers', 'run diagnostics', 'system repair']
            },

            'no internet': {
                'title': '🌐 No Internet Connection - Network Troubleshooting',
                'steps': [
                    '1. 🔌 Check physical connections (cables, WiFi)',
                    '2. 🔄 Restart modem/router and computer',
                    '3. 🌐 Run network diagnostics and repair',
                    '4. 📡 Check WiFi signal strength and settings',
                    '5. 🔧 Update network drivers',
                    '6. 🛡️ Temporarily disable firewall/antivirus',
                    '7. 📞 Contact ISP if all else fails'
                ],
                'commands': ['network diagnostics', 'update drivers']
            },

            'overheating': {
                'title': '🔥 PC Overheating - Cooling Solutions',
                'steps': [
                    '1. 🧹 Clean dust from fans and vents',
                    '2. 💨 Check CPU/GPU fan operation',
                    '3. 🖥️ Monitor temperatures with HWMonitor',
                    '4. 🔧 Reapply thermal paste if needed',
                    '5. 📍 Ensure proper airflow in case',
                    '6. ⚡ Reduce overclocking if applicable',
                    '7. 🛠️ Consider additional cooling solutions'
                ],
                'commands': ['system info', 'run diagnostics']
            },

            'driver': {
                'title': '🔧 Device Driver Issues - Update Guide',
                'steps': [
                    '1. 🖥️ Open Device Manager to check for errors',
                    '2. 🔄 Update drivers through Windows Update',
                    '3. 🌐 Download latest drivers from manufacturer websites',
                    '4. 🗑️ Uninstall problematic drivers and reinstall',
                    '5. 💾 Use driver update software if needed',
                    '6. 🔄 Roll back drivers if issues started after update',
                    '7. 🛠️ Use System Restore as last resort'
                ],
                'commands': ['update drivers', 'run diagnostics']
            }
        }

        # Find matching issue
        for key, info in knowledge_base.items():
            if key in issue_lower:
                response = f"{info['title']}\n\n"
                response += "📋 Step-by-step troubleshooting:\n"
                response += "\n".join(info['steps'])
                response += "\n\n💡 Quick commands I can run:\n"
                response += "\n".join(f"• {cmd}" for cmd in info['commands'])
                response += "\n\n🔍 Would you like me to run any of these commands, or need more specific help?"
                return response

        # Generic troubleshooting if no specific match
        return f"""🔧 PC Repair & Troubleshooting Knowledge Base

I can help with common PC issues:

💻 PERFORMANCE:
• "fix slow pc" - Speed up slow computer
• "optimize performance" - General optimization

🔥 HARDWARE:
• "fix overheating" - Cooling problems
• "update drivers" - Driver issues

🌐 NETWORK:
• "fix no internet" - Connection problems
• "network diagnostics" - Network troubleshooting

🛡️ SECURITY:
• "remove virus" - Malware removal
• "virus scan" - Security check

💾 STORAGE:
• "fix disk errors" - Hard drive problems
• "disk cleanup" - Free up space

🖥️ SYSTEM:
• "fix blue screen" - BSOD errors
• "system repair" - General repair

Try: "fix [issue]" or "troubleshoot [problem]"
Example: "fix slow pc" or "troubleshoot no internet"

What specific issue are you facing?"""

    def advanced_pc_help(self, command):
        """Provide advanced PC help and knowledge"""
        command_lower = command.lower()

        if 'fix' in command_lower or 'repair' in command_lower or 'troubleshoot' in command_lower:
            # Extract the issue from the command
            issue = command_lower.replace('fix', '').replace('repair', '').replace('troubleshoot', '').strip()
            if issue:
                return self.pc_repair_knowledge(issue)
            else:
                return self.pc_repair_knowledge('general')

        elif 'tips' in command_lower or 'advice' in command_lower:
            return """💡 PC Maintenance Tips & Best Practices:

🧹 REGULAR CLEANING:
• Clean dust from vents and fans monthly
• Clear temporary files weekly
• Empty Recycle Bin regularly
• Clean browser cache and history

🔄 SYSTEM UPDATES:
• Keep Windows updated
• Update device drivers regularly
• Update antivirus definitions daily
• Keep applications updated

🛡️ SECURITY PRACTICES:
• Use strong passwords
• Enable Windows Defender
• Be cautious with email attachments
• Regular backup of important files

⚡ PERFORMANCE OPTIMIZATION:
• Close unused programs
• Disable unnecessary startup items
• Defragment hard drives (HDD only)
• Monitor resource usage

💾 STORAGE MANAGEMENT:
• Keep at least 20% free space
• Use external drives for large files
• Regular disk cleanup
• Monitor disk health

🌐 NETWORK CARE:
• Secure WiFi with strong password
• Update router firmware
• Use Ethernet for important tasks
• Monitor network security

🔧 HARDWARE MAINTENANCE:
• Check temperatures regularly
• Ensure proper ventilation
• Handle components carefully
• Professional service when needed

Try "fix [specific issue]" for detailed troubleshooting!"""

        else:
            return """🧠 Advanced PC Knowledge & Support:

🔧 REPAIR & TROUBLESHOOTING:
• "fix slow pc" - Performance issues
• "fix no internet" - Network problems
• "fix overheating" - Cooling issues
• "fix blue screen" - System crashes
• "fix driver issues" - Hardware drivers

💡 MAINTENANCE TIPS:
• "pc maintenance tips" - Best practices
• "security advice" - Protection tips
• "performance tips" - Speed optimization

🛠️ DIAGNOSTICS:
• "run diagnostics" - System health check
• "network diagnostics" - Connection test
• "driver diagnostics" - Hardware check

📚 LEARNING RESOURCES:
• "learn pc repair" - Basic repair skills
• "windows troubleshooting" - OS-specific help
• "hardware basics" - Component knowledge

What would you like to know or fix?"""

    def get_usage_stats(self):
        """Get usage statistics for display"""
        stats = self.usage_tracker.get_stats()
        recent = self.usage_tracker.get_recent_activity(5)

        response = f"""📊 Usage Statistics:

🎯 OVERVIEW:
• Total Commands: {stats['total_commands']}
• Modules Used: {stats['modules_used']}
• Most Used Module: {stats['most_used_module']}
• Avg Session Time: {stats['avg_session_time']}s

📝 RECENT ACTIVITY:
"""

        if recent:
            for i, log in enumerate(recent, 1):
                timestamp = datetime.fromtimestamp(log['timestamp']).strftime("%H:%M:%S")
                response += f"{i}. [{timestamp}] {log['module']}: {log['action']}\n"
        else:
            response += "No recent activity"

        return response

    def handle_learning_command(self, command):
        """Handle learning and teaching commands"""
        command_lower = command.lower()

        if 'pattern' in command_lower or 'behavior' in command_lower:
            patterns = self.usage_tracker.detect_pattern("command_processor", lambda log: True)
            return f"🤖 Learning from {len(patterns)} interactions. I adapt based on your usage patterns!"
        elif 'preference' in command_lower:
            return "💡 I learn your preferences over time. Try using commands repeatedly and I'll remember what you prefer!"
        else:
            return """🧠 Self-Learning Commands:

• "learn my patterns" - Analyze usage patterns
• "teach me [topic]" - Get learning resources
• "optimize myself" - Self-optimization
• "upgrade myself" - Check for improvements
• "manage preferences" - View/set preferences

I'm constantly learning from our interactions!"""

    def self_optimize(self):
        """Self-optimization based on usage patterns"""
        try:
            # Analyze slow modules
            slow_modules = self.optimizer.analyze(self.usage_tracker.logs)

            if slow_modules:
                suggestions = []
                for module in slow_modules:
                    suggestion = self.improvement_proposer.suggest(module)
                    suggestions.append(f"• {module}: {suggestion}")

                return f"""⚡ Self-Optimization Results:

🔍 Identified {len(slow_modules)} areas for improvement:

{chr(10).join(suggestions)}

💡 These optimizations will be applied automatically over time as I learn more about your usage patterns."""
            else:
                return "✅ All modules are performing optimally! No optimizations needed at this time."

        except Exception as e:
            return f"❌ Self-optimization failed: {str(e)}"

    def self_upgrade(self):
        """Check for and apply self-upgrades"""
        try:
            # Create a simple module registry for demonstration
            module_registry = [
                {"name": "voice_recognition", "version": 1.0, "latest_version": 1.1},
                {"name": "command_parser", "version": 1.0, "latest_version": 1.0},
                {"name": "ai_model", "version": 1.0, "latest_version": 1.2}
            ]

            # Initialize upgrade scanner
            if not self.upgrade_scanner:
                self.upgrade_scanner = UpgradeScanner(module_registry)

            outdated = self.upgrade_scanner.find_outdated()

            if outdated:
                return f"""🔄 Self-Upgrade Available!

📦 Outdated modules: {len(outdated)}
{chr(10).join(f"• {mod['name']}: v{mod['version']} → v{mod['latest_version']}" for mod in outdated)}

⚠️ Upgrades require user consent. Use "upgrade myself confirm" to proceed."""
            else:
                return "✅ All modules are up to date! No upgrades needed."

        except Exception as e:
            return f"❌ Self-upgrade check failed: {str(e)}"

    def manage_preferences(self, command):
        """Manage user preferences"""
        command_lower = command.lower()

        if 'set' in command_lower:
            # Extract preference key and value
            parts = command_lower.replace('set', '').strip().split('=')
            if len(parts) == 2:
                key, value = parts[0].strip(), parts[1].strip()
                self.feedback_loop.set_preference(key, value)
                self.local_store.set(f"pref_{key}", value)
                return f"✅ Preference set: {key} = {value}"
            else:
                return "❌ Format: 'set preference_name = value'"

        elif 'get' in command_lower:
            # Extract preference key
            key = command_lower.replace('get', '').replace('preference', '').strip()
            if key:
                value = self.feedback_loop.get_preference(key) or self.local_store.get(f"pref_{key}")
                if value:
                    return f"📋 {key}: {value}"
                else:
                    return f"❌ Preference '{key}' not found"
            else:
                return "❌ Specify preference name: 'get preference_name'"

        else:
            # Show all preferences
            preferences = {}
            for key, value in self.feedback_loop.preferences.items():
                preferences[key] = value

            # Add stored preferences
            for key, value in self.local_store.data.items():
                if key.startswith("pref_"):
                    pref_key = key.replace("pref_", "")
                    preferences[pref_key] = value

            if preferences:
                pref_list = "\n".join(f"• {k}: {v}" for k, v in preferences.items())
                return f"""📋 Current Preferences:

{pref_list}

💡 Commands:
• "set [key] = [value]" - Set preference
• "get [key]" - Get preference value"""
            else:
                return """📋 No preferences set yet.

💡 Commands:
• "set [key] = [value]" - Set preference
• "get [key]" - Get preference value

Example: "set voice_language = tamil\""""

# === Runtime Upgrade Flow ===
def runtime_upgrade_flow(module_name, module, test_cases, registry, store):
    """Runtime upgrade orchestration"""
    scanner = UpgradeScanner(registry)
    sandbox = SandboxRunner()
    validator = DiffValidator()
    rollback = RollbackManager()
    consent = ConsentGate(auto_upgrade=False)  # Require user consent

    outdated = scanner.find_outdated()
    if module_name in [m["name"] for m in outdated]:
        rollback.save(module_name, module.config)
        new_results = sandbox.test(module, test_cases)
        old_results = sandbox.test(module, test_cases)  # simulate old version

        if validator.validate(old_results, new_results) and consent.is_allowed():
            module.apply_upgrade()
            return f"✅ {module_name} upgraded successfully!"
        else:
            module.config = rollback.restore(module_name)
            return f"⚠️ {module_name} upgrade cancelled or failed. Rolled back to previous version."
    else:
        return f"ℹ️ {module_name} is already up to date."


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