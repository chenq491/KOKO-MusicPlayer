from PySide6.QtCore import Signal, Slot, Qt, QSize, QRectF, QRect
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush
from PySide6.QtWidgets import QWidget, QHBoxLayout, QApplication, QLabel, QPushButton, QVBoxLayout, QSlider
from constant import SongChanged, PlayMode, COVER_SiZE
from songList.songItem import SongItem
from assets.svg import playing_icon, paused_icon, next_song_icon, prev_song_icon, play_list_icon, order_play_mode_icon, \
    random_play_mode_icon, repeat_play_mode_icon, immersive_mode_icon, location_icon
from styleTemplate.svgIconButton import SvgIconButton
from theme import theme_manager
from uitls.utils import create_svg_icon, ms_to_str, create_style_label


class ProgressSlider(QSlider):
    """进度条"""

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)

        self.handle_pix = QPixmap("assets/guitar.svg")

        self.setFixedHeight(10)

        self.setMouseTracking(True)  # 开启鼠标追踪以支持 hover 效果
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # 鼠标样式变化

        self.groove_height = 4
        self.groove_border_color = QColor(255, 255, 255)
        self.groove_border_width = 1
        self.groove_progress_color = None
        self.groove_bg_color = None
        self.groove_radius = 2

        self.groove_rect = QRect(
            self.rect().left(),
            self.rect().top() + ((self.rect().height() - self.groove_height) // 2),
            self.rect().width(),
            self.groove_height
        )

        self.set_style()

        theme_manager.themeChanged.connect(self.set_style)

    def set_style(self):
        self.groove_bg_color = QColor(theme_manager.current.bg_color_400)
        self.groove_progress_color = QColor(theme_manager.current.bg_color_700)

    def resizeEvent(self, event, /):
        super().resizeEvent(event)
        self.groove_rect = QRect(
            self.rect().left(),
            self.rect().top() + ((self.rect().height() - self.groove_height) // 2),
            self.rect().width(),
            self.groove_height
        )

    def get_ratio(self):
        # 计算进度条的宽度
        if self.maximum() == self.minimum():
            progress_ratio = 0.0
        else:
            progress_ratio = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
        return progress_ratio

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # TODO 这里可以选择性地重绘背景，达到性能优化
        """
        绘制滑槽
        """
        # 计算进度条的宽度
        # if self.maximum() == self.minimum():
        #     progress_ratio = 0.0
        # else:
        #     progress_ratio = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
        progress_width = int(self.groove_rect.width() * self.get_ratio())
        progress_rect = QRect(
            self.groove_rect.left(),
            self.groove_rect.top(),
            progress_width,
            self.groove_rect.height()
        )

        # 绘制滑槽边框和背景
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        # painter.setPen(QPen(self.groove_border_color, self.groove_border_width))  # 边框
        painter.setBrush(QBrush(self.groove_bg_color))  # 背景
        painter.drawRoundedRect(
            self.groove_rect,
            self.groove_radius,
            self.groove_radius
        )
        painter.restore()

        # 绘制滑槽进度
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)  # 无边框
        painter.setBrush(QBrush(self.groove_progress_color))
        painter.drawRoundedRect(
            progress_rect,
            self.groove_radius if progress_width > 0 else 0,  # 有进度才显示圆角
            self.groove_radius if progress_width > 0 else 0,
        )
        painter.restore()

        """
        绘制手柄
        """
        handle_rect = QRect(
            progress_rect.right() - 16,
            self.rect().top() + ((self.rect().height() - 32) // 2),
            32, 32
        )
        center_x = handle_rect.center().x()
        center_y = handle_rect.center().y()

        painter.save()
        painter.setClipping(False)
        painter.translate(center_x, center_y)
        if self.underMouse():  # 鼠标悬浮
            painter.rotate(15)
        if self.isSliderDown():  # 鼠标按下
            painter.scale(1.2, 1.2)
        w = self.handle_pix.width()
        h = self.handle_pix.height()
        target_rect = QRectF(-w / 2, -h / 2, w, h)
        # painter.drawPixmap(target_rect.toRect(), self.handle_pix)
        painter.restore()

    def mousePressEvent(self, event):
        # 如果需要自定义点击区域（比如只点击图片有效区域），可以在这里拦截
        # 否则直接调用父类，保持默认拖动行为
        super().mousePressEvent(event)


class BottomPanel(QWidget):
    playlistButtonClicked = Signal()
    songChangedButtonClicked = Signal(SongChanged)
    playOrPausedButtonClicked = Signal()
    platModeChanged = Signal(PlayMode)
    pageImmersiveMode = Signal()
    location = Signal()
    songProgressChanged = Signal(int)
    rectChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.PLAY_MODE_LIST = list(PlayMode)
        self.current_play_mode_index = 0

        # 设置为固定高度
        self.setFixedHeight(110)

        # 歌曲进度条
        self.progress_slider = ProgressSlider()

        left_layout = QHBoxLayout()
        # 当前播放歌曲封面
        self.current_song_cover = QLabel()
        self.current_song_cover.setFixedWidth(60)  # 设置封面为固定宽度
        self.current_song_cover.setPixmap(QPixmap("./assets/default_cover.png").scaled(
            COVER_SiZE,
            COVER_SiZE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        # 当前歌曲标题
        current_song_info = QVBoxLayout()
        current_song_info.setContentsMargins(0, 0, 0, 0)
        current_song_info.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.current_song_title = create_style_label("歌曲标题", font_size=11,
                                                     color=theme_manager.current.text_color_300)
        self.current_song_title.setWordWrap(True)
        self.current_song_artist = create_style_label("歌手", font_size=10, color=theme_manager.current.text_color_100)
        self.current_song_artist.setWordWrap(True)
        current_song_info.addWidget(self.current_song_title)
        current_song_info.addWidget(self.current_song_artist)
        left_layout.addWidget(self.current_song_cover)
        left_layout.addLayout(current_song_info)
        left_layout.addStretch(1)

        center_layout = QHBoxLayout()
        # 选择歌曲模式下拉框
        self.play_mode_button = PlayModeButton(self)
        # 上一首按钮
        self.prev_song_button = NextOrPrevButton(SongChanged.PREV, self)
        self.prev_song_button.setToolTip("上一首")
        # 下一首按钮
        self.next_song_button = NextOrPrevButton(SongChanged.NEXT, self)
        self.next_song_button.setToolTip("下一首")
        # 播放/暂停按钮
        self.play_or_paused_button = PlayPausedButton(self)
        # 展示播放列表按钮
        self.show_playlist_button = PlayListButton(self)
        self.show_playlist_button.setToolTip("播放列表")
        center_layout.addWidget(self.play_mode_button)
        center_layout.addWidget(self.prev_song_button)
        center_layout.addWidget(self.play_or_paused_button)
        center_layout.addWidget(self.next_song_button)
        center_layout.addWidget(self.show_playlist_button)

        right_layout = QHBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        # 沉浸模式按钮
        self.immersive_mode_button = ImmersiveModeButton(self)
        # 定位按钮
        self.location_button = LocationButton(self)
        # 歌曲时间信息
        self.time_label = create_style_label("00:00 / 00:00", font_size=11, color=theme_manager.current.text_color_200)
        right_layout.addStretch(3)
        right_layout.addWidget(self.time_label)
        right_layout.addStretch(1)
        right_layout.addWidget(self.location_button)
        right_layout.addWidget(self.immersive_mode_button)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(9, 12, 9, 0)
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(center_layout, 2)
        main_layout.addLayout(right_layout, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.progress_slider)
        layout.addLayout(main_layout)

        self.setObjectName("bottomPanel")
        self.setAutoFillBackground(True)
        self.setStyleSheet("""
            #bottomPanel{
                background: transparent;
            }
        """)

        self.bind()

    def bind(self):
        """绑定事件"""
        self.play_mode_button.clicked.connect(self.on_play_mode_changed)  # 播放模式切换
        self.prev_song_button.clicked.connect(self.on_prev_song_button_clicked)  # 上一首
        self.next_song_button.clicked.connect(self.on_next_song_button_clicked)  # 下一首
        self.play_or_paused_button.clicked.connect(self.on_play_or_paused)  # 播放/暂停
        self.show_playlist_button.clicked.connect(self.on_playlist_button_clicked)  # 展示音乐列表
        self.immersive_mode_button.clicked.connect(self.pageImmersiveMode)  # 进入沉浸模式
        self.location_button.clicked.connect(self.on_location_button_clicked)  # 定位到当前音乐
        self.progress_slider.valueChanged.connect(self.on_progress_slider_changed)  # 歌曲进度条拖动

    def set_current_song(self, song_item: SongItem):
        """设置当前播放音乐"""
        self.current_song_cover.setPixmap(song_item.cover)
        self.current_song_title.setText(song_item.title)
        self.current_song_artist.setText(song_item.artist)

    def update_display(self, is_playing: bool):
        """更新视图"""
        self.play_or_paused_button.update_icon(is_playing)

    def get_current_play_mode(self, is_index=True):
        if is_index:
            return self.current_play_mode_index
        else:
            return self.PLAY_MODE_LIST[self.current_play_mode_index]

    def set_current_play_mode(self, current_mode_index, is_changing=False):
        """设置当前播放模式"""
        self.current_play_mode_index = current_mode_index
        current_mode = self.PLAY_MODE_LIST[self.current_play_mode_index]
        self.play_mode_button.update_display(current_mode)
        if is_changing:
            self.platModeChanged.emit(current_mode)

    def reset_progress(self):
        """重置进度"""
        self.time_label.setText("00:00 / 00:00")
        self.progress_slider.setValue(0)
        self.progress_slider.setEnabled(True)

    def update_progress(self, position, duration):
        """更新进度"""
        if duration < 0:
            return
        # 更新时间标签
        self.time_label.setText(f"{ms_to_str(position)} / {ms_to_str(duration)}")
        # 更新进度条
        self.progress_slider.blockSignals(True)  # 阻塞信号
        self.progress_slider.setMaximum(duration)
        self.progress_slider.setValue(position)
        self.progress_slider.blockSignals(False)

    def showEvent(self, event, /):
        super().showEvent(event)
        self.rectChanged.emit()

    def resizeEvent(self, event, /):
        super().resizeEvent(event)
        self.rectChanged.emit()

    @Slot()
    def on_playlist_button_clicked(self):
        """播放列表按钮点击"""
        self.playlistButtonClicked.emit()

    @Slot()
    def on_next_song_button_clicked(self):
        """下一首歌"""
        self.songChangedButtonClicked.emit(SongChanged.NEXT)

    @Slot()
    def on_prev_song_button_clicked(self):
        """上一首歌"""
        self.songChangedButtonClicked.emit(SongChanged.PREV)

    @Slot()
    def on_play_or_paused(self):
        """播放或暂停歌曲"""
        self.playOrPausedButtonClicked.emit()

    @Slot()
    def on_play_mode_changed(self):
        """歌曲播放模式改变"""
        self.set_current_play_mode((self.current_play_mode_index + 1) % len(self.PLAY_MODE_LIST), is_changing=True)

    @Slot()
    def on_location_button_clicked(self):
        """定位到当前歌曲"""
        self.location.emit()

    @Slot()
    def on_progress_slider_changed(self, value):
        """歌曲进度改变"""
        self.songProgressChanged.emit(value)


class PlayPausedButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._normal_color = theme_manager.current.bg_color_600  # 默认颜色
        self._hover_color = theme_manager.current.bg_color_700  # 悬停颜色

        # 播放图标和暂停图标
        self.playing_icon = create_svg_icon(playing_icon, theme_manager.current.bg_color_0, 20)
        self.paused_icon = create_svg_icon(paused_icon, theme_manager.current.bg_color_0, 30)

        # 设置按钮为圆形
        self.setFixedSize(50, 50)
        self.setStyleSheet(f"""
            QPushButton{{
                background-color: {self._normal_color};
                border: none;
                border-radius: 25px;
            }}
            QPushButton:hover{{
                background-color: {self._hover_color};
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # 鼠标样式变化

        # 初始绘制图标
        self.update_icon(False)

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


if __name__ == "__main__":
    app = QApplication([])
    bottom = BottomPanel()
    bottom.show()
    app.exec()
