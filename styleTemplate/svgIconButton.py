from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton


class SvgIconButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.normal_size = (50, 50)
        self.pressed_size = (27, 27)

        self.normal_color = "#5c6175"
        self.hover_color = "#70768f"

        self.btn_icon = None
        self.hover_icon = None

        # 设置按钮为圆形
        self.setFixedSize(*self.normal_size)
        self.setStyleSheet("""
                        QPushButton{
                            background-color: transparent;
                            border: none;
                        }
                    """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # 鼠标样式变化
        self.setIconSize(QSize(*self.normal_size))

    def enterEvent(self, event, /):
        self.setIcon(self.hover_icon)
        super().enterEvent(event)

    def leaveEvent(self, event, /):
        self.setIcon(self.btn_icon)
        super().leaveEvent(event)

    def mousePressEvent(self, e, /):
        self.setIconSize(QSize(*self.pressed_size))
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e, /):
        self.setIconSize(QSize(*self.normal_size))
        super().mouseReleaseEvent(e)
