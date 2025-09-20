#!/usr/bin/env python3
"""
Simple test to check if PyQt5 window creation works
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Window")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()
        label = QLabel("Hello! This is a test window.\nIf you can see this, PyQt5 windows are working!")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    window.raise_()
    window.activateWindow()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()