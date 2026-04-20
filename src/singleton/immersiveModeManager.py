import io

import miniaudio
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap

from songList.songItem import SongItem, load_cover_bytes
from uitls.utils import draw_rounded_pixmap


def create_pixmap_from_bytes(image_bytes, pixmap_size) -> QPixmap:
    """从图片bytes格式创建pixmap"""
    if image_bytes:
        pixmap = QPixmap()
        pixmap.loadFromData(image_bytes)
        pixmap = pixmap.scaled(
            pixmap_size[0],
            pixmap_size[1],
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    else:
        pixmap = QPixmap(pixmap_size[0], pixmap_size[1])
        pixmap.fill(Qt.GlobalColor.gray)

    pixmap = draw_rounded_pixmap(pixmap)

    return pixmap


def blur_image(
    image_bytes: bytes, radius: int = 30, brightness_factor: float = 0.5
) -> QPixmap:
    # TODO 优化图片模糊处理
    if image_bytes is None:
        pixmap = QPixmap(60, 60)
        pixmap.fill(Qt.GlobalColor.gray)
        return pixmap
    else:
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        if radius > 0:
            blurred = image.filter(ImageFilter.GaussianBlur(radius))
        else:
            blurred = image

        enhancer = ImageEnhance.Brightness(blurred)
        enhanced = enhancer.enhance(brightness_factor)

        qim = QImage(
            enhanced.tobytes(),
            blurred.width,
            blurred.height,
            QImage.Format.Format_RGBA8888,
        )
        pixmap = QPixmap.fromImage(qim)
        return pixmap


class DataLoader(QObject):
    request_bg_load = Signal(str, int, float)
    request_data_load = Signal(str, int, float)

    bg_loaded = Signal(QPixmap)
    data_loaded = Signal(dict)

    def __init__(self):
        super().__init__()
        self.request_bg_load.connect(self.get_bg)
        self.request_data_load.connect(self.get_full_data)

    @Slot()
    def get_bg(self, path, radius, brightness_factor):
        if not path:
            return

        image_bytes = load_cover_bytes(path)
        bg_pixmap = blur_image(image_bytes, radius, brightness_factor)
        self.bg_loaded.emit(bg_pixmap)

    @Slot()
    def get_full_data(self, path, radius, brightness_factor):
        print(path)
        if not path:
            return

        result = {}

        # 加载封面数据
        try:
            cover_bytes = load_cover_bytes(path)
            cover_pixmap = create_pixmap_from_bytes(cover_bytes, (300, 300))
            bg_pixmap = blur_image(cover_bytes, radius, brightness_factor)

            result["cover"] = cover_pixmap
            result["bg"] = bg_pixmap
        except Exception as e:
            print(f"Cover loading error: {e}")
            # 失败时给个默认图，防止UI报错
            result["cover"] = QPixmap(300, 300)
            result["cover"].fill(Qt.GlobalColor.gray)
            result["bg"] = QPixmap(60, 60)
            result["bg"].fill(Qt.GlobalColor.gray)

        # 加载频谱数据
        with open(path, "rb") as f:
            data = f.read()
        try:
            # 使用 miniaudio 解码为 32-bit float, 单声道, 22050 Hz（可自定义）
            decoded = miniaudio.decode(
                data,
                output_format=miniaudio.SampleFormat.FLOAT32,
                nchannels=1,
                sample_rate=22050,
            )

            result["audio"] = np.frombuffer(decoded.samples, dtype=np.float32)
            result["sample_rate"] = decoded.sample_rate
        finally:
            self.data_loaded.emit(result)


class ImmersiveModeManager(QObject):
    """沉浸模式数据相关管理器"""

    dataLoaded = Signal()
    bg_changed = Signal()

    def __init__(self):
        # 音乐ffm数据, 用于音频显示
        super().__init__()
        self.audio = None
        self.sample_rate = None
        self.pos = 0
        self.chunk_size = 2048

        # 音乐封面数据
        self.bg = None  # 背景模糊图片
        self.cover = None  # 大图封面

        self.bg_brightness_factor = 0.5
        self.bg_blur_radiu = 30

        self.music_path = None

        # 数据加载器
        self.data_loader = DataLoader()
        self.loader_thread = QThread()

        self.data_loader.bg_loaded.connect(self.on_bg_loaded)
        self.data_loader.data_loaded.connect(self.on_data_loaded)

        self.data_loader.moveToThread(self.loader_thread)
        self.loader_thread.start()

    def load_data(self, song_item: SongItem):
        """加载数据"""
        self.music_path = song_item.music_file_path
        self.data_loader.request_data_load.emit(
            self.music_path, self.bg_blur_radiu, self.bg_brightness_factor
        )

    def get_bg_pixmap(self):
        return self.bg

    def bg_lighteness_changed(self, value):
        self.bg_brightness_factor = value
        self.data_loader.request_bg_load.emit(
            self.music_path, self.bg_blur_radiu, self.bg_brightness_factor
        )

    def bg_ambiguity_changed(self, value):
        self.bg_blur_radiu = value
        self.data_loader.request_bg_load.emit(
            self.music_path, self.bg_blur_radiu, self.bg_brightness_factor
        )

    @Slot()
    def on_data_loaded(self, result: dict):
        """数据加载完成后赋值"""
        self.bg = result["bg"]  # QPixmap 类型
        self.cover = result["cover"]  # QPixmap类型

        self.audio = result["audio"]
        self.sample_rate = result["sample_rate"]
        self.pos = 0

        self.dataLoaded.emit()

    @Slot()
    def on_bg_loaded(self, bg: QPixmap):
        self.bg = bg
        self.bg_changed.emit()


immersive_mode_manager = ImmersiveModeManager()
