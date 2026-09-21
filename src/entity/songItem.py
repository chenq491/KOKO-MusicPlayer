from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from constant import COVER_SiZE
from utils.path import get_file_path
from utils.utils import draw_rounded_pixmap
from utils.music_parser import load_meta_data


class SongItem:
    default = None

    def __init__(self, music_file_path, index):
        self.index = index
        self.music_file_path = music_file_path
        self.title = None
        self.artist = None
        self.album = None
        self.duration = None
        self.cover = None

        self.load_data()

    def load_data(self):
        # TODO 可以优化cover_bytes项
        self.title, self.artist, self.album, self.duration, cover_bytes = (
            load_meta_data(self.music_file_path)
        )
        self.cover = QPixmap()
        self.cover.loadFromData(cover_bytes)
        if self.cover.isNull():
            if self.default is None:
                self.cover.load(
                    str(get_file_path("src", "assets", "default_cover.png"))
                )
                self.default = self.cover
            else:
                self.cover = self.default
        self.cover = self.cover.scaled(
            COVER_SiZE,
            COVER_SiZE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.cover = draw_rounded_pixmap(self.cover)
