from PySide6.QtGui import QPixmap


class SongItem:
    def __init__(self, idx, music_file_path, title, artist, album, duration, cover):
        self.idx: int = idx
        self.music_file_path: str = music_file_path  # 音乐文件路径
        self.title: str = title  # 标题
        self.artist: str = artist  # 歌手
        self.album: str = album  # 专辑
        self.duration: str = duration  # 时长
        self.cover: QPixmap = cover  # 封面

    def __repr__(self) -> str:
        return f"SongItem(idx={self.idx}, music_file_path={self.music_file_path}, title={self.title}, artist={self.artist}, album={self.album}, duration={self.duration})\n"

    #     self.get_song_info()
    #     self.get_file_info()
    #
    # def get_song_info(self):
    #     # TODO 可以优化cover_bytes项
    #     self.title, self.artist, self.album, self.duration, cover_bytes = (
    #         get_song_info(self.music_file_path)
    #     )
    #     self.cover = QPixmap()
    #     self.cover.loadFromData(cover_bytes)
    #     if self.cover.isNull():
    #         if self.default is None:
    #             self.cover.load(
    #                 str(get_file_path("src", "assets", "default_cover.png"))
    #             )
    #             self.default = self.cover
    #         else:
    #             self.cover = self.default
    #     self.cover = self.cover.scaled(
    #         COVER_SiZE,
    #         COVER_SiZE,
    #         Qt.AspectRatioMode.KeepAspectRatio,
    #         Qt.TransformationMode.SmoothTransformation,
    #     )
    #     self.cover = draw_rounded_pixmap(self.cover)
    #
    # def get_file_info(self):
    #     stat_info = Path(self.music_file_path).stat()
    #     self.mtime = stat_info.st_mtime
    #     self.size = stat_info.st_size
