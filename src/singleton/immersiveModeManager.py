from PySide6.QtCore import Slot, Qt, Signal

from songList.songItem import SongItem
from uitls.audioLoader import AudioFFMLoader


class ImmersiveModeManager:
    """沉浸模式数据相关管理器"""
    dataLoaded = Signal()

    def __init__(self):
        # 音乐ffm数据, 用于音频显示
        self.audio = None
        self.sample_rate = None
        self.pos = 0
        self.chunk_size = 2048

        # 音乐封面数据
        self.bg = None  # 背景模糊图片
        self.cover = None  # 大图封面

        # 数据加载线程
        self.loader_thread = AudioFFMLoader()
        self.loader_thread.dataLoaded.connect(self.on_data_loaded)

    def load_data(self, song_item: SongItem):
        """加载数据"""
        self.loader_thread.set_item(song_item)
        self.loader_thread.start()

    @Slot()
    def on_data_loaded(self, result: dict):
        """数据加载完成后赋值"""
        self.bg = result["bg"]  # QPixmap 类型
        self.cover = result["cover"]  # QPixmap类型

        self.audio = result["audio"]
        self.sample_rate = result["sample_rate"]
        self.pos = 0

        self.dataLoaded.emit()


immersive_mode_manager = ImmersiveModeManager()