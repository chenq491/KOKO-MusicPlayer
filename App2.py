from PySide6.QtGui import QCloseEvent, QPainter, QColor, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QStackedWidget
)
from PySide6.QtCore import Slot, QUrl, QTimer, Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
import sys

from components.handleLabel import HandleLabel
from singleton.playListManager import PlayListManager
from playListWidget import PlayListPanel
from singleton.config import Config
from constant import PlayMode, SongChanged
from immersiveModePage import ImmersiveModeWidget
from components.message import show_message
from settingPage import SettingPage
from bottomPanel import BottomPanel
from songList.songListPage import SongListPage
from theme import theme_manager
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
        self.song_click_changed = False  # 是否是用户手动点击切换歌曲

        self.setWindowTitle("音乐播放器")
        self.resize(1200, 800)

        # 👇 关键：隐藏系统标题栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 可选：支持透明背景

        self.title_bar = TitleBar(self)

        # 歌曲列表页面
        self.song_list_page = SongListPage(self)

        # 设置页面
        self.settings_widget = SettingPage(self)

        # 沉浸模式页面
        self.immersive_mode_widget = ImmersiveModeWidget(self)

        # 中心可切换页面
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(self.song_list_page)
        self.stacked_widget.addWidget(self.settings_widget)
        self.stacked_widget.addWidget(self.immersive_mode_widget)

        # 底部面板
        self.bottom_panel = BottomPanel(self)

        center_widget = QWidget()
        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        center_layout.addWidget(self.title_bar, 0)
        center_layout.addWidget(self.stacked_widget, 14)
        center_layout.addWidget(self.bottom_panel, 0)
        center_widget.setLayout(center_layout)

        # 设置为主窗口内容
        self.setCentralWidget(center_widget)

        # 定时器，用于更新进度条
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_timeout)

        # 播放列表展示面板
        self.playlist_panel = PlayListPanel(PlayListManager.get_playlist(), self)
        self.playlist_panel.update_geometry()

        self.handle_label = HandleLabel(self)
        self.handle_label.set_geometry(0)

        # 样式
        self.bg_pixmap = QPixmap()
        self.setObjectName("mainWindow")

        self.bind()
        self.load_data()
        self.set_style()

    def bind(self):
        """绑定事件"""
        self.title_bar.pageConfig.connect(lambda: self.on_page_changed(1))  # 切换到设置页面
        self.title_bar.pageHome.connect(lambda: self.on_page_changed(0))  # 切换到主页页面

        self.media_player.errorOccurred.connect(self.on_media_player_error)  # 播放失败
        self.media_player.playbackStateChanged.connect(self.on_playback_state_changed)  # 播放状态改变

        self.song_list_page.songItemDoubleClicked.connect(self.on_music_list_item_double_clicked)

        self.settings_widget.musicDirSelected.connect(self.on_music_dir_selected)  # 选择音乐文件夹
        self.settings_widget.volumeChanged.connect(self.on_volume_changed)  # 音量改变

        self.immersive_mode_widget.backgroundChanged.connect(self.on_background_changed)

        self.bottom_panel.songProgressChanged.connect(self.on_song_progress_changed)  # 歌曲进度条改变
        self.bottom_panel.songChangedButtonClicked.connect(self.on_song_changed_button_clicked)  # 切换歌曲
        self.bottom_panel.playOrPausedButtonClicked.connect(self.on_play_or_paused)  # 播放/暂停歌曲
        self.bottom_panel.platModeChanged.connect(self.on_play_mode_changed)  # 播放模式切换
        self.bottom_panel.playlistButtonClicked.connect(self.playlist_panel.show_or_hidden)  # 点击播放列表按钮
        self.bottom_panel.pageImmersiveMode.connect(lambda: self.on_page_changed(2))
        self.bottom_panel.location.connect(self.on_song_list_location)
        self.bottom_panel.rectChanged.connect(self.on_bottom_panel_rect_changed)

        self.playlist_panel.selectMusic.connect(self.on_playlist_select_music)  # 播放列表切换歌曲

        theme_manager.themeChanged.connect(self.set_style)

    def set_style(self):
        self.setStyleSheet(f"""
            #mainWindow{{
                border: none;
            }}
        """)

    def load_data(self):
        """加载设置数据"""

        def set_position():
            self.media_player.setPosition(play_progress['position'])
            self.update_music_progress()

        # 加载音乐文件夹里的音乐
        if Config.get_value('music_dir') != "":
            self.update_music_list()
            if Config.get_value(['startup_setting', 'keep_last_progress']) == 0:
                # 加载上一次播放进度
                play_progress = Config.get_value('play_progress')
                self.bottom_panel.set_current_play_mode(play_progress['play_mode'])
                if PlayListManager.get_playlist():
                    self.song_list_page.set_current()
                    self.play_music()
                    self.media_player.pause()
                    QTimer.singleShot(20, set_position)

    def play_music(self):
        """播放音乐"""
        song_item = PlayListManager.get_current_song_item()
        # 设置当前歌曲到列表
        self.playlist_panel.set_current()

        # 更新底部面板
        self.bottom_panel.reset_progress()
        self.bottom_panel.set_current_song(song_item)

        # 播放歌曲
        self.media_player.setSource(QUrl.fromLocalFile(song_item.music_file_path))
        self.media_player.play()

        # 加载音乐ffm数据
        self.immersive_mode_widget.load_audio(song_item)

    def update_music_progress(self):
        """更新歌曲进度"""
        duration = self.media_player.duration()  # 歌曲总时长
        position = self.media_player.position()  # 当前歌曲进度

        # 歌曲进度视图更新
        self.bottom_panel.update_progress(position, duration)
        # 沉浸模式频谱图更新
        self.immersive_mode_widget.update_spectrum_from_position(position)

        # 改变手柄位置
        if duration == 0:
            self.handle_label.set_geometry(0)
        else:
            self.handle_label.set_geometry(int((position / duration) * self.width()))

    def update_music_list(self):
        """更新音乐列表"""
        # TODO 查出当前播放的音乐SongItem，找到其对应的新的SongItem，获取其索引值
        # 如果存在播放列表，则更新它
        if PlayListManager.get_playlist():
            PlayListManager.update_playlist(self.bottom_panel.get_current_play_mode(is_index=False))
        # 若存在当前播放音乐，则跳转并高亮显示
        if PlayListManager.get_current_song_index() != -1:
            self.song_list_page.set_current()

        self.song_list_page.show_music_list()  # 0.7s

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
        if Config.get_value(['startup_setting', 'keep_last_progress']) == 0:
            # 保存播放进度
            play_progress = {
                'play_list': PlayListManager.get_playlist(),
                'current_play_index': PlayListManager.get_current_play_index(),
                'position': self.media_player.position(),
                'play_mode': self.bottom_panel.get_current_play_mode()
            }
            Config.save_value("play_progress", play_progress)

    def paintEvent(self, event, /):
        super().paintEvent(event)
        """
        绘制背景
        """
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(theme_manager.current.bg_color_200))
        if not self.bg_pixmap.isNull():
            self.bg_pixmap = self.bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (self.width() - self.bg_pixmap.width()) // 2
            y = (self.height() - self.bg_pixmap.height()) // 2
            painter.drawPixmap(x, y, self.bg_pixmap)

    @Slot()
    def on_music_dir_selected(self, music_dir):
        """选择了音乐文件夹"""
        Config.save_value('music_dir', music_dir)
        PlayListManager.reset()  # 重置播放管理器
        self.update_music_list()

    @Slot()
    def on_music_list_item_double_clicked(self, current_song_index):
        """双击音乐列表中的音乐"""
        # 设置播放列表
        PlayListManager.set_current_song_index(current_song_index)
        PlayListManager.update_playlist(self.bottom_panel.get_current_play_mode(False))

        # 更新播放列表视图
        self.playlist_panel.set_content()

        # 播放音乐
        if not self.media_player.source().isEmpty():
            self.song_click_changed = True
        self.play_music()

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
            self.timer.start(50)  # 100ms更新一次
            self.bottom_panel.update_display(True)
            self.immersive_mode_widget.start()
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.timer.stop()
            self.bottom_panel.update_display(False)
            self.immersive_mode_widget.stop()
        elif state == QMediaPlayer.PlaybackState.StoppedState:
            if self.song_click_changed:
                self.song_click_changed = False
            else:
                self.timer.stop()
                PlayListManager.next_song()
                self.song_list_page.set_current()
                self.play_music()

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
        self.handle_label.set_geometry(int(value / self.media_player.duration() * self.width()))

    @Slot()
    def on_play_mode_changed(self, current_mode: PlayMode):
        """更改播放模式"""
        PlayListManager.update_playlist(current_mode)
        show_message("播放模式修改成功，播放列表已更新！", msg_type="success", parent=self)

    @Slot()
    def on_song_changed_button_clicked(self, song_changed: SongChanged):
        """上/下一首歌"""
        if PlayListManager.get_current_play_index() == -1:
            return
        self.song_click_changed = True
        if song_changed == SongChanged.NEXT:
            PlayListManager.next_song()
        else:
            PlayListManager.previous_song()
        self.song_list_page.set_current()
        self.play_music()

    @Slot()
    def on_playlist_select_music(self):
        """播放列表选择音乐"""
        if not self.media_player.source().isEmpty():
            self.song_click_changed = True
        self.song_list_page.set_current()
        self.play_music()

    @Slot()
    def on_page_changed(self, page_index: int):
        """页面切换"""
        current_index = self.stacked_widget.currentIndex()
        self.stacked_widget.setCurrentIndex(page_index)
        if current_index == 2 and page_index != 2:
            self.bg_pixmap = QPixmap()
            self.update(self.rect())
        elif current_index != 2 and page_index == 2:
            self.update(self.rect())

    @Slot()
    def on_volume_changed(self, new_volume: float):
        """音量改变"""
        self.audio_output.setVolume(new_volume)

    @Slot()
    def on_background_changed(self, bg: QPixmap):
        """主窗口背景改变"""
        if self.stacked_widget.currentIndex() == 2:
            self.bg_pixmap = bg
            self.update(self.rect())

    @Slot()
    def on_song_list_location(self):
        """定位当前歌曲位置"""
        if self.stacked_widget.currentIndex() != 0:
            self.on_page_changed(0)
        self.song_list_page.location()

    @Slot()
    def on_bottom_panel_rect_changed(self):
        self.handle_label.update_bp_rect(self.bottom_panel)
        self.update_music_progress()

if __name__ == "__main__":
    # QApplication.setStyle("Windows")
    app = QApplication(sys.argv)

    Config.init()  # 加载配置
    PlayListManager.init()  # 初始化播放管理器

    player = MusicPlayer()
    player.show()
    sys.exit(app.exec())
