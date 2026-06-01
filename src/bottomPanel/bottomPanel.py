import sys
from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from constant import COVER_SiZE, PlayMode, SongChanged
from singleton.themeManager import theme_manager
from songList.songItem import SongItem
from styleTemplate.styleFontLabel import StyleFontLabel
from uitls.path import get_file_path
from uitls.utils import ms_to_str

sys.path.append(str(Path(__file__).parent))
from buttons import (
    ImmersiveModeButton,
    LocationButton,
    NextOrPrevButton,
    PlayListButton,
    PlayModeButton,
    PlayPausedButton,
)
from progressSlider import ProgressSlider


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
        self.setObjectName("bottomPanel")

        # 歌曲进度条
        self.progress_slider = ProgressSlider()

        # 当前播放歌曲封面
        self.current_song_cover = QLabel()
        self.current_song_cover.setFixedWidth(60)  # 设置封面为固定宽度
        self.current_song_cover.setPixmap(
            QPixmap(str(get_file_path("src", "assets", "default_cover.png"))).scaled(
                COVER_SiZE,
                COVER_SiZE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

        # 当前播放歌曲标题
        self.current_song_title = StyleFontLabel(
            "歌曲标题", font_size=11, color=theme_manager.current.text_bold
        )
        self.current_song_title.setWordWrap(True)
        self.current_song_artist = StyleFontLabel(
            "歌手", font_size=10, color=theme_manager.current.text_light
        )
        self.current_song_artist.setWordWrap(True)

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

        # 沉浸模式按钮
        self.immersive_mode_button = ImmersiveModeButton(self)
        # 定位按钮
        self.location_button = LocationButton(self)
        # 歌曲时间信息
        self.time_label = StyleFontLabel(
            "00:00 / 00:00", font_size=11, color=theme_manager.current.text_normal
        )

        self.init_ui()
        self.init_style()
        self.bind()

    def init_ui(self):
        """初始化布局"""
        """
        左侧布局
        """
        # 当前歌曲标题
        current_song_info = QVBoxLayout()
        current_song_info.setContentsMargins(0, 0, 0, 0)
        current_song_info.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        current_song_info.addWidget(self.current_song_title)
        current_song_info.addWidget(self.current_song_artist)

        left_layout = QHBoxLayout()
        left_layout.addWidget(self.current_song_cover)
        left_layout.addLayout(current_song_info)
        left_layout.addStretch(1)

        """中间布局"""
        center_layout = QHBoxLayout()
        center_layout.addWidget(self.play_mode_button)
        center_layout.addWidget(self.prev_song_button)
        center_layout.addWidget(self.play_or_paused_button)
        center_layout.addWidget(self.next_song_button)
        center_layout.addWidget(self.show_playlist_button)

        """
        右侧布局
        """
        right_layout = QHBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addStretch(3)
        right_layout.addWidget(self.time_label)
        right_layout.addStretch(1)
        right_layout.addWidget(self.location_button)
        right_layout.addWidget(self.immersive_mode_button)

        """
        主要布局
        """
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(9, 12, 9, 0)
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(center_layout, 2)
        main_layout.addLayout(right_layout, 1)

        """
        添加上进度条
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.progress_slider)
        layout.addLayout(main_layout)

    def init_style(self):
        """初始化样式"""
        self.setAutoFillBackground(True)
        self.setStyleSheet("""
                   #bottomPanel{
                       background: transparent;
                   }
               """)

    def bind(self):
        """绑定事件"""
        self.play_mode_button.clicked.connect(self.on_play_mode_changed)  # 播放模式切换
        self.prev_song_button.clicked.connect(
            self.on_prev_song_button_clicked
        )  # 上一首
        self.next_song_button.clicked.connect(
            self.on_next_song_button_clicked
        )  # 下一首
        self.play_or_paused_button.clicked.connect(self.on_play_or_paused)  # 播放/暂停
        self.show_playlist_button.clicked.connect(
            self.on_playlist_button_clicked
        )  # 展示音乐列表
        self.immersive_mode_button.clicked.connect(
            self.pageImmersiveMode
        )  # 进入沉浸模式
        self.location_button.clicked.connect(
            self.on_location_button_clicked
        )  # 定位到当前音乐
        self.progress_slider.valueChanged.connect(
            self.on_progress_slider_changed
        )  # 歌曲进度条拖动
        theme_manager.themeChanged.connect(self.update_text_color)

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
        self.set_current_play_mode(
            (self.current_play_mode_index + 1) % len(self.PLAY_MODE_LIST),
            is_changing=True,
        )

    @Slot()
    def on_location_button_clicked(self):
        """定位到当前歌曲"""
        self.location.emit()

    @Slot()
    def on_progress_slider_changed(self, value):
        """歌曲进度改变"""
        self.songProgressChanged.emit(value)

    def update_text_color(self):
        self.current_song_title.set_color(theme_manager.current.text_bold)
        self.current_song_artist.set_color(theme_manager.current.text_light)
        self.time_label.set_color(theme_manager.current.text_normal)


if __name__ == "__main__":
    app = QApplication([])
    bottom = BottomPanel()
    bottom.show()
    app.exec()
