from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from stackradar.ui import theme


class TitleBar(QWidget):
    minimize_requested = pyqtSignal()
    maximize_requested = pyqtSignal()
    close_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(32)
        self.setStyleSheet(f"background-color: {theme.BG}; color: {theme.TEXT_MUTED};")
        
        self.title_lbl = QLabel(" stackradar ")
        self.title_lbl.setStyleSheet(f"font-size: 9pt; color: {theme.TEXT_MUTED};")

        self.btn_min = self._make_btn("−", self.minimize_requested)
        self.btn_max = self._make_btn("□", self.maximize_requested)
        self.btn_close = self._make_btn("×", self.close_requested)
        self.btn_close.setObjectName("CloseButton")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(0)
        
        layout.addWidget(self.title_lbl)
        layout.addStretch()
        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_max)
        layout.addWidget(self.btn_close)

        self._start_pos = None

    def _make_btn(self, text: str, signal: pyqtSignal) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(40, 32)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip(text)
        btn.clicked.connect(signal.emit)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; border: none; font-size: 10pt; color: {theme.TEXT_MUTED};
            }}
            QPushButton:hover {{
                background-color: {theme.BG_ELEVATED}; color: {theme.TEXT};
            }}
            QPushButton#CloseButton:hover {{
                background-color: {theme.DANGER}; color: #ffffff;
            }}
        """)
        return btn

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event) -> None:
        if self._start_pos is not None:
            delta = event.globalPosition().toPoint() - self._start_pos
            if self.window():
                self.window().move(self.window().pos() + delta)
            self._start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event) -> None:
        self._start_pos = None

    def mouseDoubleClickEvent(self, event) -> None:
        self.maximize_requested.emit()
