import io

import miniaudio
import numpy as np
from PySide6.QtCore import Signal, QThread, Qt
from PySide6.QtGui import QPixmap, QImage
from PIL import Image, ImageFilter, ImageEnhance

from songList.songItem import load_cover_bytes
from uitls.utils import draw_rounded_pixmap


def create_pixmap_from_bytes(image_bytes, pixmap_size):
    """从图片bytes格式创建pixmap"""
    if image_bytes:
        pixmap = QPixmap()
        pixmap.loadFromData(image_bytes)
        pixmap = pixmap.scaled(pixmap_size[0], pixmap_size[1], Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
    else:
        pixmap = QPixmap(pixmap_size[0], pixmap_size[1])
        pixmap.fill(Qt.GlobalColor.gray)

    pixmap = draw_rounded_pixmap(pixmap)

    return pixmap


def blur_image(image_bytes, radius=30):
    if image_bytes is None:
        pixmap = QPixmap(60, 60)
        pixmap.fill(Qt.GlobalColor.gray)
        return pixmap
    else:
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        blurred = image.filter(ImageFilter.GaussianBlur(radius))

        enhancer = ImageEnhance.Brightness(blurred)
        enhanced = enhancer.enhance(0.5)

        qim = QImage(enhanced.tobytes(), blurred.width, blurred.height, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qim)
        return pixmap


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

        result = {}

        # 加载封面数据
        cover_bytes = load_cover_bytes(path)
        cover_pixmap = create_pixmap_from_bytes(cover_bytes, (300, 300))
        bg_pixmap = blur_image(cover_bytes)

        result["cover"] = cover_pixmap
        result["bg"] = bg_pixmap

        # 加载频谱数据
        with open(path, 'rb') as f:
            data = f.read()
        try:
            # 使用 miniaudio 解码为 32-bit float, 单声道, 22050 Hz（可自定义）
            decoded = miniaudio.decode(data, output_format=miniaudio.SampleFormat.FLOAT32, nchannels=1,
                                       sample_rate=22050)

            result["audio"] = np.frombuffer(decoded.samples, dtype=np.float32)
            result["sample_rate"] = decoded.sample_rate
        finally:
            self.dataLoaded.emit(result)
