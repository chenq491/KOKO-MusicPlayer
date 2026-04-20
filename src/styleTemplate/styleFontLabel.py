from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel

from singleton.themeManager import theme_manager


class StyleFontLabel(QLabel):
    def __init__(
        self,
        text,
        family="Microsoft YaHei",
        font_size=13,
        bold=True,
        color=theme_manager.current.text_bold,
        parent=None,
    ):
        super().__init__(parent)

        font = QFont()
        font.setFamily(family)
        font.setPointSize(font_size)
        font.setBold(bold)
        self.setFont(font)
        self.setStyleSheet(f"color: {color};")
        self.setText(text)

    def set_color(self, color):
        self.setStyleSheet(f"color: {color};")
