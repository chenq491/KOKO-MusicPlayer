from PySide6.QtCore import Slot, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from components.message import show_message


class MediaPlayer:

    def __init__(self):
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)

        self.bind()

    def bind(self):
        """绑定事件"""
        self.media_player.errorOccurred.connect(self.on_media_player_error)  # 播放失败

    def set_position(self, position):
        """设置音乐位置"""
        self.media_player.setPosition(position)

    def get_position(self):
        return self.media_player.position()

    def get_duration(self):
        return self.media_player.duration()

    def pause(self):
        """暂停音乐"""
        self.media_player.pause()

    def play(self):
        self.media_player.play()

    def play_from_path(self, music_file_path):
        """播放音乐"""
        self.media_player.setSource(QUrl.fromLocalFile(music_file_path))
        self.media_player.play()

    def is_empty(self):
        """当前播放是否为空"""
        return self.media_player.source().isEmpty()

    def is_playing(self):
        """当前音乐是否在播放"""
        return self.media_player.isPlaying()

    def play_or_paused(self):
        """播放或暂停歌曲"""
        if media_player.is_empty():
            show_message("请选择歌曲进行播放！", msg_type="warning", parent=self)
            return

        if self.is_playing():
            self.media_player.pause()
        else:
            self.media_player.play()

    def set_volume(self, volume: float):
        self.audio_output.setVolume(volume)

    def get_volume(self):
        return self.audio_output.volume()

    @Slot()
    def on_media_player_error(self, error, error_string):
        """音乐播放失败"""
        print(f"播放错误：{error} - {error_string}")


media_player = MediaPlayer()
