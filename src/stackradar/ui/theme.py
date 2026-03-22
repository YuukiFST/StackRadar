from __future__ import annotations

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

# Paleta "Pure Black" minimalista e reta
BG = "#000000"
BG_ELEVATED = "#080808"
BG_CARD = "#000000"
BORDER = "#333333"
BORDER_SUBTLE = "#1a1a1a"
TEXT = "#eeeeee"
TEXT_MUTED = "#777777"
ACCENT = "#ffffff"
ACCENT_DIM = "#222222"
ACCENT_HOVER = "#dddddd"
DANGER = "#ff3333"
SUCCESS = "#33ff33"


def apply_black_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    pal = QPalette()
    c = QColor(BG)
    pal.setColor(QPalette.ColorRole.Window, c)
    pal.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    pal.setColor(QPalette.ColorRole.Base, QColor(BG_CARD))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(BG_ELEVATED))
    pal.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    pal.setColor(QPalette.ColorRole.Button, QColor(BG_ELEVATED))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(BORDER))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    pal.setColor(QPalette.ColorRole.PlaceholderText, QColor(TEXT_MUTED))
    app.setPalette(pal)
    app.setStyleSheet(global_stylesheet())


def global_stylesheet() -> str:
    return f"""
    QWidget {{
        background-color: {BG};
        color: {TEXT};
        font-size: 9pt;
    }}
    QMainWindow {{
        background-color: {BG};
    }}
    QTabWidget::pane {{
        border: 1px solid {BORDER};
        background-color: {BG};
        margin-top: -1px;
    }}
    QTabBar::tab {{
        background-color: {BG};
        color: {TEXT_MUTED};
        padding: 6px 16px;
        margin-right: 2px;
        border: 1px solid {BORDER};
        border-bottom: none;
        font-weight: normal;
        font-size: 9pt;
    }}
    QTabBar::tab:selected {{
        color: {TEXT};
        background-color: {BG_ELEVATED};
        border-bottom: 1px solid {BG_ELEVATED};
    }}
    QTabBar::tab:hover:!selected {{
        color: {TEXT};
        background-color: {BG_ELEVATED};
    }}
    QPushButton {{
        background-color: {BG};
        color: {TEXT};
        border: 1px solid {BORDER};
        border-radius: 0px;
        padding: 6px 12px;
        font-weight: normal;
    }}
    QPushButton:hover {{
        border-color: {TEXT};
        background-color: {BG_ELEVATED};
    }}
    QPushButton:pressed {{
        background-color: {TEXT};
        color: {BG};
    }}
    QPushButton:disabled {{
        color: {TEXT_MUTED};
        border-color: {BORDER_SUBTLE};
        background-color: {BG};
    }}
    QPushButton#PrimaryButton {{
        background-color: {BORDER};
        border: 1px solid {TEXT};
        color: {TEXT};
        font-weight: normal;
    }}
    QPushButton#PrimaryButton:hover {{
        background-color: {TEXT};
        color: {BG};
    }}
    QPushButton#PrimaryButton:disabled {{
        background-color: {BG};
        border-color: {BORDER};
        color: {TEXT_MUTED};
    }}
    QListWidget {{
        background-color: {BG};
        border: 1px solid {BORDER};
        border-radius: 0px;
        padding: 4px;
        outline: none;
    }}
    QListWidget::item {{
        padding: 6px 8px;
        border-radius: 0px;
        margin-bottom: 1px;
    }}
    QListWidget::item:selected {{
        background-color: {ACCENT_DIM};
        color: {ACCENT_HOVER};
    }}
    QListWidget::item:hover:!selected {{
        background-color: {BG_ELEVATED};
    }}
    QLineEdit, QTextEdit, QComboBox {{
        background-color: {BG};
        border: 1px solid {BORDER};
        border-radius: 0px;
        padding: 6px 8px;
        selection-background-color: {BORDER};
        color: {TEXT};
    }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border: 1px solid {TEXT_MUTED};
        background-color: {BG_ELEVATED};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid {TEXT_MUTED};
        margin-right: 4px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {BG};
        border: 1px solid {BORDER};
        border-radius: 0px;
        selection-background-color: {ACCENT_DIM};
        outline: none;
        padding: 2px;
    }}
    QGroupBox {{
        border: 1px solid {BORDER};
        border-radius: 0px;
        margin-top: 14px;
        padding: 16px 12px 10px 12px;
        font-weight: normal;
        color: {TEXT};
        background-color: {BG};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 8px;
        padding: 0 4px;
        color: {TEXT_MUTED};
        font-size: 9pt;
    }}
    QLabel#StatValue {{
        font-size: 16pt;
        font-weight: normal;
        color: {TEXT};
    }}
    QLabel#StatLabel {{
        font-size: 8pt;
        color: {TEXT_MUTED};
        font-weight: normal;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}
    QFrame#StatCard {{
        background-color: {BG};
        border: 1px solid {BORDER};
        border-radius: 0px;
    }}
    QFrame#StatCard:hover {{
        border: 1px solid {TEXT_MUTED};
        background-color: {BG_ELEVATED};
    }}
    QFrame#FetchBanner {{
        background-color: {BG_ELEVATED};
        border: 1px solid {BORDER};
        border-radius: 0px;
        border-left: 4px solid {TEXT};
    }}
    QProgressBar {{
        border: 1px solid {BORDER};
        border-radius: 0px;
        background-color: {BG};
        height: 6px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background-color: {TEXT};
        border-radius: 0px;
    }}
    QStatusBar {{
        background-color: {BG};
        border-top: 1px solid {BORDER};
        color: {TEXT_MUTED};
        padding-left: 4px;
    }}
    QMessageBox {{
        background-color: {BG};
    }}
    QMessageBox QLabel {{
        color: {TEXT};
        font-size: 9pt;
    }}
    QMessageBox QPushButton {{
        min-width: 60px;
    }}
    QScrollBar:vertical {{
        background: {BG};
        width: 10px;
        margin: 0;
        border-left: 1px solid {BORDER};
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 0px;
        min-height: 20px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {TEXT_MUTED};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background: {BG};
        height: 10px;
        margin: 0;
        border-top: 1px solid {BORDER};
    }}
    QScrollBar::handle:horizontal {{
        background: {BORDER};
        border-radius: 0px;
        min-width: 20px;
        margin: 0px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {TEXT_MUTED};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        border: none;
        background: none;
        width: 0px;
    }}
    """
