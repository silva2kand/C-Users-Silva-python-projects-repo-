"""
Enhanced AI Mouse Bot
A sophisticated AI assistant that follows your mouse and responds to voice commands.
"""

import sys
import os
import json
import time
import random
import threading
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                            QSystemTrayIcon, QMenu, QAction, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt, QPoint, QTimer, QSize, pyqtSignal, QObject
from PyQt5.QtGui import (QPainter, QColor, QPen, QIcon, QPixmap, QFont, 
                         QCursor, QLinearGradient, QBrush, QPainterPath)

# Import our custom modules
from ai_core import AICore
from vision_controller import VisionController, UIElement, ElementType
from voice_controller import VoiceController, VoiceState

# Constants
APP_NAME = "AI Mouse Bot"
VERSION = "1.0.0"
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".ai_mouse_bot")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Language support
LANGUAGE = {
    'en': {
        'title': 'AI Mouse Bot',
        'exit': 'Exit',
        'show': 'Show Bot',
        'hide': 'Hide Bot',
        'welcome': 'AI Mouse Bot is running. Right-click the system tray icon for options.',
        'listening': 'Listening...',
        'processing': 'Processing...',
        'speaking': 'Speaking...',
        'voice_on': 'Voice: On',
        'voice_off': 'Voice: Off',
        'language': 'Language',
        'settings': 'Settings',
        'about': 'About',
        'help': 'Help',
    },
    'ta': {
        'title': 'AI சுட்டி உதவி',
        'exit': 'வெளியேறு',
        'show': 'பாட்டைக் காட்டு',
        'hide': 'பாட்டை மறை',
        'welcome': 'AI சுட்டி உதவி இயங்குகிறது. விருப்பங்களுக்கு system tray ஐ வலது கிளிக் செய்யவும்.',
        'listening': 'கேட்கிறது...',
        'processing': 'செயல்படுகிறது...',
        'speaking': 'பேசுகிறது...',
        'voice_on': 'குரல்: இயக்கப்பட்டது',
        'voice_off': 'குரல்: முடக்கப்பட்டது',
        'language': 'மொழி',
        'settings': 'அமைப்புகள்',
        'about': 'விவரம்',
        'help': 'உதவி',
    }
}

class AISignals(QObject):
    """Signals for cross-thread communication."""
    command_received = pyqtSignal(dict)
    state_changed = pyqtSignal(str, str)  # old_state, new_state
    speak_requested = pyqtSignal(str)
    update_ui = pyqtSignal()

class AIMouseBot(QWidget):
    """Main application window for the AI Mouse Bot."""
    
    def __init__(self, lang: str = 'en'):
        super().__init__()
        
        # Initialize properties
        self.lang = lang
        self.is_following = False
        self.bot_visible = True
        self.voice_enabled = True
        self.bot_size = 40
        self.bot_color = QColor(65, 105, 225)  # Royal Blue
        self.bot_eye_color = QColor(255, 255, 255)  # White
        self.bot_pupil_color = QColor(0, 0, 0)  # Black
        self.bot_expression = "neutral"  # neutral, happy, sad, surprised, thinking
        self.last_mouse_pos = QPoint(0, 0)
        self.target_pos = QPoint(0, 0)
        self.smooth_speed = 0.2  # Lower is smoother but slower
        
        # Initialize AI components
        self.signals = AISignals()
        self.ai_core = AICore()
        self.vision = VisionController()
        self.voice = VoiceController(language=self._get_voice_language())
        
        # Setup UI and system tray
        self.init_ui()
        self.setup_tray_icon()
        
        # Connect signals
        self.signals.command_received.connect(self.handle_command)
        self.signals.state_changed.connect(self.handle_state_change)
        self.signals.speak_requested.connect(self.speak)
        self.signals.update_ui.connect(self.update)
        
        # Setup voice callbacks
        self.voice.on_command_callback = self._on_voice_command
        self.voice.on_state_change = self._on_voice_state_change
        
        # Start with voice listening if enabled
        if self.voice_enabled:
            self.voice.start_listening()
        
        # Start mouse tracking
        self.start_mouse_tracking()
        
        # Load configuration
        self.load_config()
        
        # Show welcome message
        self.show_welcome_message()
    
    def _get_voice_language(self) -> str:
        """Get the appropriate voice language code based on current language setting."""
        return 'en-US' if self.lang == 'en' else 'ta-IN'
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        
        # Set window attributes
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        
        # Set window size and position
        self.resize(self.bot_size * 2, self.bot_size * 2)
        self.move(100, 100)
        
        # Set window title
        self.setWindowTitle(LANGUAGE[self.lang]['title'])
        
        # Set up the layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Make the window click-through
        self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        # Start with the window hidden (only system tray icon visible)
        self.hide()
    
    def setup_tray_icon(self):
        """Set up the system tray icon and menu."""
        # Create the tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # Create the tray menu
        tray_menu = QMenu()
        
        # Toggle visibility action
        self.toggle_visibility_action = QAction(
            LANGUAGE[self.lang]['show'] if not self.isVisible() else LANGUAGE[self.lang]['hide'],
            self
        )
        self.toggle_visibility_action.triggered.connect(self.toggle_visibility)
        
        # Toggle voice action
        self.toggle_voice_action = QAction(
            LANGUAGE[self.lang]['voice_on'] if self.voice_enabled else LANGUAGE[self.lang]['voice_off'],
            self
        )
        self.toggle_voice_action.triggered.connect(self.toggle_voice)
        
        # Language menu
        lang_menu = QMenu(LANGUAGE[self.lang]['language'], self)
        
        # English language action
        en_action = QAction("English", self, checkable=True)
        en_action.setChecked(self.lang == 'en')
        en_action.triggered.connect(lambda: self.set_language('en'))
        
        # Tamil language action
        ta_action = QAction("தமிழ் (Tamil)", self, checkable=True)
        ta_action.setChecked(self.lang == 'ta')
        ta_action.triggered.connect(lambda: self.set_language('ta'))
        
        # Add language actions to the language menu
        lang_menu.addAction(en_action)
        lang_menu.addAction(ta_action)
        
        # Settings action
        settings_action = QAction(LANGUAGE[self.lang]['settings'], self)
        settings_action.triggered.connect(self.show_settings)
        
        # About action
        about_action = QAction(LANGUAGE[self.lang]['about'], self)
        about_action.triggered.connect(self.show_about)
        
        # Help action
        help_action = QAction(LANGUAGE[self.lang]['help'], self)
        help_action.triggered.connect(self.show_help)
        
        # Exit action
        exit_action = QAction(LANGUAGE[self.lang]['exit'], self)
        exit_action.triggered.connect(QApplication.quit)
        
        # Add actions to the tray menu
        tray_menu.addAction(self.toggle_visibility_action)
        tray_menu.addAction(self.toggle_voice_action)
        tray_menu.addMenu(lang_menu)
        tray_menu.addSeparator()
        tray_menu.addAction(settings_action)
        tray_menu.addAction(about_action)
        tray_menu.addAction(help_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)
        
        # Set the tray menu
        self.tray_icon.setContextMenu(tray_menu)
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Handle tray icon activation
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def start_mouse_tracking(self):
        """Start tracking mouse movements."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.follow_mouse)
        self.timer.start(20)  # ~50 FPS
    
    def follow_mouse(self):
        """Make the bot follow the mouse cursor."""
        if not self.bot_visible:
            return
            
        # Get current mouse position
        cursor_pos = QCursor.pos()
        
        # Calculate direction to mouse
        dx = cursor_pos.x() - self.target_pos.x()
        dy = cursor_pos.y() - self.target_pos.y()
        distance = (dx**2 + dy**2)**0.5
        
        # Update last mouse position
        self.last_mouse_pos = cursor_pos
        
        # If we're close enough, just snap to the mouse
        if distance < 5:
            self.target_pos = cursor_pos
            self.move(self.target_pos.x() - self.width() // 2, 
                     self.target_pos.y() - self.height() // 2)
            return
        
        # Smooth movement towards the mouse
        self.target_pos.setX(self.target_pos.x() + dx * self.smooth_speed)
        self.target_pos.setY(self.target_pos.y() + dy * self.smooth_speed)
        
        # Move the window
        self.move(self.target_pos.x() - self.width() // 2, 
                 self.target_pos.y() - self.height() // 2)
        
        # Update expression based on movement speed
        speed = (dx**2 + dy**2)**0.5
        if speed > 100:
            self.bot_expression = "surprised"
        elif speed > 30:
            self.bot_expression = "happy"
        else:
            self.bot_expression = "neutral"
        
        # Request UI update
        self.signals.update_ui.emit()
    
    def paintEvent(self, event):
        """Draw the bot."""
        if not self.bot_visible:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the bot body (circle)
        body_rect = self.rect().adjusted(5, 5, -5, -5)
        
        # Create a gradient for the body
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, self.bot_color.lighter(120))
        gradient.setColorAt(1, self.bot_color.darker(120))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(Qt.NoPen))
        
        # Draw the main circle
        painter.drawEllipse(body_rect)
        
        # Draw the eyes based on expression
        self._draw_eyes(painter, body_rect)
        
        # Draw the mouth based on expression
        self._draw_mouth(painter, body_rect)
    
    def _draw_eyes(self, painter, body_rect):
        """Draw the bot's eyes based on the current expression."""
        eye_size = body_rect.width() // 4
        eye_y = body_rect.center().y() - eye_size // 2
        left_eye_x = body_rect.center().x() - eye_size - 5
        right_eye_x = body_rect.center().x() + 5
        
        # Draw white of the eyes
        painter.setBrush(QBrush(self.bot_eye_color))
        painter.drawEllipse(left_eye_x, eye_y, eye_size, eye_size)
        painter.drawEllipse(right_eye_x, eye_y, eye_size, eye_size)
        
        # Draw pupils based on expression
        pupil_size = eye_size // 2
        pupil_offset = 0
        
        if self.bot_expression == "happy":
            pupil_offset = -2
        elif self.bot_expression == "sad":
            pupil_offset = 2
        elif self.bot_expression == "surprised":
            pupil_size = eye_size // 3
        elif self.bot_expression == "thinking":
            # Animate thinking (looking around)
            pupil_offset = int(3 * (time.time() % 2 - 1))  # -3 to 0
        
        # Left pupil
        painter.setBrush(QBrush(self.bot_pupil_color))
        painter.drawEllipse(
            left_eye_x + (eye_size - pupil_size) // 2 + pupil_offset,
            eye_y + (eye_size - pupil_size) // 2 + pupil_offset,
            pupil_size,
            pupil_size
        )
        
        # Right pupil
        painter.drawEllipse(
            right_eye_x + (eye_size - pupil_size) // 2 + pupil_offset,
            eye_y + (eye_size - pupil_size) // 2 + pupil_offset,
            pupil_size,
            pupil_size
        )
    
    def _draw_mouth(self, painter, body_rect):
        """Draw the bot's mouth based on the current expression."""
        mouth_width = body_rect.width() // 2
        mouth_height = body_rect.height() // 6
        mouth_x = body_rect.center().x() - mouth_width // 2
        mouth_y = body_rect.center().y() + mouth_height
        
        path = QPainterPath()
        
        if self.bot_expression == "happy":
            # Smile
            path.moveTo(mouth_x, mouth_y - mouth_height // 2)
            path.quadTo(
                body_rect.center().x(), mouth_y + mouth_height,
                mouth_x + mouth_width, mouth_y - mouth_height // 2
            )
        elif self.bot_expression == "sad":
            # Frown
            path.moveTo(mouth_x, mouth_y + mouth_height // 2)
            path.quadTo(
                body_rect.center().x(), mouth_y - mouth_height,
                mouth_x + mouth_width, mouth_y + mouth_height // 2
            )
        elif self.bot_expression == "surprised":
            # Small circle for surprise
            path.addEllipse(
                body_rect.center().x() - mouth_width // 4,
                mouth_y - mouth_height // 2,
                mouth_width // 2,
                mouth_height
            )
        elif self.bot_expression == "thinking":
            # Straight line for thinking
            path.moveTo(mouth_x, mouth_y)
            path.lineTo(mouth_x + mouth_width, mouth_y)
        else:  # neutral
            # Small straight line
            path.moveTo(mouth_x + mouth_width // 4, mouth_y)
            path.lineTo(mouth_x + 3 * mouth_width // 4, mouth_y)
        
        painter.setPen(QPen(self.bot_pupil_color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
    
    def toggle_visibility(self):
        """Toggle the visibility of the bot."""
        self.bot_visible = not self.bot_visible
        
        if self.bot_visible:
            self.show()
            self.toggle_visibility_action.setText(LANGUAGE[self.lang]['hide'])
        else:
            self.hide()
            self.toggle_visibility_action.setText(LANGUAGE[self.lang]['show'])
        
        self.save_config()
    
    def toggle_voice(self):
        """Toggle voice recognition on/off."""
        self.voice_enabled = not self.voice_enabled
        
        if self.voice_enabled:
            self.voice.start_listening()
            self.toggle_voice_action.setText(LANGUAGE[self.lang]['voice_on'])
        else:
            self.voice.stop()
            self.toggle_voice_action.setText(LANGUAGE[self.lang]['voice_off'])
        
        self.save_config()
    
    def set_language(self, lang: str):
        """Set the application language."""
        if lang != self.lang:
            self.lang = lang
            self.ai_core = AICore()  # Reinitialize AI with new language
            self.voice = VoiceController(language=self._get_voice_language())
            
            # Update UI
            self.setWindowTitle(LANGUAGE[self.lang]['title'])
            self.toggle_visibility_action.setText(
                LANGUAGE[self.lang]['hide'] if self.bot_visible else LANGUAGE[self.lang]['show']
            )
            self.toggle_voice_action.setText(
                LANGUAGE[self.lang]['voice_on'] if self.voice_enabled else LANGUAGE[self.lang]['voice_off']
            )
            
            # Save the new language preference
            self.save_config()
    
    def show_settings(self):
        """Show the settings dialog."""
        # For now, just show a message
        QMessageBox.information(
            self,
            LANGUAGE[self.lang]['settings'],
            "Settings dialog will be implemented here."
        )
    
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            f"About {LANGUAGE[self.lang]['title']}",
            f"""
            <h2>{LANGUAGE[self.lang]['title']} v{VERSION}</h2>
            <p>An intelligent AI assistant that follows your mouse and responds to voice commands.</p>
            <p>Created with ❤️ using Python and PyQt5.</p>
            <p>© 2025 AI Mouse Bot Team</p>
            """
        )
    
    def show_help(self):
        """Show the help dialog."""
        QMessageBox.information(
            self,
            f"{LANGUAGE[self.lang]['help']} - {LANGUAGE[self.lang]['title']}",
            """
            <h3>Voice Commands:</h3>
            <ul>
                <li>"Hello" - Greet the bot</li>
                <li>"What can you do?" - List available commands</li>
                <li>"Show yourself" - Show the bot</li>
                <li>"Go away" - Hide the bot</li>
                <li>"What time is it?" - Get the current time</li>
                <li>"Tell me a joke" - Hear a joke</li>
            </ul>
            
            <h3>System Tray:</h3>
            <p>Right-click the system tray icon to access the menu and change settings.</p>
            """
        )
    
    def show_welcome_message(self):
        """Show a welcome message when the application starts."""
        self.tray_icon.showMessage(
            LANGUAGE[self.lang]['title'],
            LANGUAGE[self.lang]['welcome'],
            QSystemTrayIcon.Information,
            3000  # 3 seconds
        )
    
    def tray_icon_activated(self, reason):
        """Handle system tray icon activation."""
        if reason == QSystemTrayIcon.Trigger:  # Single click
            self.toggle_visibility()
        # Double-click is handled automatically by the system
    
    def _on_voice_command(self, command):
        """Handle voice commands from the voice controller."""
        # Process the command in a separate thread to avoid blocking
        threading.Thread(
            target=self._process_voice_command,
            args=(command,),
            daemon=True
        ).start()
    
    def _process_voice_command(self, command):
        """Process a voice command."""
        try:
            # Update UI to show we're processing
            self.bot_expression = "thinking"
            self.signals.update_ui.emit()
            
            # Process the command using the AI core
            response = self.ai_core.process_input(command.text)
            
            # Update expression based on the response
            if "happy" in response['response'].lower():
                self.bot_expression = "happy"
            elif "sad" in response['response'].lower():
                self.bot_expression = "sad"
            else:
                self.bot_expression = "neutral"
            
            # Speak the response
            self.signals.speak_requested.emit(response['response'])
            
            # Update UI
            self.signals.update_ui.emit()
            
        except Exception as e:
            print(f"Error processing voice command: {e}")
            self.bot_expression = "sad"
            self.signals.update_ui.emit()
    
    def _on_voice_state_change(self, old_state, new_state):
        """Handle voice state changes."""
        # Update expression based on voice state
        if new_state == VoiceState.LISTENING:
            self.bot_expression = "surprised"
        elif new_state == VoiceState.PROCESSING:
            self.bot_expression = "thinking"
        elif new_state == VoiceState.SPEAKING:
            self.bot_expression = "happy"
        else:
            self.bot_expression = "neutral"
        
        # Update UI
        self.signals.update_ui.emit()
    
    def handle_command(self, command: Dict):
        """Handle a command from the AI core."""
        # This method can be expanded to handle different types of commands
        print(f"Handling command: {command}")
    
    def handle_state_change(self, old_state: str, new_state: str):
        """Handle state changes."""
        # This method can be used to update the UI based on state changes
        print(f"State changed from {old_state} to {new_state}")
    
    def speak(self, text: str):
        """Speak the given text."""
        if self.voice_enabled:
            self.voice.speak(text)
    
    def load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    
                    # Load settings
                    self.lang = config.get('language', self.lang)
                    self.bot_visible = config.get('bot_visible', self.bot_visible)
                    self.voice_enabled = config.get('voice_enabled', self.voice_enabled)
                    
                    # Apply settings
                    if self.bot_visible:
                        self.show()
                    else:
                        self.hide()
                    
                    if self.voice_enabled:
                        self.voice.start_listening()
                    else:
                        self.voice.stop()
                    
                    # Update UI
                    self.toggle_visibility_action.setText(
                        LANGUAGE[self.lang]['hide'] if self.bot_visible else LANGUAGE[self.lang]['show']
                    )
                    self.toggle_voice_action.setText(
                        LANGUAGE[self.lang]['voice_on'] if self.voice_enabled else LANGUAGE[self.lang]['voice_off']
                    )
                    
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            
            config = {
                'language': self.lang,
                'bot_visible': self.bot_visible,
                'voice_enabled': self.voice_enabled,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def closeEvent(self, event):
        """Handle the close event."""
        # Save configuration before closing
        self.save_config()
        
        # Stop the voice controller
        if hasattr(self, 'voice'):
            self.voice.stop()
        
        # Hide to the system tray instead of closing
        if not event.spontaneous() or not self.isVisible():
            return
        
        self.hide()
        event.ignore()

def main():
    """Main entry point for the application."""
    # Create the application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Set application information
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setOrganizationName("AI Mouse Bot")
    app.setOrganizationDomain("aimousebot.example.com")
    
    # Create and show the main window
    bot = AIMouseBot()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
