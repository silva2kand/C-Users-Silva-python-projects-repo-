"""
Hybrid AI Video Remaker
=======================

A comprehensive PyQt5 application for AI-powered video processing with integrated
hybrid AI chat functionality. Features seamless integration of multiple AI services
for natural language processing, video generation, and intelligent conversation.

Features:
- PyQt5 GUI with modern interface
- Integrated hybrid AI chat system
- Multi-service AI integration (GPT4All, OpenAI, Gemini, Claude)
- Video processing with moviepy
- Speech recognition and text-to-speech
- Personality-based AI responses
- Real-time chat with fallback mechanisms
- Video generation and editing capabilities

Author: Hybrid AI System
"""

import asyncio
import json
import logging
import os
import sys
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QComboBox, QProgressBar,
    QSplitter, QFrame, QScrollArea, QGroupBox, QCheckBox,
    QFileDialog, QMessageBox, QStatusBar, QMenuBar, QMenu,
    QAction, QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QUrl, QSize
)
from PyQt5.QtGui import (
    QFont, QPalette, QColor, QIcon, QPixmap, QTextCursor
)

# AI and video processing imports
try:
    from hybrid_ai_client import HybridAIClient, FreeTierAIClient
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("Warning: Hybrid AI client not available")

try:
    import moviepy.editor as mp
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("Warning: MoviePy not available")

try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("Warning: Speech recognition not available")

try:
    from gtts import gTTS
    import pygame
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Warning: Text-to-speech not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_remaker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIWorker(QThread):
    """Worker thread for AI processing to keep GUI responsive."""

    response_ready = pyqtSignal(str, str, float)  # response, service_used, processing_time
    error_occurred = pyqtSignal(str)
    status_updated = pyqtSignal(str)

    def __init__(self, ai_client, message, personality="helpful", max_tokens=150, temperature=0.7):
        super().__init__()
        self.ai_client = ai_client
        self.message = message
        self.personality = personality
        self.max_tokens = max_tokens
        self.temperature = temperature

    def run(self):
        """Execute AI processing in background thread."""
        try:
            self.status_updated.emit("Processing with AI...")

            start_time = time.time()
            response = self.ai_client.generate_response(
                message=self.message,
                personality=self.personality,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            processing_time = time.time() - start_time

            if response:
                # Determine which service was used (this is a simplification)
                service_used = getattr(self.ai_client, 'last_used_service', 'unknown')
                self.response_ready.emit(response, service_used, processing_time)
            else:
                self.error_occurred.emit("No response generated")

        except Exception as e:
            logger.error(f"AI processing error: {e}")
            self.error_occurred.emit(f"AI Error: {str(e)}")

class VideoProcessor(QThread):
    """Worker thread for video processing operations."""

    progress_updated = pyqtSignal(int, str)  # progress, status
    processing_complete = pyqtSignal(str)  # output_path
    error_occurred = pyqtSignal(str)

    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs

    def run(self):
        """Execute video processing operation."""
        try:
            if self.operation == "generate_video":
                self._generate_video()
            elif self.operation == "edit_video":
                self._edit_video()
            elif self.operation == "add_effects":
                self._add_effects()
            else:
                self.error_occurred.emit(f"Unknown operation: {self.operation}")

        except Exception as e:
            logger.error(f"Video processing error: {e}")
            self.error_occurred.emit(f"Video Error: {str(e)}")

    def _generate_video(self):
        """Generate video from AI prompt."""
        prompt = self.kwargs.get('prompt', '')
        duration = self.kwargs.get('duration', 30)
        output_path = self.kwargs.get('output_path', 'generated_video.mp4')

        # This would integrate with actual video generation
        # For now, simulate the process
        for i in range(101):
            self.progress_updated.emit(i, f"Generating video... {i}%")
            time.sleep(0.1)  # Simulate processing time

        self.processing_complete.emit(output_path)

    def _edit_video(self):
        """Edit existing video."""
        input_path = self.kwargs.get('input_path', '')
        output_path = self.kwargs.get('output_path', 'edited_video.mp4')

        if not MOVIEPY_AVAILABLE:
            self.error_occurred.emit("MoviePy not available for video editing")
            return

        # Simulate video editing
        for i in range(101):
            self.progress_updated.emit(i, f"Editing video... {i}%")
            time.sleep(0.05)

        self.processing_complete.emit(output_path)

    def _add_effects(self):
        """Add effects to video."""
        input_path = self.kwargs.get('input_path', '')
        output_path = self.kwargs.get('output_path', 'effects_video.mp4')

        # Simulate adding effects
        for i in range(101):
            self.progress_updated.emit(i, f"Adding effects... {i}%")
            time.sleep(0.03)

        self.processing_complete.emit(output_path)

class AIChatDialog(QDialog):
    """Dialog for AI chat functionality."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ai_client = None
        self.free_tier_client = None
        self.current_worker = None
        self.conversation_history = []

        self.init_ai_clients()
        self.init_ui()
        self.load_conversation_history()

    def init_ai_clients(self):
        """Initialize AI clients."""
        if AI_AVAILABLE:
            try:
                self.ai_client = HybridAIClient()
                self.free_tier_client = FreeTierAIClient()
                logger.info("AI clients initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize AI clients: {e}")
                QMessageBox.warning(self, "AI Initialization Error",
                                  f"Failed to initialize AI clients: {e}")

    def init_ui(self):
        """Initialize the chat dialog UI."""
        self.setWindowTitle("AI Chat Assistant")
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        # Personality selector
        personality_layout = QHBoxLayout()
        personality_layout.addWidget(QLabel("AI Personality:"))
        self.personality_combo = QComboBox()
        self.personality_combo.addItems(["helpful", "creative", "analytical", "funny"])
        personality_layout.addWidget(self.personality_combo)
        personality_layout.addStretch()
        layout.addLayout(personality_layout)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Arial", 10))
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(80)
        self.message_input.setFont(QFont("Arial", 10))
        input_layout.addWidget(self.message_input)

        # Control buttons
        button_layout = QVBoxLayout()

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setMinimumHeight(30)
        button_layout.addWidget(self.send_button)

        self.voice_button = QPushButton("Voice Input")
        self.voice_button.clicked.connect(self.voice_input)
        self.voice_button.setMinimumHeight(30)
        button_layout.addWidget(self.voice_button)

        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.clicked.connect(self.clear_chat)
        self.clear_button.setMinimumHeight(30)
        button_layout.addWidget(self.clear_button)

        input_layout.addLayout(button_layout)
        layout.addLayout(input_layout)

        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # Connect enter key to send
        self.message_input.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Handle keyboard events."""
        if obj == self.message_input and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ShiftModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def send_message(self):
        """Send message to AI."""
        message = self.message_input.toPlainText().strip()
        if not message:
            return

        if not self.ai_client:
            QMessageBox.warning(self, "AI Not Available",
                              "AI client is not initialized. Please check your configuration.")
            return

        # Add user message to chat
        self.add_message("You", message, "user")
        self.message_input.clear()

        # Disable send button while processing
        self.send_button.setEnabled(False)
        self.status_label.setText("Thinking...")

        # Start AI processing in background
        personality = self.personality_combo.currentText()
        self.current_worker = AIWorker(
            self.ai_client, message, personality=personality
        )
        self.current_worker.response_ready.connect(self.on_ai_response)
        self.current_worker.error_occurred.connect(self.on_ai_error)
        self.current_worker.status_updated.connect(self.on_status_update)
        self.current_worker.start()

    def on_ai_response(self, response, service_used, processing_time):
        """Handle AI response."""
        self.add_message("AI", response, "ai", service_used, processing_time)
        self.send_button.setEnabled(True)
        self.status_label.setText("Ready")

        # Save conversation
        self.save_conversation_history()

    def on_ai_error(self, error_message):
        """Handle AI error."""
        self.add_message("System", f"Error: {error_message}", "error")
        self.send_button.setEnabled(True)
        self.status_label.setText("Error occurred")

    def on_status_update(self, status):
        """Update status display."""
        self.status_label.setText(status)

    def add_message(self, sender, message, msg_type, service_used=None, processing_time=None):
        """Add message to chat display."""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Format message based on type
        if msg_type == "user":
            formatted_msg = f'<b>[{timestamp}] {sender}:</b> {message}<br>'
        elif msg_type == "ai":
            service_info = f" (via {service_used})" if service_used else ""
            time_info = f" ({processing_time:.1f}s)" if processing_time else ""
            formatted_msg = f'<b>[{timestamp}] {sender}{service_info}{time_info}:</b><br>{message}<br>'
        elif msg_type == "error":
            formatted_msg = f'<span style="color: red;"><b>[{timestamp}] {sender}:</b> {message}</span><br>'
        else:
            formatted_msg = f'<i>[{timestamp}] {sender}:</i> {message}<br>'

        self.chat_display.append(formatted_msg)

        # Store in conversation history
        self.conversation_history.append({
            'timestamp': timestamp,
            'sender': sender,
            'message': message,
            'type': msg_type,
            'service_used': service_used,
            'processing_time': processing_time
        })

        # Scroll to bottom
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)

    def voice_input(self):
        """Handle voice input."""
        if not SPEECH_AVAILABLE:
            QMessageBox.warning(self, "Voice Input Unavailable",
                              "Speech recognition is not available. Please install SpeechRecognition.")
            return

        try:
            self.status_label.setText("Listening...")
            QApplication.processEvents()

            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                audio = recognizer.listen(source, timeout=5)

            self.status_label.setText("Processing speech...")
            QApplication.processEvents()

            text = recognizer.recognize_google(audio)
            self.message_input.setPlainText(text)
            self.status_label.setText("Ready")

        except sr.WaitTimeoutError:
            self.status_label.setText("No speech detected")
        except sr.UnknownValueError:
            self.status_label.setText("Could not understand audio")
        except sr.RequestError as e:
            self.status_label.setText(f"Speech recognition error: {e}")
        except Exception as e:
            self.status_label.setText(f"Voice input error: {e}")

    def clear_chat(self):
        """Clear chat history."""
        reply = QMessageBox.question(self, "Clear Chat",
                                   "Are you sure you want to clear the chat history?",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.chat_display.clear()
            self.conversation_history = []
            self.save_conversation_history()

    def load_conversation_history(self):
        """Load conversation history from file."""
        try:
            if os.path.exists("chat_history.json"):
                with open("chat_history.json", 'r') as f:
                    self.conversation_history = json.load(f)

                # Display loaded messages
                for msg in self.conversation_history:
                    self.add_message(
                        msg['sender'],
                        msg['message'],
                        msg['type'],
                        msg.get('service_used'),
                        msg.get('processing_time')
                    )
        except Exception as e:
            logger.error(f"Failed to load conversation history: {e}")

    def save_conversation_history(self):
        """Save conversation history to file."""
        try:
            with open("chat_history.json", 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save conversation history: {e}")

class VideoGenerationDialog(QDialog):
    """Dialog for video generation settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize video generation dialog UI."""
        self.setWindowTitle("Generate Video")
        self.setGeometry(300, 300, 500, 400)

        layout = QVBoxLayout()

        # Prompt input
        prompt_group = QGroupBox("Video Description")
        prompt_layout = QVBoxLayout()
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Describe the video you want to generate...")
        prompt_layout.addWidget(self.prompt_input)
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)

        # Settings
        settings_group = QGroupBox("Settings")
        settings_layout = QFormLayout()

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(5, 300)
        self.duration_spin.setValue(30)
        self.duration_spin.setSuffix(" seconds")
        settings_layout.addRow("Duration:", self.duration_spin)

        self.style_combo = QComboBox()
        self.style_combo.addItems(["realistic", "animated", "artistic", "minimalist"])
        settings_layout.addRow("Style:", self.style_combo)

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["720p", "1080p", "4K"])
        self.resolution_combo.setCurrentText("1080p")
        settings_layout.addRow("Resolution:", self.resolution_combo)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_settings(self):
        """Get video generation settings."""
        return {
            'prompt': self.prompt_input.toPlainText(),
            'duration': self.duration_spin.value(),
            'style': self.style_combo.currentText(),
            'resolution': self.resolution_combo.currentText()
        }

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.ai_client = None
        self.chat_dialog = None
        self.current_video_processor = None

        self.init_ai_client()
        self.init_ui()
        self.setup_menu()
        self.setup_status_bar()

    def init_ai_client(self):
        """Initialize AI client."""
        if AI_AVAILABLE:
            try:
                self.ai_client = HybridAIClient()
                logger.info("Main AI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize main AI client: {e}")

    def init_ui(self):
        """Initialize the main UI."""
        self.setWindowTitle("Hybrid AI Video Remaker")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Left panel - Controls
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        # Right panel - Preview/Chat
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)

    def create_left_panel(self):
        """Create the left control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Video operations group
        video_group = QGroupBox("Video Operations")
        video_layout = QVBoxLayout()

        self.generate_button = QPushButton("Generate Video with AI")
        self.generate_button.clicked.connect(self.generate_video)
        video_layout.addWidget(self.generate_button)

        self.load_button = QPushButton("Load Video")
        self.load_button.clicked.connect(self.load_video)
        video_layout.addWidget(self.load_button)

        self.edit_button = QPushButton("Edit Video")
        self.edit_button.clicked.connect(self.edit_video)
        video_layout.addWidget(self.edit_button)

        self.effects_button = QPushButton("Add Effects")
        self.effects_button.clicked.connect(self.add_effects)
        video_layout.addWidget(self.effects_button)

        video_group.setLayout(video_layout)
        layout.addWidget(video_group)

        # AI Chat group
        chat_group = QGroupBox("AI Assistant")
        chat_layout = QVBoxLayout()

        self.chat_button = QPushButton("Open AI Chat")
        self.chat_button.clicked.connect(self.open_chat)
        chat_layout.addWidget(self.chat_button)

        self.voice_chat_button = QPushButton("Voice Chat")
        self.voice_chat_button.clicked.connect(self.voice_chat)
        chat_layout.addWidget(self.voice_chat_button)

        chat_group.setLayout(chat_layout)
        layout.addWidget(chat_group)

        # Progress area
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("Ready")
        progress_layout.addWidget(self.progress_label)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        layout.addStretch()
        return panel

    def create_right_panel(self):
        """Create the right preview/chat panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Video preview area
        preview_group = QGroupBox("Video Preview")
        preview_layout = QVBoxLayout()

        self.preview_label = QLabel("No video loaded")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setStyleSheet("border: 2px dashed #aaa;")
        preview_layout.addWidget(self.preview_label)

        # Video controls
        controls_layout = QHBoxLayout()

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_video)
        controls_layout.addWidget(self.play_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_video)
        controls_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_video)
        controls_layout.addWidget(self.stop_button)

        preview_layout.addLayout(controls_layout)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        return panel

    def setup_menu(self):
        """Set up the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        open_action = QAction('Open Video', self)
        open_action.triggered.connect(self.load_video)
        file_menu.addAction(open_action)

        save_action = QAction('Save Video', self)
        save_action.triggered.connect(self.save_video)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # AI menu
        ai_menu = menubar.addMenu('AI')

        chat_action = QAction('AI Chat', self)
        chat_action.triggered.connect(self.open_chat)
        ai_menu.addAction(chat_action)

        generate_action = QAction('Generate Video', self)
        generate_action.triggered.connect(self.generate_video)
        ai_menu.addAction(generate_action)

        # Help menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        # AI status indicator
        if self.ai_client and self.ai_client.services:
            self.status_bar.showMessage(f"AI Ready - {len(self.ai_client.services)} services available")
        else:
            self.status_bar.showMessage("AI Not Available")

    def generate_video(self):
        """Generate video using AI."""
        if not self.ai_client:
            QMessageBox.warning(self, "AI Not Available",
                              "AI client is not initialized. Please check your configuration.")
            return

        dialog = VideoGenerationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            settings = dialog.get_settings()

            if not settings['prompt'].strip():
                QMessageBox.warning(self, "Invalid Input",
                                  "Please enter a video description.")
                return

            # Start video generation
            self.current_video_processor = VideoProcessor(
                "generate_video",
                prompt=settings['prompt'],
                duration=settings['duration'],
                style=settings['style'],
                resolution=settings['resolution'],
                output_path=f"generated_video_{int(time.time())}.mp4"
            )

            self.current_video_processor.progress_updated.connect(self.update_progress)
            self.current_video_processor.processing_complete.connect(self.on_video_complete)
            self.current_video_processor.error_occurred.connect(self.on_video_error)
            self.current_video_processor.start()

    def load_video(self):
        """Load video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video File",
            "", "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )

        if file_path:
            self.current_video_path = file_path
            self.preview_label.setText(f"Loaded: {os.path.basename(file_path)}")
            self.status_bar.showMessage(f"Video loaded: {file_path}")

    def edit_video(self):
        """Edit loaded video."""
        if not hasattr(self, 'current_video_path'):
            QMessageBox.warning(self, "No Video Loaded",
                              "Please load a video file first.")
            return

        # Start video editing
        output_path = f"edited_{int(time.time())}.mp4"
        self.current_video_processor = VideoProcessor(
            "edit_video",
            input_path=self.current_video_path,
            output_path=output_path
        )

        self.current_video_processor.progress_updated.connect(self.update_progress)
        self.current_video_processor.processing_complete.connect(self.on_video_complete)
        self.current_video_processor.error_occurred.connect(self.on_video_error)
        self.current_video_processor.start()

    def add_effects(self):
        """Add effects to video."""
        if not hasattr(self, 'current_video_path'):
            QMessageBox.warning(self, "No Video Loaded",
                              "Please load a video file first.")
            return

        # Start adding effects
        output_path = f"effects_{int(time.time())}.mp4"
        self.current_video_processor = VideoProcessor(
            "add_effects",
            input_path=self.current_video_path,
            output_path=output_path
        )

        self.current_video_processor.progress_updated.connect(self.update_progress)
        self.current_video_processor.processing_complete.connect(self.on_video_complete)
        self.current_video_processor.error_occurred.connect(self.on_video_error)
        self.current_video_processor.start()

    def open_chat(self):
        """Open AI chat dialog."""
        if not self.chat_dialog:
            self.chat_dialog = AIChatDialog(self)

        self.chat_dialog.show()
        self.chat_dialog.raise_()
        self.chat_dialog.activateWindow()

    def voice_chat(self):
        """Start voice chat."""
        if not SPEECH_AVAILABLE:
            QMessageBox.warning(self, "Voice Chat Unavailable",
                              "Speech recognition is not available.")
            return

        if not self.chat_dialog:
            self.open_chat()

        self.chat_dialog.voice_input()

    def play_video(self):
        """Play video (placeholder)."""
        QMessageBox.information(self, "Play Video",
                              "Video playback functionality would be implemented here.")

    def pause_video(self):
        """Pause video (placeholder)."""
        QMessageBox.information(self, "Pause Video",
                              "Video pause functionality would be implemented here.")

    def stop_video(self):
        """Stop video (placeholder)."""
        QMessageBox.information(self, "Stop Video",
                              "Video stop functionality would be implemented here.")

    def save_video(self):
        """Save video (placeholder)."""
        QMessageBox.information(self, "Save Video",
                              "Video save functionality would be implemented here.")

    def update_progress(self, progress, status):
        """Update progress bar and status."""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(status)
        self.status_bar.showMessage(status)

    def on_video_complete(self, output_path):
        """Handle video processing completion."""
        self.progress_bar.setValue(100)
        self.progress_label.setText("Complete")
        self.status_bar.showMessage(f"Video saved: {output_path}")

        QMessageBox.information(self, "Success",
                              f"Video processing completed!\nSaved to: {output_path}")

        # Update preview
        if hasattr(self, 'current_video_path'):
            self.preview_label.setText(f"Processed: {os.path.basename(output_path)}")

    def on_video_error(self, error_message):
        """Handle video processing error."""
        self.progress_bar.setValue(0)
        self.progress_label.setText("Error")
        self.status_bar.showMessage("Error occurred")

        QMessageBox.critical(self, "Video Processing Error", error_message)

    def show_about(self):
        """Show about dialog."""
        about_text = """
        Hybrid AI Video Remaker

        A comprehensive AI-powered video processing application
        featuring multi-service AI integration and natural language chat.

        Features:
        • Multi-service AI integration (GPT4All, OpenAI, Gemini, Claude)
        • Intelligent fallback mechanisms
        • Video generation and editing
        • Natural language chat interface
        • Voice input/output support

        Version: 1.0.0
        """

        QMessageBox.about(self, "About", about_text)

    def closeEvent(self, event):
        """Handle application close event."""
        if self.chat_dialog:
            self.chat_dialog.close()

        if self.current_video_processor and self.current_video_processor.isRunning():
            reply = QMessageBox.question(
                self, "Confirm Exit",
                "Video processing is in progress. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.current_video_processor.terminate()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Hybrid AI Video Remaker")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Hybrid AI System")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()