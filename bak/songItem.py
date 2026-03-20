from PySide6.QtGui import QImage, QPixmap, QPainter, QPainterPath, QColor
from PySide6.QtWidgets import QLabel, QHBoxLayout, QWidget
from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve

from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from uitls.utils import secs_to_str


def get_tag(audio, keys):
    """从不同格式中尝试获取标签值"""
    for key in keys:
        if key in audio:
            val = audio[key]
            if isinstance(val, list):
                return str(val[0]) if val else ""
            return str(val)
    return ""


def load_meta_data(music_file_path):
    """获取音乐文件的元数据（标题、歌手、专辑、时长、封面）"""
    audio = File(music_file_path)
    duration = secs_to_str(audio.info.length)

    # 获取通用信息
    title = get_tag(audio, ['title', 'TIT2', '\xa9nam']) or "未知标题"  # 标题
    artist = get_tag(audio, ['artist', 'TPE1', '\xa9ART']) or "未知歌手"  # 歌手
    album = get_tag(audio, ['album', 'TALB', '\xa9alb']) or "未知专辑"  # 专辑

    # 提取封面(Bytes)
    cover_data = None
    if isinstance(audio, MP3):  # MP3文件
        if audio.tags and "APIC:" in audio.tags:
            apic = audio.tags.getall("APIC")[0]
            cover_data = apic.data
    elif isinstance(audio, FLAC):  # FLAC文件
        if audio.pictures:
            cover_data = audio.pictures[0].data
    elif isinstance(audio, MP4):  # MP4文件
        if 'covr' in audio.tags:
            cover_data = audio['covr'][0]

    return title, artist, album, duration, cover_data


def create_pixmap_from_bytes(image_bytes, pixmap_size):
    """从图片bytes格式创建pixmap"""
    if image_bytes:
        pixmap = QPixmap()
        pixmap.loadFromData(image_bytes)
        pixmap = pixmap.scaled(pixmap_size[0], pixmap_size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    else:
        pixmap = QPixmap(pixmap_size[0], pixmap_size[1])
        pixmap.fill(Qt.GlobalColor.gray)

    pixmap = create_rounded_pixmap(pixmap)

    return pixmap


def create_rounded_pixmap(original_pixmap, radius=10):
    """创建带圆角的pixmap"""
    w, h = original_pixmap.width(), original_pixmap.height()
    # 创建更大的画布（容纳阴影）
    canvas = QImage(w, h, QImage.Format_ARGB32)
    canvas.fill(Qt.transparent)

    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.Antialiasing)

    # 画圆角图片
    path = QPainterPath()
    path.addRoundedRect(0, 0, w, h, radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, original_pixmap)

    painter.end()
    return QPixmap.fromImage(canvas)


class SongItem:
    def __init__(self, music_file_path, index):
        self.index = index
        self.music_file_path = music_file_path
        self.title, self.artist, self.album, self.duration, self.cover_bytes = load_meta_data(music_file_path)


class SongItemWidget(QWidget):

    def __init__(self, song_item: SongItem):
        super().__init__()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._background_color = QColor("#e9ebfa")

        self._animation = QPropertyAnimation(self, b"background_color")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)


        self.setFixedHeight(85)  # 设置高度为80px

        self.songItem = song_item

        # 歌曲标数
        self.index_label = QLabel(str(self.songItem.index))
        self.index_label.setWordWrap(True)
        self.index_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 歌曲时长
        self.duration_label = QLabel(self.songItem.duration)
        self.duration_label.setWordWrap(True)
        # self.duration_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        # 歌曲标题
        self.title_label = QLabel(self.songItem.title)
        self.title_label.setWordWrap(True)
        # self.duration_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        # 歌曲歌手
        self.artist_label = QLabel(self.songItem.artist)
        self.artist_label.setWordWrap(True)
        # 歌曲专辑
        self.album_label = QLabel(self.songItem.album)
        self.album_label.setWordWrap(True)
        # 歌曲封面
        self.cover_label = QLabel()
        self.cover_label.setPixmap(create_pixmap_from_bytes(song_item.cover_bytes, (60, 60)))

        main_layout = QHBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # 垂直居中显示
        main_layout.setContentsMargins(0, 10, 0, 10)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.index_label, 2)
        main_layout.addWidget(self.cover_label, 3)
        main_layout.addWidget(self.title_label, 10)
        main_layout.addWidget(self.artist_label, 9)
        main_layout.addWidget(self.album_label, 14)
        main_layout.addWidget(self.duration_label, 3)

        self.is_selected = False
        self.setStyleSheet("""
                background-color: #e9ebfa;
                color: #4c4e5d;
                font-weight: bold;
                border: none;
            """)

    @Property(QColor)
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color):
        self._background_color = color
        self.update_style()

    def update_style(self):
        self.setStyleSheet(f"""
            background-color: {self._background_color.name()};
            color: #4c4e5d;
            font-weight: bold;
            border: none;
        """)

    def animation_to_color(self, color: QColor):
        if self._animation.state() == QPropertyAnimation.State.Running:
            self._animation.setEndValue(color)
        else:
            self._animation.setStartValue(self._background_color)
            self._animation.setEndValue(color)
            self._animation.start()

    def set_selected(self):
        self.is_selected = True
        # self._background_color = QColor("#adb2e9")
        # self.update_style()
        self.animation_to_color(QColor("#adb2e9"))

    def set_unselected(self):
        self.is_selected = False
        # self._background_color = QColor("#e9ebfa")
        # self.update_style()
        self.animation_to_color(QColor("#e9ebfa"))

    def enterEvent(self, event, /):
        if not self.is_selected:
            self.animation_to_color(QColor("#d9dbf2"))

    def leaveEvent(self, event, /):
        if not self.is_selected:
            self.animation_to_color(QColor("#e9ebfa"))
