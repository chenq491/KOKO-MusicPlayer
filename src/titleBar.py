from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QWidget

from assets.svg import (
    close_icon,
    config_icon,
    fullscreen_icon,
    home_icon,
    min_icon,
    window_icon,
)
from singleton.themeManager import theme_manager
from styleTemplate.styleFontLabel import StyleFontLabel
from styleTemplate.svgIconButton import SvgIconButton
from uitls.utils import create_svg_icon


class TitleBar(QWidget):
    pageConfig = Signal()
    pageHome = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.window_geo = parent.geometry()
        self.is_maximized = False

        self.initial_pos = None

        # 设置高度
        self.setFixedHeight(60)

        # 缩放动画
        self.anim = None

        # 窗口标题
        self.title = StyleFontLabel("KOKO音乐播放器", font_size=16)

        # 设置按钮
        self.config_button = ConfigButton(self)
        # 主页按钮
        self.home_button = HomeButton(self)
        # 最小化按钮
        self.min_button = MinButton(self)
        # 最大化/还原按钮
        self.max_button = MaxButton(self)
        # 关闭按钮
        self.close_button = CloseButton(self)

        self.init_ui()
        self.bind()

    def init_ui(self):
        """初始化布局"""
        self.config_button.setFixedSize(40, 40)
        self.home_button.setFixedSize(40, 40)
        self.min_button.setFixedSize(40, 40)
        self.max_button.setFixedSize(40, 40)
        self.close_button.setFixedSize(40, 40)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 0, 10, 0)
        main_layout.addWidget(self.title)
        main_layout.addStretch()
        main_layout.addWidget(self.home_button)
        main_layout.addWidget(self.config_button)
        main_layout.addWidget(self.min_button)
        main_layout.addWidget(self.max_button)
        main_layout.addWidget(self.close_button)

    def bind(self):
        """绑定事件"""
        self.config_button.clicked.connect(self.pageConfig)
        self.home_button.clicked.connect(self.pageHome)
        self.min_button.clicked.connect(self.parent.showMinimized)
        self.max_button.clicked.connect(self.toggle_maximize)
        self.close_button.clicked.connect(self.parent.close_smooth)

        theme_manager.themeChanged.connect(
            lambda: self.title.set_color(theme_manager.current.text_bold)
        )

    def freeze_layout(self):
        # 挂起布局，暂停所有子控件的几何更新
        self.parent.layout.setEnabled(False)
        # 临时关闭自动重绘
        self.parent.setUpdatesEnabled(False)

    def unfreeze_layout(self):
        # 恢复布局
        self.parent.layout.setEnabled(True)
        # 恢复重绘并强制一次完整更新
        self.parent.setUpdatesEnabled(True)
        self.parent.update()

    def toggle_maximize(self):
        # TODO 优化一下变量存储
        if self.is_maximized:
            start_geo = self.screen().geometry()
            end_geo = self.window_geo

            self.max_button.update_display(False)
        else:
            start_geo = self.parent.geometry()
            end_geo = self.screen().geometry()
            self.window_geo = start_geo

            self.max_button.update_display(True)

        self.resize_animation(start_geo, end_geo)
        self.is_maximized = not self.is_maximized

    def resize_animation(self, start_geo, end_geo):
        self.anim = QPropertyAnimation(self.parent, b"geometry")

        self.anim.setStartValue(start_geo)
        self.anim.setEndValue(end_geo)
        self.anim.setDuration(100)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim.start()

    # 允许通过标题栏拖动窗口
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.initial_pos is not None:
            if self.is_maximized:
                self.parent.setGeometry(self.window_geo)
                self.is_maximized = False

            if (
                self.parent.windowState() == Qt.WindowState.WindowMaximized
                or self.parent.windowState() == Qt.WindowState.WindowFullScreen
            ):
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

        self.set_icon()

    def create_icon(self):
        self.btn_icon = create_svg_icon(close_icon, self.normal_color, 15)
        self.hover_icon = create_svg_icon(close_icon, self.hover_color, 15)


class MaxButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.window_button = None
        self.window_button_hover = None
        self.fullscreen_button_hover = None
        self.fullscreen_button = None
        self.normal_size = (40, 40)
        self.pressed_size = (15, 15)

        self.set_icon()

    def create_icon(self):
        self.fullscreen_button = create_svg_icon(fullscreen_icon, self.normal_color, 18)
        self.fullscreen_button_hover = create_svg_icon(
            fullscreen_icon, self.hover_color, 18
        )

        self.window_button = create_svg_icon(window_icon, self.normal_color, 15)
        self.window_button_hover = create_svg_icon(window_icon, self.hover_color, 15)

        self.btn_icon = self.fullscreen_button
        self.hover_icon = self.fullscreen_button_hover

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

        self.set_icon()

    def create_icon(self):
        self.btn_icon = create_svg_icon(min_icon, self.normal_color, 15)
        self.hover_icon = create_svg_icon(min_icon, self.hover_color, 15)


class ConfigButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setToolTip("设置")

        self.normal_size = (40, 40)
        self.pressed_size = (18, 18)

        self.set_icon()

    def create_icon(self):
        self.btn_icon = create_svg_icon(config_icon, self.normal_color, 20)
        self.hover_icon = create_svg_icon(config_icon, self.hover_color, 20)


class HomeButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setToolTip("主页")

        self.normal_size = (40, 40)
        self.pressed_size = (18, 18)

        self.set_icon()

    def create_icon(self):
        self.btn_icon = create_svg_icon(home_icon, self.normal_color, 20)
        self.hover_icon = create_svg_icon(home_icon, self.hover_color, 20)
