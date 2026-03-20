from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from styleTemplate.svgIconButton import SvgIconButton
from assets.svg import close_icon, fullscreen_icon, window_icon, min_icon, config_icon, home_icon
from uitls.utils import create_svg_icon


class TitleBar(QWidget):
    pageConfig = Signal()
    pageHome = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.initial_pos = None

        # 设置高度
        self.setFixedHeight(40)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 0, 0, 0)

        # 窗口标题
        self.title = QLabel("KOKO音乐播放器")
        self.title.setStyleSheet("""
            color: #4a4c57;
            font-size:20px;
            font-weight: bold;
            background-color: transparent;
        """)
        main_layout.addWidget(self.title)

        # 设置按钮
        self.config_button = ConfigButton(self)
        self.config_button.setFixedSize(40, 40)
        self.config_button.clicked.connect(self.pageConfig)

        # 主页按钮
        self.home_button = HomeButton(self)
        self.home_button.setFixedSize(40, 40)
        self.home_button.clicked.connect(self.pageHome)

        # 最小化按钮
        self.min_button = MinButton(self)
        self.min_button.setFixedSize(40, 40)
        self.min_button.clicked.connect(self.parent.showMinimized)

        # 最大化/还原按钮
        self.max_button = MaxButton(self)
        self.max_button.setFixedSize(40, 40)
        self.max_button.clicked.connect(self.toggle_maximize)

        # 关闭按钮
        self.close_button = CloseButton(self)
        self.close_button.setFixedSize(40, 40)
        self.close_button.setStyleSheet("""
            QPushButton { 
                color: #4a4c57; 
            } 
            QPushButton:hover { 
            }
        """)
        self.close_button.clicked.connect(self.parent.close_smooth)

        # 添加按钮到右侧
        main_layout.addStretch()
        main_layout.addWidget(self.home_button)
        main_layout.addWidget(self.config_button)
        main_layout.addWidget(self.min_button)
        main_layout.addWidget(self.max_button)
        main_layout.addWidget(self.close_button)

    def toggle_maximize(self):
        if self.parent.windowState() == Qt.WindowState.WindowMaximized or self.parent.windowState() == Qt.WindowState.WindowFullScreen:
            self.parent.showNormal()
            self.max_button.update_display(False)
        else:
            self.parent.showMaximized()
            self.max_button.update_display(True)

    # 允许通过标题栏拖动窗口
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.initial_pos is not None:
            if self.parent.windowState() == Qt.WindowState.WindowMaximized or self.parent.windowState() == Qt.WindowState.WindowFullScreen:
                self.parent.showNormal()
                self.max_button.update_display(False)
            delta = event.position().toPoint() - self.initial_pos
            self.parent.move(self.parent.pos() + delta)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.toggle_maximize()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.initial_pos = None


class CloseButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.normal_size = (40, 40)
        self.pressed_size = (12, 12)

        self.btn_icon = create_svg_icon(close_icon, self.normal_color, 15)
        self.hover_icon = create_svg_icon(close_icon, self.hover_color, 15)
        self.setIcon(self.btn_icon)


class MaxButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.normal_size = (40, 40)
        self.pressed_size = (15, 15)

        self.fullscreen_button = create_svg_icon(fullscreen_icon, self.normal_color, 18)
        self.fullscreen_button_hover = create_svg_icon(fullscreen_icon, self.hover_color, 18)

        self.window_button = create_svg_icon(window_icon, self.normal_color, 15)
        self.window_button_hover = create_svg_icon(window_icon, self.hover_color, 15)

        self.btn_icon = self.fullscreen_button
        self.hover_icon = self.fullscreen_button_hover
        self.setIcon(self.btn_icon)

    def update_display(self, is_fullscreen: bool):
        if is_fullscreen:
            self.btn_icon = self.window_button
            self.hover_icon = self.window_button_hover
        else:
            self.btn_icon = self.fullscreen_button
            self.hover_icon = self.fullscreen_button_hover
        self.setIcon(self.btn_icon)


class MinButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.normal_size = (40, 40)
        self.pressed_size = (12, 12)

        self.btn_icon = create_svg_icon(min_icon, self.normal_color, 15)
        self.hover_icon = create_svg_icon(min_icon, self.hover_color, 15)

        self.setIcon(self.btn_icon)

class ConfigButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setToolTip("设置")

        self.normal_size = (40, 40)
        self.pressed_size = (18, 18)

        self.btn_icon = create_svg_icon(config_icon, self.normal_color, 20)
        self.hover_icon = create_svg_icon(config_icon, self.hover_color, 20)

        self.setIcon(self.btn_icon)

class HomeButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setToolTip("主页")

        self.normal_size = (40, 40)
        self.pressed_size = (18, 18)

        self.btn_icon = create_svg_icon(home_icon, self.normal_color, 20)
        self.hover_icon = create_svg_icon(home_icon, self.hover_color, 20)

        self.setIcon(self.btn_icon)