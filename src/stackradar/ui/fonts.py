import logging
from PyQt6.QtGui import QFont, QFontDatabase

def resolve_ui_font(size: int = 9, weight: int = QFont.Weight.Normal) -> QFont:
    fallback = ["Iosevka", "Consolas", "Courier New", "Courier"]
    db = QFontDatabase.families()
    family = "Courier New"
    for f in fallback:
        if f in db:
            family = f
            break
    font = QFont(family, size, weight)
    font.setStyleHint(QFont.StyleHint.Monospace)
    return font

def configure_matplotlib_font() -> None:
    # Disable findfont debug spam from matplotlib font_manager
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

def matplotlib_font_candidates() -> list[str]:
    return ["Iosevka", "Consolas", "Courier New", "monospace"]
