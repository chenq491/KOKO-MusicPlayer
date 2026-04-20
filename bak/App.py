import sys
from pathlib import Path

from progressDisplay import ProgressDisplay
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, QUrl, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from songItem import SongItem
from songListPage import SongListPage

from bottomPanel.bottomPanel import BottomPanel
from components.message import show_message
from constant import MUSIC_SUFFIX, PlayMode, SongChanged
from immersiveModePage import ImmersiveModeWidget
from settingPage import SettingPage
from singleton.config import Config
from singleton.playListManager import PlayListManager, PlayListPanel
from titleBar import TitleBar


class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.animation = None

        # 播放音乐工具
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)

        # 播放列表
        self.playlist = PlayListManager()
        self.song_click_changed = False  # 是否是用户手动点击切换歌曲

        self.setWindowTitle("音乐播放器")
        self.resize(1200, 800)

        # 👇 关键：隐藏系统标题栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 可选：支持透明背景

        # # 加载.ui文件
        # ui_file = QFile("main.ui")
        # ui_file.open(QFile.ReadOnly)
        # loader = QUiLoader()
        # center_widget = loader.load(ui_file, self)
        # ui_file.close()

        self.title_bar = TitleBar(self)

        # 歌曲列表页面
        self.song_list_widget = SongListPage(self)

        # 设置页面
        self.settings_widget = SettingPage(self)

        # 沉浸模式页面
        self.immersive_mode_widget = ImmersiveModeWidget(self)

        # 中心可切换页面
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(self.song_list_widget)
        self.stacked_widget.addWidget(self.settings_widget)
        self.stacked_widget.addWidget(self.immersive_mode_widget)

        # 进度展示
        self.progress_display = ProgressDisplay(self)

        # 底部面板
        self.bottom_panel = BottomPanel(self)

        center_widget = QWidget()
        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        center_layout.addWidget(self.title_bar, 0)
        center_layout.addWidget(self.stacked_widget, 14)
        center_layout.addWidget(self.progress_display, 0)
        center_layout.addWidget(self.bottom_panel, 0)
        center_widget.setLayout(center_layout)

        # 设置为主窗口内容
        self.setCentralWidget(center_widget)

        # 定时器，用于更新进度条
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_timeout)

        # 播放列表展示面板
        self.playlist_panel = PlayListPanel(self.playlist, self)
        self.playlist_panel.update_geometry()

        # 样式
        self.setObjectName("mainWindow")
        self.setStyleSheet("""
                            #mainWindow{
                                background-color: #dfe0f5;
                                border: none;
                            }
                        """)

        self.bind()
        self.load_data()

    def bind(self):
        """绑定事件"""
        self.title_bar.pageConfig.connect(
            lambda: self.stacked_widget.setCurrentIndex(1)
        )  # 切换到设置页面
        self.title_bar.pageHome.connect(
            lambda: self.stacked_widget.setCurrentIndex(0)
        )  # 切换到主页页面

        self.media_player.errorOccurred.connect(self.on_media_player_error)  # 播放失败
        self.media_player.playbackStateChanged.connect(
            self.on_playback_state_changed
        )  # 播放状态改变

        self.song_list_widget.songItemDoubleClicked.connect(
            self.on_song_list_item_double_clicked
        )  # 双击音乐列表歌曲
        self.song_list_widget.refresh.connect(
            lambda: self.update_music_list(Config.get_value("music_dir"))
        )

        self.settings_widget.musicDirSelected.connect(
            self.on_music_dir_selected
        )  # 选择音乐文件夹
        self.settings_widget.volumeChanged.connect(self.on_volume_changed)  # 音量改变

        self.progress_display.songProgressChanged.connect(
            self.on_song_progress_changed
        )  # 歌曲进度条改变

        self.bottom_panel.songChangedButtonClicked.connect(
            self.on_song_changed_button_clicked
        )  # 切换歌曲
        self.bottom_panel.playOrPausedButtonClicked.connect(
            self.on_play_or_paused
        )  # 播放/暂停歌曲
        self.bottom_panel.platModeChanged.connect(
            self.on_play_mode_changed
        )  # 播放模式切换
        self.bottom_panel.playlistButtonClicked.connect(
            self.playlist_panel.show_or_hidden
        )  # 点击播放列表按钮
        self.bottom_panel.pageImmersiveMode.connect(
            lambda: self.stacked_widget.setCurrentIndex(2)
        )

        self.playlist_panel.selectMusic.connect(
            self.on_playlist_select_music
        )  # 播放列表切换歌曲

    def load_data(self):
        """加载设置数据"""

        def set_position():
            self.media_player.setPosition(play_progress["position"])
            self.update_music_progress()

        # 加载配置里的音乐文件夹里的音乐
        if Config.get_value("music_dir") != "":
            self.update_music_list(Config.get_value("music_dir"))
            if Config.get_value(["startup_setting", "keep_last_progress"]) == 0:
                # 加载上一次播放进度
                play_progress = Config.get_value("play_progress")
                self.playlist.playlist = play_progress["play_list"]
                self.bottom_panel.set_current_play_mode(play_progress["play_mode"])
                if self.playlist.playlist:
                    self.playlist.current_play_index = play_progress[
                        "current_play_index"
                    ]
                    song_item = self.playlist.get_current_song_item()
                    self.play_music(song_item)
                    self.media_player.pause()
                    QTimer.singleShot(50, set_position)

    def load_music_list_in_dir(self, music_dir):
        if not music_dir:  # 确保文件夹存在
            raise FileNotFoundError("文件夹不存在！")

        folder_path = Path(music_dir)
        if not folder_path.is_dir():  # 确保为文件夹
            raise Exception("该目录不为文件夹！")

        # 获取歌曲文件路径
        files = []
        try:
            files = [
                f
                for f in folder_path.iterdir()
                if f.is_file() and f.suffix.lower() in MUSIC_SUFFIX
            ]
        except Exception as e:
            print(f"ERROR: 读取文件夹出错：{e}")

        song_item_list = []
        idx = 1
        for f in files:
            song_item = SongItem(str(f), idx)
            song_item_list.append(song_item)
            idx += 1

        return song_item_list

    def play_music(self, song_item: SongItem):
        """播放音乐"""
        # 设置当前歌曲到列表
        self.song_list_widget.set_current(self.playlist.current_song_index)
        self.playlist_panel.set_current()

        # 更新底部面板
        self.progress_display.reset_progress()
        self.bottom_panel.set_current_song(song_item)

        # 播放歌曲
        self.media_player.setSource(QUrl.fromLocalFile(song_item.music_file_path))
        self.media_player.play()

        # 推迟500ms再加载音乐ffm数据，防止动画卡顿
        QTimer.singleShot(500, lambda: self.immersive_mode_widget.load_audio(song_item))

    def update_music_progress(self):
        """更新歌曲进度"""
        duration = self.media_player.duration()  # 歌曲总时长
        position = self.media_player.position()  # 当前歌曲进度

        # 歌曲进度视图更新
        self.progress_display.update_progress(position, duration)

        # 沉浸模式频谱图更新
        self.immersive_mode_widget.update_spectrum_from_position(position)

    def update_music_list(self, music_dir: str):
        """更新音乐列表"""
        music_list = self.load_music_list_in_dir(music_dir)
        self.playlist.song_list = music_list
        self.song_list_widget.show_music_list(music_list)
        # 若存在当前播放音乐，则跳转并高亮显示
        if self.playlist.current_play_index != -1:
            self.song_list_widget.jump2current(self.playlist.current_song_index)
        # 如果存在播放列表，则更新它
        if self.playlist.playlist:
            self.playlist.update_playlist(
                self.bottom_panel.get_current_play_mode(is_index=False)
            )

    def close_smooth(self):
        """平滑关闭（淡出）"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()
        self.animation.finished.connect(self.close)  # 动画结束后真正关闭

    def closeEvent(self, event: QCloseEvent):
        """窗口关闭执行操作"""
        if Config.get_value(["startup_setting", "keep_last_progress"]) == 0:
            # 保存播放进度
            play_progress = {
                "play_list": self.playlist.playlist,
                "current_play_index": self.playlist.current_play_index,
                "position": self.media_player.position(),
                "play_mode": self.bottom_panel.get_current_play_mode(),
            }
            Config.save_value("play_progress", play_progress)

    @Slot()
    def on_music_dir_selected(self, music_dir):
        """选择了音乐文件夹"""
        Config.save_value("music_dir", music_dir)
        self.update_music_list(music_dir)

    @Slot()
    def on_song_list_item_double_clicked(self, current_song_index):
        """双击音乐列表中的音乐"""
        # 设置播放列表
        self.playlist.current_song_index = current_song_index
        self.playlist.update_playlist(self.bottom_panel.get_current_play_mode(False))

        # 更新播放列表视图
        self.playlist_panel.set_content()

        # 播放音乐
        if not self.media_player.source().isEmpty():
            self.song_click_changed = True
        self.play_music(self.playlist.get_current_song_item())

    @Slot()
    def on_media_player_error(self, error, error_string):
        """音乐播放失败"""
        print(f"播放错误：{error} - {error_string}")

    @Slot()
    def on_playback_state_changed(self, state):
        """
        歌曲状态发生变化时调用
        :param state: 歌曲状态
        """
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.timer.start(100)  # 100ms更新一次
            self.bottom_panel.update_display(True)
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.timer.stop()
            self.bottom_panel.update_display(False)
        elif state == QMediaPlayer.PlaybackState.StoppedState:
            if self.song_click_changed:
                self.song_click_changed = False
            else:
                self.timer.stop()
                self.playlist.next_song()
                self.song_list_widget.set_current(self.playlist.current_song_index)
                self.play_music(self.playlist.get_current_song_item())

    @Slot()
    def on_timer_timeout(self):
        """歌曲更新"""
        self.update_music_progress()

    @Slot()
    def on_play_or_paused(self):
        """播放或暂停歌曲"""
        if self.media_player.source().isEmpty():
            show_message("请选择歌曲进行播放！", msg_type="warning", parent=self)
            return

        if self.media_player.isPlaying():
            self.media_player.pause()
        else:
            self.media_player.play()

    @Slot()
    def on_song_progress_changed(self, value):
        """改变歌曲进度"""
        self.media_player.setPosition(value)

    @Slot()
    def on_play_mode_changed(self, current_mode: PlayMode):
        """更改播放模式"""
        self.playlist.update_playlist(current_mode)
        show_message(
            "播放模式修改成功，播放列表已更新！", msg_type="success", parent=self
        )

    @Slot()
    def on_song_changed_button_clicked(self, song_changed: SongChanged):
        """下一首歌"""
        if self.playlist.current_play_index == -1:
            return
        self.song_click_changed = True
        if song_changed == SongChanged.NEXT:
            self.playlist.next_song()
        else:
            self.playlist.previous_song()
        self.song_list_widget.set_current(self.playlist.current_song_index)
        self.play_music(self.playlist.get_current_song_item())

    @Slot()
    def on_playlist_select_music(self):
        """播放列表选择音乐"""
        if not self.media_player.source().isEmpty():
            self.song_click_changed = True
        self.song_list_widget.set_current(self.playlist.current_song_index)
        self.play_music(self.playlist.get_current_song_item())

    @Slot()
    def on_page_changed(self, page_index: int):
        """页面切换"""
        self.stacked_widget.setCurrentIndex(page_index)

    @Slot()
    def on_volume_changed(self, new_volume: float):
        """音量改变"""
        self.audio_output.setVolume(new_volume)


if __name__ == "__main__":
    # QApplication.setStyle("Windows")
    Config.init()  # 加载配置

    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec())
