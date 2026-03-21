from PySide6.QtCore import Signal, Slot, Qt, QSize, QRectF, QRect
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QWidget, QHBoxLayout, QApplication, QLabel, QPushButton, QVBoxLayout, QSlider, \
    QStyleOptionSlider, QStyle

from constant import SongChanged, PlayMode
from bak.songItem import SongItem, create_pixmap_from_bytes
from assets.svg import playing_icon, paused_icon, next_song_icon, prev_song_icon, play_list_icon, order_play_mode_icon, \
    random_play_mode_icon, repeat_play_mode_icon, immersive_mode_icon
from styleTemplate.svgIconButton import SvgIconButton
from uitls.utils import create_svg_icon, ms_to_str


class ProgressSlider(QSlider):
    """进度条"""

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.handle_pix = QPixmap("assets/吉他.svg")

        self.setFixedHeight(32)

        self.setMouseTracking(True)  # 开启鼠标追踪以支持 hover 效果
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

        self.groove_height = 4
        self.groove_border_color = QColor(255, 255, 255)
        self.groove_border_width = 1
        self.groove_bg_color = QColor("#cbcfea")
        self.groove_radius = 2
        self.groove_progress_color = QColor("#8186cc")

        self.groove_rect = QRect(
            self.rect().left(),
            self.rect().top() + ((self.rect().height() - self.groove_height) // 2),
            self.rect().width(),
            self.groove_height
        )

    def resizeEvent(self, event, /):
        super().resizeEvent(event)
        self.groove_rect = QRect(
            self.rect().left(),
            self.rect().top() + ((self.rect().height() - self.groove_height) // 2),
            self.rect().width(),
            self.groove_height
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setClipping(False)

        # TODO 这里可以选择性地重绘背景，达到性能优化
        """
        绘制滑槽
        """
        # 计算进度条的宽度
        progress_ratio = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
        progress_width = int(self.groove_rect.width() * progress_ratio)
        progress_rect = QRect(
            self.groove_rect.left(),
            self.groove_rect.top(),
            progress_width,
            self.groove_rect.height()
        )

        # 绘制滑槽边框和背景
        painter.save()
        painter.setPen(QPen(self.groove_border_color, self.groove_border_width))  # 边框
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
            self.rect().top() + ((self.rect().height() -32) // 2),
            32, 32
        )
        center_x = handle_rect.center().x()
        center_y = handle_rect.center().y()

        painter.save()
        painter.translate(center_x, center_y)
        if self.underMouse():  # 鼠标悬浮
            painter.rotate(15)
        if self.isSliderDown():  # 鼠标按下
            painter.scale(1.2, 1.2)
        w = self.handle_pix.width()
        h = self.handle_pix.height()
        target_rect = QRectF(-w / 2, -h / 2, w, h)
        painter.drawPixmap(target_rect.toRect(), self.handle_pix)
        painter.restore()

    def mousePressEvent(self, event):
        # 如果需要自定义点击区域（比如只点击图片有效区域），可以在这里拦截
        # 否则直接调用父类，保持默认拖动行为
        super().mousePressEvent(event)


class ProgressDisplay(QWidget):
    songProgressChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(32)

        # 歌曲进度条
        self.song_progress_slider = ProgressSlider(Qt.Orientation.Horizontal)
        self.song_progress_slider.valueChanged.connect(self.on_song_progress_slider_changed)

        # 歌曲进度数字
        self.song_progress_label = QLabel("00:00 / 00:00")

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.song_progress_slider)
        main_layout.addWidget(self.song_progress_label)

        self.setLayout(main_layout)

    def reset_progress(self):
        """重置进度"""
        self.song_progress_slider.setValue(0)
        self.song_progress_slider.setEnabled(True)
        self.song_progress_label.setText("00:00 / 00:00")

    def update_progress(self, position, duration):
        """更新进度"""
        if duration < 0:
            return

        # 更新进度条
        self.song_progress_slider.blockSignals(True)  # 阻塞信号
        self.song_progress_slider.setMaximum(duration)
        self.song_progress_slider.setValue(position)
        self.song_progress_slider.blockSignals(False)

        # 更新时间标签
        self.song_progress_label.setText(f"{ms_to_str(position)} / {ms_to_str(duration)}")

    def on_song_progress_slider_changed(self, value):
        """歌曲进度条值改变"""
        self.songProgressChanged.emit(value)


class BottomPanel(QWidget):
    playlistButtonClicked = Signal()
    songChangedButtonClicked = Signal(SongChanged)
    playOrPausedButtonClicked = Signal()
    platModeChanged = Signal(PlayMode)
    pageImmersiveMode = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.PLAY_MODE_LIST = list(PlayMode)
        self.current_play_mode_index = 0

        self.resize(1200, 800)

        # 设置为固定高度
        self.setMinimumHeight(100)
        self.setMaximumHeight(100)

        left_layout = QHBoxLayout()
        # 当前播放歌曲封面
        self.current_song_cover = QLabel()
        self.current_song_cover.setFixedWidth(60)  # 设置封面为固定宽度
        self.current_song_cover.setPixmap(create_pixmap_from_bytes('', (60, 60)))
        # 当前歌曲标题
        current_song_info = QVBoxLayout()
        current_song_info.setContentsMargins(0, 20, 0, 20)
        title_font = QFont("Microsoft YaHei", 13)
        title_font.setBold(True)
        self.current_song_title = QLabel("歌曲标题")
        self.current_song_title.setWordWrap(True)
        self.current_song_title.setFont(title_font)
        self.current_song_title.setStyleSheet("color: #4a4c57")
        self.current_song_artist = QLabel("歌手")
        self.current_song_artist.setWordWrap(True)
        artist_font = QFont("Microsoft YaHei")
        artist_font.setBold(True)
        self.current_song_artist.setFont(artist_font)
        self.current_song_artist.setStyleSheet("color: #7b7b8b")
        current_song_info.addWidget(self.current_song_title)
        current_song_info.addWidget(self.current_song_artist)
        left_layout.addWidget(self.current_song_cover)
        left_layout.addLayout(current_song_info)
        left_layout.addStretch(1)

        center_layout = QHBoxLayout()
        # 选择歌曲模式下拉框
        self.play_mode_button = PlayModeButton(self)
        self.play_mode_button.clicked.connect(self.on_play_mode_changed)
        # 上一首按钮
        self.prev_song_button = NextOrPrevButton(SongChanged.PREV, self)
        self.prev_song_button.setToolTip("上一首")
        self.prev_song_button.clicked.connect(self.on_prev_song_button_clicked)
        # 下一首按钮
        self.next_song_button = NextOrPrevButton(SongChanged.NEXT, self)
        self.next_song_button.setToolTip("下一首")
        self.next_song_button.clicked.connect(self.on_next_song_button_clicked)
        # 播放/暂停按钮
        self.play_or_paused_button = PlayPausedButton(self)
        self.play_or_paused_button.clicked.connect(self.on_play_or_paused)
        # 展示播放列表按钮
        self.show_playlist_button = PlayListButton(self)
        self.show_playlist_button.setToolTip("播放列表")
        self.show_playlist_button.clicked.connect(self.on_playlist_button_clicked)
        center_layout.addWidget(self.play_mode_button)
        center_layout.addWidget(self.prev_song_button)
        center_layout.addWidget(self.play_or_paused_button)
        center_layout.addWidget(self.next_song_button)
        center_layout.addWidget(self.show_playlist_button)

        right_layout = QHBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        # 沉浸模式按钮
        self.immersive_mode_button = ImmersiveModeButton(self)
        self.immersive_mode_button.clicked.connect(self.pageImmersiveMode)
        right_layout.addStretch(1)
        right_layout.addWidget(self.immersive_mode_button)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(9, 0, 9, 0)

        # main_layout.addWidget(self.current_song_cover)
        # main_layout.addLayout(current_song_info)
        # main_layout.addWidget(self.play_mode_button)
        # main_layout.addWidget(self.prev_song_button)
        # main_layout.addWidget(self.play_or_paused_button)
        # main_layout.addWidget(self.next_song_button)
        # main_layout.addWidget(self.show_playlist_button)
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(center_layout, 2)
        main_layout.addLayout(right_layout, 1)

        self.setLayout(main_layout)

        self.setObjectName("bottomPanel")
        self.setAutoFillBackground(True)
        self.setStyleSheet("""
            #bottomPanel{
                background-color: #cbcfea;
            }
        """)

    def set_current_song(self, song_item: SongItem):
        """设置当前播放音乐"""
        self.current_song_cover.setPixmap(create_pixmap_from_bytes(song_item.cover_bytes, (60, 60)))
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

    def on_play_mode_changed(self):
        """歌曲播放模式改变"""
        self.set_current_play_mode((self.current_play_mode_index + 1) % len(self.PLAY_MODE_LIST), is_changing=True)


class PlayPausedButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._normal_color = "#9092dc"  # 默认颜色
        self._hover_color = "#6467ce"  # 悬停颜色

        # 播放图标和暂停图标
        self.playing_icon = create_svg_icon(playing_icon, "#e5e5e5", 20)
        self.paused_icon = create_svg_icon(paused_icon, "#e5e5e5", 30)

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

        if btn_type == SongChanged.NEXT:
            self.btn_icon = create_svg_icon(next_song_icon, self.normal_color, 30)
            self.hover_icon = create_svg_icon(next_song_icon, self.hover_color, 30)
        else:
            self.btn_icon = create_svg_icon(prev_song_icon, self.normal_color, 30)
            self.hover_icon = create_svg_icon(prev_song_icon, self.hover_color, 30)

        # 设置按钮为圆形
        self.setIcon(self.btn_icon)


class PlayListButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.btn_icon = create_svg_icon(play_list_icon, self.normal_color, 30)
        self.hover_icon = create_svg_icon(play_list_icon, self.hover_color, 30)
        self.setIcon(self.btn_icon)


class PlayModeButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.order_icon = create_svg_icon(order_play_mode_icon, self.normal_color, 30)
        self.order_icon_hover = create_svg_icon(order_play_mode_icon, self.hover_color, 30)
        self.random_icon = create_svg_icon(random_play_mode_icon, self.normal_color, 30)
        self.random_icon_hover = create_svg_icon(random_play_mode_icon, self.hover_color, 30)
        self.repeat_icon = create_svg_icon(repeat_play_mode_icon, self.normal_color, 30)
        self.repeat_icon_hover = create_svg_icon(repeat_play_mode_icon, self.hover_color, 30)

        self.btn_icon = self.order_icon
        self.hover_icon = self.order_icon_hover
        self.setIcon(self.btn_icon)
        self.setToolTip("顺序播放")

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

        self.btn_icon = create_svg_icon(immersive_mode_icon, self.normal_color, 30)
        self.hover_icon = create_svg_icon(immersive_mode_icon, self.hover_color, 30)

        self.setIcon(self.btn_icon)


if __name__ == "__main__":
    app = QApplication([])
    bottom = BottomPanel()
    bottom.show()
    app.exec()
