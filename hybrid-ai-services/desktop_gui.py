import sys
import requests
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QPushButton, QLabel,
                             QFileDialog, QProgressBar, QSplitter, QGroupBox,
                             QComboBox, QSpinBox, QCheckBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPalette, QColor
import os

class ChatWorker(QThread):
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            response = requests.post(
                "http://localhost:8000/chat",
                json={"prompt": self.prompt},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.response_received.emit(data.get("response", "No response"))
            else:
                self.error_occurred.emit(f"HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"Connection error: {str(e)}")

class VideoRemakerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.chat_history = []

    def init_ui(self):
        self.setWindowTitle("🎬 Hybrid AI Video Remaker")
        self.setGeometry(100, 100, 1000, 700)

        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 1ex;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #666;
                border-radius: 5px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
            QLabel {
                color: #ffffff;
            }
            QComboBox {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 5px;
            }
            QSpinBox {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666;
                border-radius: 3px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel - Chat Interface
        chat_panel = self.create_chat_panel()
        splitter.addWidget(chat_panel)

        # Right panel - Video Tools
        video_panel = self.create_video_panel()
        splitter.addWidget(video_panel)

        # Set splitter proportions
        splitter.setSizes([400, 600])

    def create_chat_panel(self):
        group = QGroupBox("🤖 AI Chat Assistant")
        layout = QVBoxLayout(group)

        # Chat history
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlainText("🎬 Welcome to Hybrid AI Video Remaker!\n"
                                     "💡 I'm your AI assistant for video processing.\n"
                                     "📝 Ask me anything about video editing, AI, or Docker!\n\n")
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(60)
        self.chat_input.setPlaceholderText("Type your message here...")
        input_layout.addWidget(self.chat_input)

        send_button = QPushButton("📤 Send")
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)

        layout.addLayout(input_layout)

        # Quick action buttons
        quick_layout = QHBoxLayout()
        quick_buttons = [
            ("💡 Help", "What can you help me with?"),
            ("🎬 Video", "Tell me about video processing"),
            ("🐳 Docker", "Tell me about Docker"),
            ("⚡ Status", "How are you doing?")
        ]

        for text, prompt in quick_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, p=prompt: self.quick_message(p))
            quick_layout.addWidget(btn)

        layout.addLayout(quick_layout)
        return group

    def create_video_panel(self):
        group = QGroupBox("🎬 Video Processing Tools")
        layout = QVBoxLayout(group)

        # File selection
        file_layout = QHBoxLayout()
        self.file_path = QLabel("No file selected")
        self.file_path.setStyleSheet("border: 1px solid #666; padding: 5px; border-radius: 3px;")
        file_layout.addWidget(self.file_path)

        select_file_btn = QPushButton("📁 Select Video")
        select_file_btn.clicked.connect(self.select_video_file)
        file_layout.addWidget(select_file_btn)
        layout.addLayout(file_layout)

        # Processing options
        options_group = QGroupBox("Processing Options")
        options_layout = QVBoxLayout(options_group)

        # Video format conversion
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Convert to:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "AVI", "MOV", "WMV", "FLV"])
        format_layout.addWidget(self.format_combo)
        options_layout.addLayout(format_layout)

        # Quality settings
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low (480p)", "Medium (720p)", "High (1080p)", "Ultra (4K)"])
        quality_layout.addWidget(self.quality_combo)
        options_layout.addLayout(quality_layout)

        # Effects
        effects_layout = QVBoxLayout()
        effects_layout.addWidget(QLabel("Effects:"))
        self.effect_checkboxes = []
        effects = ["Brightness", "Contrast", "Saturation", "Grayscale", "Sepia"]
        for effect in effects:
            checkbox = QCheckBox(effect)
            self.effect_checkboxes.append(checkbox)
            effects_layout.addWidget(checkbox)
        options_layout.addLayout(effects_layout)

        layout.addWidget(options_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Action buttons
        buttons_layout = QHBoxLayout()

        process_btn = QPushButton("⚡ Process Video")
        process_btn.clicked.connect(self.process_video)
        buttons_layout.addWidget(process_btn)

        preview_btn = QPushButton("👁️ Preview")
        preview_btn.clicked.connect(self.preview_video)
        buttons_layout.addWidget(preview_btn)

        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

        # Status label
        self.status_label = QLabel("Ready to process videos!")
        self.status_label.setStyleSheet("color: #90EE90; font-weight: bold;")
        layout.addWidget(self.status_label)

        return group

    def send_message(self):
        message = self.chat_input.toPlainText().strip()
        if not message:
            return

        self.chat_display.append(f"👤 You: {message}")
        self.chat_input.clear()

        # Show typing indicator
        self.chat_display.append("🤖 AI: Thinking...")

        # Send to API
        self.worker = ChatWorker(message)
        self.worker.response_received.connect(self.on_response_received)
        self.worker.error_occurred.connect(self.on_error_occurred)
        self.worker.start()

    def quick_message(self, prompt):
        self.chat_input.setPlainText(prompt)
        self.send_message()

    def on_response_received(self, response):
        # Remove typing indicator and add response
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.End)
        cursor.select(cursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()  # Remove newline

        self.chat_display.append(f"🤖 AI: {response}\n")

        # Scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_error_occurred(self, error):
        # Remove typing indicator and show error
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.End)
        cursor.select(cursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()

        self.chat_display.append(f"❌ Error: {error}\n")

    def select_video_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Video File",
            "", "Video Files (*.mp4 *.avi *.mov *.wmv *.flv *.mkv)"
        )
        if file_path:
            self.file_path.setText(os.path.basename(file_path))
            self.selected_file_path = file_path
            self.status_label.setText(f"Selected: {os.path.basename(file_path)}")

    def process_video(self):
        if not hasattr(self, 'selected_file_path'):
            self.status_label.setText("❌ Please select a video file first!")
            self.status_label.setStyleSheet("color: #FF6B6B; font-weight: bold;")
            return

        self.status_label.setText("⚡ Processing video...")
        self.status_label.setStyleSheet("color: #FFD93D; font-weight: bold;")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(50)

        # Simulate processing (in real implementation, this would call video processing APIs)
        import time
        QThread.msleep(2000)  # Simulate processing time

        self.progress_bar.setValue(100)
        self.status_label.setText("✅ Video processed successfully!")
        self.status_label.setStyleSheet("color: #90EE90; font-weight: bold;")

        # Hide progress bar after a delay
        QThread.msleep(1000)
        self.progress_bar.setVisible(False)

    def preview_video(self):
        if not hasattr(self, 'selected_file_path'):
            self.status_label.setText("❌ Please select a video file first!")
            return

        self.status_label.setText("👁️ Preview not implemented yet (would open video player)")

    def save_settings(self):
        settings = {
            "format": self.format_combo.currentText(),
            "quality": self.quality_combo.currentText(),
            "effects": [cb.text() for cb in self.effect_checkboxes if cb.isChecked()]
        }

        with open("video_settings.json", "w") as f:
            json.dump(settings, f, indent=2)

        self.status_label.setText("💾 Settings saved!")
        self.status_label.setStyleSheet("color: #90EE90; font-weight: bold;")

def main():
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Hybrid AI Video Remaker")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("AI Video Tools")

    window = VideoRemakerGUI()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()