import miniaudio
import numpy as np
from PySide6.QtCore import Signal, QObject

from bak.songItem import SongItem


class AudioLoader(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def load_audio_ffm(self, song_item: SongItem):
        path = song_item.music_file_path
        if not path:
            return

        with open(path, 'rb') as f:
            data = f.read()

        try:
            # 使用 miniaudio 解码为 32-bit float, 单声道, 22050 Hz（可自定义）
            decoded = miniaudio.decode(data, output_format=miniaudio.SampleFormat.FLOAT32, nchannels=1,
                                       sample_rate=22050)
            result = {
                "audio" :np.frombuffer(decoded.samples, dtype=np.float32),
                "sample_rate": decoded.sample_rate
            }
            self.finished.emit(result)
        except miniaudio.DecodeError as e:
            self.finished.emit(f"解码失败：{e}")


