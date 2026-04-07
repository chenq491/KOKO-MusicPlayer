from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton

from assets.svg import immersive_mode_icon, playing_icon, paused_icon, next_song_icon, prev_song_icon, play_list_icon, \
    order_play_mode_icon, random_play_mode_icon, repeat_play_mode_icon, location_icon
from constant import SongChanged, PlayMode
from singleton.themeManager import theme_manager
from styleTemplate.svgIconButton import SvgIconButton
from uitls.utils import create_svg_icon


class PlayPausedButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 播放图标和暂停图标
        self.playing_icon = create_svg_icon(playing_icon, "#ffffff", 20)
        self.paused_icon = create_svg_icon(paused_icon, "#ffffff", 30)

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
                background-color: {theme_manager.current.button_bg};
                border: none;
                border-radius: 25px;
            }}
            QPushButton:hover{{
                background-color: {theme_manager.current.button_hover};
            }}
        """)

    def update_icon(self, is_playing: bool):
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
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setToolTip("顺序播放")

        self.repeat_icon_hover = None
        self.repeat_icon = None
        self.random_icon_hover = None
        self.random_icon = None
        self.order_icon = None
        self.order_icon_hover = None

        self.btn_icon = self.order_icon
        self.hover_icon = self.order_icon_hover
        self.set_icon()

    def create_icon(self):
        self.order_icon = create_svg_icon(order_play_mode_icon, self.normal_color, 30)
        self.order_icon_hover = create_svg_icon(order_play_mode_icon, self.hover_color, 30)
        self.random_icon = create_svg_icon(random_play_mode_icon, self.normal_color, 30)
        self.random_icon_hover = create_svg_icon(random_play_mode_icon, self.hover_color, 30)
        self.repeat_icon = create_svg_icon(repeat_play_mode_icon, self.normal_color, 30)
        self.repeat_icon_hover = create_svg_icon(repeat_play_mode_icon, self.hover_color, 30)

        self.btn_icon = self.order_icon
        self.hover_icon = self.order_icon_hover

    def update_display(self, current_mode: PlayMode):
        if current_mode == PlayMode.ORDER:
            self.btn_icon = self.order_icon
            self.hover_icon = self.order_icon_hover
        elif current_mode == PlayMode.RANDOM:
            self.btn_icon = self.random_icon
            self.hover_icon = self.random_icon_hover
        elif current_mode == PlayMode.REPEAT:
            self.btn_icon = self.repeat_icon
            self.hover_icon = self.repeat_icon_hover

        self.setToolTip(str(current_mode.value))
        self.setIcon(self.btn_icon)


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
