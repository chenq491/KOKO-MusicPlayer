from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel


class StyleFontLabel(QLabel):
    def __init__(self, parent=None, family="Microsoft YaHei", size=12, bold=False, color="#fff"):
        super().__init__(parent)

        font = QFont()
        font.setFamily(family)
        font.setPointSize(size)
        font.setBold(bold)
        self.setFont(font)
        self.setStyleSheet(f"color: {color};")

