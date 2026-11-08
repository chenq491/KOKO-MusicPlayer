from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton

from assets.svg import (
    immersive_mode_icon,
    location_icon,
    next_song_icon,
    order_play_mode_icon,
    paused_icon,
    play_list_icon,
    playing_icon,
    prev_song_icon,
    random_play_mode_icon,
    repeat_play_mode_icon,
)
from constant import PlayMode, SongChanged
from singleton.themeManager import theme_manager
from styleTemplate.svgIconButton import SvgIconButton
from utils.utils import create_svg_icon


class PlayPausedButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 播放图标和暂停图标（颜色跟随主题的「主色上的内容色」）
        self.is_playing = False
        self.playing_icon = None
        self.paused_icon = None

        # 设置按钮为圆形
        self.setFixedSize(50, 50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # 鼠标样式变化

        self.update_style()
        # 初始绘制图标
        self.update_icon(False)

        theme_manager.themeChanged.connect(self.update_style)

    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton{{
                background-color: {theme_manager.current.accent};
                border: none;
                border-radius: 25px;
            }}
            QPushButton:hover{{
                background-color: {theme_manager.current.accent_hover};
            }}
            QPushButton:pressed{{
                background-color: {theme_manager.current.accent_active};
            }}
        """)
        # 主色背景上的图标要用对比色，换主题时需要重新生成
        icon_color = theme_manager.current.on_accent
        self.playing_icon = create_svg_icon(playing_icon, icon_color, 20)
        self.paused_icon = create_svg_icon(paused_icon, icon_color, 30)
        self.update_icon(self.is_playing)

    def update_icon(self, is_playing: bool):
        self.is_playing = is_playing
        if is_playing:
            self.setIcon(self.paused_icon)
        else:
            self.setIcon(self.playing_icon)
        self.setIconSize(QSize(50, 50))  # 初始尺寸


class NextOrPrevButton(SvgIconButton):
    def __init__(self, btn_type: SongChanged, parent=None):
        super().__init__(parent)

        self.btn_type = btn_type
        self.set_icon()

    def create_icon(self):
        if self.btn_type == SongChanged.NEXT:
            self.btn_icon = create_svg_icon(next_song_icon, self.normal_color, 30)
            self.hover_icon = create_svg_icon(next_song_icon, self.hover_color, 30)
        else:
            self.btn_icon = create_svg_icon(prev_song_icon, self.normal_color, 30)
            self.hover_icon = create_svg_icon(prev_song_icon, self.hover_color, 30)


class PlayListButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setToolTip("播放列表")
        self.set_icon()

    def create_icon(self):
        self.btn_icon = create_svg_icon(play_list_icon, self.normal_color, 30)
        self.hover_icon = create_svg_icon(play_list_icon, self.hover_color, 30)


class PlayModeButton(SvgIconButton):
    def __init__(self, parent=None, current_mode=PlayMode.ORDER):
        super().__init__(parent)

        self.setToolTip("顺序播放")

        self.current_mode = None
        self.btn_icon = None
        self.hover_icon = None
        self.update_display(current_mode)

    def create_icon(self):
        if self.current_mode == PlayMode.ORDER:
            icon = create_svg_icon(order_play_mode_icon, self.normal_color, 30)
            icon_hover = create_svg_icon(order_play_mode_icon, self.hover_color, 30)
        elif self.current_mode == PlayMode.RANDOM:
            icon = create_svg_icon(random_play_mode_icon, self.normal_color, 30)
            icon_hover = create_svg_icon(random_play_mode_icon, self.hover_color, 30)
        elif self.current_mode == PlayMode.REPEAT:
            icon = create_svg_icon(repeat_play_mode_icon, self.normal_color, 30)
            icon_hover = create_svg_icon(repeat_play_mode_icon, self.hover_color, 30)
        self.btn_icon = icon
        self.hover_icon = icon_hover

    def update_display(self, current_mode: PlayMode):
        self.current_mode = current_mode

        self.setToolTip(str(current_mode.value))
        self.set_icon()


class ImmersiveModeButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setToolTip("沉浸模式")

        self.normal_size = (40, 40)
        self.pressed_size = (28, 28)

        self.set_icon()

    def create_icon(self):
        self.btn_icon = create_svg_icon(immersive_mode_icon, self.normal_color, 30)
        self.hover_icon = create_svg_icon(immersive_mode_icon, self.hover_color, 30)


class LocationButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setToolTip("定位")

        self.normal_size = (40, 40)
        self.pressed_size = (28, 28)

        self.set_icon()

    def create_icon(self):
        self.btn_icon = create_svg_icon(location_icon, self.normal_color, 30)
        self.hover_icon = create_svg_icon(location_icon, self.hover_color, 30)
