from __future__ import annotations

import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from stackradar.ui.fonts import resolve_ui_font
from stackradar.ui.main_window import MainWindow
from stackradar.ui.theme import apply_black_theme


def _get_icon_path() -> str:
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, "radar_copy_icon_124877.ico")


def main() -> None:
    if os.name == "nt":
        import ctypes
        try:
            myappid = "stackradar.app.standalone.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    app = QApplication(sys.argv)
    
    icon_path = _get_icon_path()
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        
    apply_black_theme(app)
    app.setFont(resolve_ui_font(11))
    
    win = MainWindow()
    if os.path.exists(icon_path):
        win.setWindowIcon(QIcon(icon_path))
        
    win.show()
    raise SystemExit(app.exec())
