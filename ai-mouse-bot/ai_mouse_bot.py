#!/usr/bin/env python3
"""
AI Mouse Bot - A smart bot that follows your mouse with natural language support
Supports both English and Tamil
"""

import sys
import os
import json
import time
import threading
import pyautogui
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                            QSystemTrayIcon, QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt, QPoint, QTimer, QSize
from PyQt5.QtGui import QPainter, QColor, QPen, QIcon, QPixmap, QFont, QCursor

# Language support
LANGUAGE = {
    'en': {
        'title': 'AI Mouse Bot',
        'exit': 'Exit',
        'show': 'Show Bot',
        'hide': 'Hide Bot',
        'welcome': 'AI Mouse Bot is running. Right-click the system tray icon for options.',
    },
    'ta': {
        'title': 'AI சுட்டி உதவி',
        'exit': 'வெளியேறு',
        'show': 'பாட்டைக் காட்டு',
        'hide': 'பாட்டை மறை',
        'welcome': 'AI சுட்டி உதவி இயங்குகிறது. விருப்பங்களுக்கு system tray ஐ வலது கிளிக் செய்யவும்.',
    }
}

class AIMouseBot(QWidget):
    def __init__(self, lang='en'):
        super().__init__()
        self.lang = lang
        self.is_following = False
        self.bot_visible = True
        self.bot_size = 40
        self.bot_color = QColor(65, 105, 225)  # Royal Blue
        self.init_ui()
        self.setup_tray_icon()
        self.start_mouse_tracking()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(self.bot_size, self.bot_size)
        
        # Center the bot on screen initially
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.center() - self.rect().center())
        
    def setup_tray_icon(self):
        """Create system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("input-mouse"))
        
        # Create menu
        tray_menu = QMenu()
        
        # Toggle visibility
        self.toggle_visibility = QAction(LANGUAGE[self.lang]['show'] if not self.bot_visible 
                                       else LANGUAGE[self.lang]['hide'], self)
        self.toggle_visibility.triggered.connect(self.toggle_bot_visibility)
        
        # Exit action
        exit_action = QAction(LANGUAGE[self.lang]['exit'], self)
        exit_action.triggered.connect(QApplication.quit)
        
        # Add actions to menu
        tray_menu.addAction(self.toggle_visibility)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.showMessage(
            LANGUAGE[self.lang]['title'],
            LANGUAGE[self.lang]['welcome'],
            QSystemTrayIcon.Information,
            3000
        )
    
    def toggle_bot_visibility(self):
        """Toggle bot visibility"""
        self.bot_visible = not self.bot_visible
        self.setVisible(self.bot_visible)
        self.toggle_visibility.setText(
            LANGUAGE[self.lang]['hide'] if self.bot_visible 
            else LANGUAGE[self.lang]['show']
        )
    
    def paintEvent(self, event):
        """Draw the bot"""
        if not self.bot_visible:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw bot circle
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.bot_color)
        painter.drawEllipse(0, 0, self.bot_size, self.bot_size)
        
        # Draw eyes
        eye_size = self.bot_size // 4
        painter.setBrush(Qt.white)
        painter.drawEllipse(self.bot_size // 4, self.bot_size // 3, eye_size, eye_size)
        painter.drawEllipse((self.bot_size // 4) * 2, self.bot_size // 3, eye_size, eye_size)
        
        # Draw smile
        smile_rect = self.rect().adjusted(
            self.bot_size // 4, 
            self.bot_size // 2,
            -self.bot_size // 4,
            -self.bot_size // 4
        )
        painter.setPen(QPen(Qt.white, 2))
        painter.drawArc(smile_rect, 0, -180 * 16)
    
    def start_mouse_tracking(self):
        """Start tracking mouse movements"""
        self.mouse_timer = QTimer(self)
        self.mouse_timer.timeout.connect(self.follow_mouse)
        self.mouse_timer.start(20)  # Update every 20ms
    
    def follow_mouse(self):
        """Make the bot follow the mouse cursor"""
        if not self.is_following:
            return
            
        # Get current mouse position
        mouse_pos = QCursor.pos()
        
        # Calculate new position (slightly offset from cursor)
        new_x = mouse_pos.x() - (self.width() // 2)
        new_y = mouse_pos.y() - (self.height() // 2) - 20  # Slightly above cursor
        
        # Smooth movement
        current_pos = self.pos()
        dx = (new_x - current_pos.x()) * 0.2
        dy = (new_y - current_pos.y()) * 0.2
        
        self.move(int(current_pos.x() + dx), int(current_pos.y() + dy))
    
    def mousePressEvent(self, event):
        """Make window draggable"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def enterEvent(self, event):
        """When mouse enters the bot"""
        self.is_following = False
        self.bot_color = QColor(255, 69, 0)  # Orange-Red
        self.update()
    
    def leaveEvent(self, event):
        """When mouse leaves the bot"""
        self.is_following = True
        self.bot_color = QColor(65, 105, 225)  # Royal Blue
        self.update()

def main():
    app = QApplication(sys.argv)
    
    # Set application info
    app.setApplicationName("AI Mouse Bot")
    app.setQuitOnLastWindowClosed(False)
    
    # Create and show the bot
    bot = AIMouseBot(lang='en')  # Default to English
    bot.show()
    
    # Start following mouse
    bot.is_following = True
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
