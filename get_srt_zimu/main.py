#!/usr/bin/env python3
"""
Whisper Auto Captions - Python Version
Auto Captions for Final Cut Pro Powered by OpenAI's Whisper Model
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow


def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Whisper Auto Captions")
    app.setOrganizationName("Whisper Auto Captions")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

