from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton
from singleton.themeManager import theme_manager


class SvgIconButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.normal_size = (50, 50)
        self.pressed_size = (27, 27)

        self.normal_color = None
        self.hover_color = None

        self.btn_icon = None
        self.hover_icon = None

        # 设置固定高度和背景透明
        self.setFixedSize(*self.normal_size)
        self.setStyleSheet("""
                        QPushButton{
                            border: none;
                        }
                    """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # 鼠标样式变化
        self.setIconSize(QSize(*self.normal_size))

        theme_manager.themeChanged.connect(self.set_icon)

    def set_icon(self):
        self.normal_color = theme_manager.current.text_normal
        self.hover_color = theme_manager.current.text_light
        self.create_icon()
        self.setIcon(self.btn_icon)

    # @abstractmethod
    def create_icon(self):
        """创建图标"""
        pass

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
