import miniaudio
import numpy as np
from PySide6.QtCore import Signal, QThread


class AudioFFMLoader(QThread):
    dataLoaded = Signal(dict)

    def __init__(self):
        super().__init__()
        self.song_item = None

    def set_item(self, item):
        self.song_item = item

    def run(self, /):
        path = self.song_item.music_file_path
        if not path:
            return

        with open(path, 'rb') as f:
            data = f.read()

        try:
            # 使用 miniaudio 解码为 32-bit float, 单声道, 22050 Hz（可自定义）
            decoded = miniaudio.decode(data, output_format=miniaudio.SampleFormat.FLOAT32, nchannels=1,
                                       sample_rate=22050)
            result = {
                "audio": np.frombuffer(decoded.samples, dtype=np.float32),
                "sample_rate": decoded.sample_rate
            }
            self.dataLoaded.emit(result)
        except miniaudio.DecodeError as e:
            self.dataLoaded.emit(None)

