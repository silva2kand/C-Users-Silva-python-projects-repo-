"""GUI testing utilities for SpecKit"""

import sys
import time
from typing import Optional, Union, List
from unittest.mock import Mock

try:
    from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QTextEdit
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtTest import QTest
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    QApplication = None
    QWidget = None
    QPushButton = None
    QLineEdit = None
    QTextEdit = None
    Qt = None
    QTest = None

from .base_test import BaseTest

class GUITestCase(BaseTest):
    """Base class for GUI testing with PyQt5"""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for GUI tests"""
        if not PYQT_AVAILABLE:
            raise ImportError("PyQt5 is required for GUI testing")
            
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        super().setUp()
        self.widgets = []
        
    def tearDown(self):
        # Clean up widgets
        for widget in self.widgets:
            if widget:
                widget.close()
        self.widgets.clear()
        super().tearDown()
    
    def create_widget(self, widget_class, *args, **kwargs):
        """Create and track a widget for cleanup"""
        widget = widget_class(*args, **kwargs)
        self.widgets.append(widget)
        return widget
    
    def click_button(self, button: QPushButton, delay_ms: int = 100):
        """Click a button and wait"""
        if not PYQT_AVAILABLE:
            return
        QTest.mouseClick(button, Qt.LeftButton)
        QTest.qWait(delay_ms)
    
    def type_text(self, widget: Union[QLineEdit, QTextEdit], text: str, delay_ms: int = 50):
        """Type text into a widget"""
        if not PYQT_AVAILABLE:
            return
        widget.clear()
        QTest.keyClicks(widget, text)
        QTest.qWait(delay_ms)
    
    def key_press(self, widget: QWidget, key, delay_ms: int = 50):
        """Press a key on a widget"""
        if not PYQT_AVAILABLE:
            return
        QTest.keyPress(widget, key)
        QTest.qWait(delay_ms)
    
    def wait_for_signal(self, signal, timeout_ms: int = 5000):
        """Wait for a signal to be emitted"""
        if not PYQT_AVAILABLE:
            return False
            
        received = []
        signal.connect(lambda: received.append(True))
        
        start_time = time.time()
        while not received and (time.time() - start_time) * 1000 < timeout_ms:
            QTest.qWait(10)
            
        return len(received) > 0
    
    def assert_widget_visible(self, widget: QWidget):
        """Assert that a widget is visible"""
        self.assertTrue(widget.isVisible(), "Widget should be visible")
    
    def assert_widget_hidden(self, widget: QWidget):
        """Assert that a widget is hidden"""
        self.assertFalse(widget.isVisible(), "Widget should be hidden")
    
    def assert_widget_enabled(self, widget: QWidget):
        """Assert that a widget is enabled"""
        self.assertTrue(widget.isEnabled(), "Widget should be enabled")
    
    def assert_widget_disabled(self, widget: QWidget):
        """Assert that a widget is disabled"""
        self.assertFalse(widget.isEnabled(), "Widget should be disabled")
    
    def assert_text_equals(self, widget: Union[QLineEdit, QTextEdit], expected: str):
        """Assert that widget text equals expected value"""
        if isinstance(widget, QLineEdit):
            actual = widget.text()
        elif isinstance(widget, QTextEdit):
            actual = widget.toPlainText()
        else:
            actual = str(widget.text() if hasattr(widget, 'text') else widget)
            
        self.assertEqual(actual, expected, f"Expected '{expected}', got '{actual}'")
    
    def assert_text_contains(self, widget: Union[QLineEdit, QTextEdit], substring: str):
        """Assert that widget text contains substring"""
        if isinstance(widget, QLineEdit):
            actual = widget.text()
        elif isinstance(widget, QTextEdit):
            actual = widget.toPlainText()
        else:
            actual = str(widget.text() if hasattr(widget, 'text') else widget)
            
        self.assertIn(substring, actual, f"'{substring}' not found in '{actual}'")
    
    def screenshot(self, widget: QWidget, filename: str):
        """Take a screenshot of a widget"""
        if not PYQT_AVAILABLE:
            return
        pixmap = widget.grab()
        pixmap.save(filename)
    
    def simulate_user_interaction(self, widget: QWidget, actions: List[dict]):
        """Simulate a sequence of user interactions
        
        Actions format:
        [
            {'type': 'click', 'target': button_widget},
            {'type': 'type', 'target': line_edit, 'text': 'hello'},
            {'type': 'key', 'target': widget, 'key': Qt.Key_Enter},
            {'type': 'wait', 'ms': 1000}
        ]
        """
        if not PYQT_AVAILABLE:
            return
            
        for action in actions:
            action_type = action.get('type')
            
            if action_type == 'click':
                self.click_button(action['target'], action.get('delay', 100))
            elif action_type == 'type':
                self.type_text(action['target'], action['text'], action.get('delay', 50))
            elif action_type == 'key':
                self.key_press(action['target'], action['key'], action.get('delay', 50))
            elif action_type == 'wait':
                QTest.qWait(action.get('ms', 100))

class MockGUITestCase(BaseTest):
    """Mock GUI test case for when PyQt5 is not available"""
    
    def setUp(self):
        super().setUp()
        self.mock_widgets = {}
    
    def create_mock_widget(self, name: str, widget_type: str = 'generic'):
        """Create a mock widget for testing without GUI"""
        mock_widget = Mock()
        mock_widget.name = name
        mock_widget.widget_type = widget_type
        mock_widget.visible = True
        mock_widget.enabled = True
        mock_widget.text = ""
        
        # Add common methods
        mock_widget.show = Mock()
        mock_widget.hide = Mock()
        mock_widget.setEnabled = Mock()
        mock_widget.setText = Mock()
        mock_widget.getText = Mock(return_value="")
        
        self.mock_widgets[name] = mock_widget
        return mock_widget
    
    def simulate_click(self, widget_name: str):
        """Simulate clicking a mock widget"""
        widget = self.mock_widgets.get(widget_name)
        if widget:
            widget.clicked = True
            return True
        return False
    
    def simulate_text_input(self, widget_name: str, text: str):
        """Simulate text input on a mock widget"""
        widget = self.mock_widgets.get(widget_name)
        if widget:
            widget.text = text
            return True
        return False