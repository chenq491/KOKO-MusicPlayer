import io

import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QPixmap, QImage
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsBlurEffect

from bak.songItem import SongItem, create_pixmap_from_bytes
from uitls.audioLoader import AudioLoader
from uitls.utils import fft_from_chunk
from PIL import Image, ImageFilter


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
        qim = QImage(blurred.tobytes(), blurred.width, blurred.height, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qim)
        return pixmap


class ImmersiveModeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 音乐ffm数据
        self.audio = None
        self.sample_rate = None
        self.pos = 0
        self.chunk_size = 2048

        # self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # self.setObjectName("ImmersiveModeWidget")
        # self.setStyleSheet("""
        #     #ImmersiveModeWidget{
        #         border: 2px solid #5c9ded;
        #         border-radius: 10px;
        #         background-color: white;
        #     }
        # """)

        # =========背景层===========
        self._background_initialized = False
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(False)  # 自动缩放
        # 应用模糊效果
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(200)  # 模糊半径（越大越模糊）
        blur_effect.setBlurHints(QGraphicsBlurEffect.BlurHint.QualityHint)
        self.bg_label.setGraphicsEffect(blur_effect)
        self.bg_pixmap = QPixmap()

        # ==========内容层===========
        self.content_widget = QWidget()
        self.content_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # 频谱控件
        self.spectrum_widget = SpectrumWidget(self)
        # 封面控件
        self.cover_display_widget = CoverDisplayWidget(self)

        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_layout.addWidget(self.cover_display_widget)
        self.content_layout.addWidget(self.spectrum_widget)

        # 布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.content_widget)

    def resizeEvent(self, event, /):
        # 每次 resize 都更新背景尺寸

        self.bg_label.resize(self.size())
        self.bg_pixmap = self.bg_pixmap.scaled(
            self.bg_label.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        self.bg_label.setPixmap(self.bg_pixmap)
        self.content_widget.resize(self.size())
        super().resizeEvent(event)

    def showEvent(self, event, /):
        # 第一次 显示 时初始化背景
        if not self._background_initialized:
            self.bg_label.setGeometry(self.rect())
            self._background_initialized = True

        self.bg_label.setPixmap(self.bg_pixmap)

        super().showEvent(event)

    def load_audio(self, song_item: SongItem):
        """加载音频数据"""

        # TODO 可能需要优化数据操作
        self.cover_display_widget.cover.setPixmap(create_pixmap_from_bytes(song_item.cover_bytes, (300, 300)))
        self.bg_pixmap = blur_image(song_item.cover_bytes)
        if self._background_initialized:
            self.bg_pixmap = self.bg_pixmap.scaled(
                self.bg_label.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.bg_label.setPixmap(self.bg_pixmap)

        def load_success(result):
            self.audio = result["audio"]
            self.sample_rate = result["sample_rate"]
            self.pos = 0
            loader.deleteLater()

        loader = AudioLoader()
        loader.finished.connect(load_success)
        loader.load_audio_ffm(song_item)

    def update_spectrum_from_position(self, pos_ms):
        """更新频谱图
        pos_ms: 当前播放位置（毫秒）
        """
        if self.audio is None or self.sample_rate is None or pos_ms < 0:
            return

        # pos转换为采样点索引
        pos_sample = int(pos_ms / 1000.0 * self.sample_rate)

        start = pos_sample
        end = start + self.chunk_size
        if end > len(self.audio):
            # 不够的补零
            chunk = np.zeros(self.chunk_size, dtype=np.float32)
            valid = self.audio[start:]
            chunk[:len(valid)] = valid
        else:
            chunk = self.audio[start:end]

        binned = fft_from_chunk(chunk, self.spectrum_widget.column_num)
        self.spectrum_widget.update_spectrum(binned)


class CoverDisplayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(500)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # self.setStyleSheet("border: 2px solid #5c9ded;")

        self.cover = QLabel()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        main_layout.addWidget(self.cover)

        self.setLayout(main_layout)


class SpectrumWidget(QWidget):
    """频谱跳动组件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumHeight(150)

        self.column_num = 128

        self.current_spectrum = np.zeros(self.column_num, dtype=np.float32)  # 当前显示值
        self.target_spectrum = np.zeros(self.column_num, dtype=np.float32)  # 目标值

        self.decay_rate = 0.2  # 衰减速率（越小越慢）

        self.timer = QTimer()
        self.timer.start(20)
        self.timer.timeout.connect(self.update)

        self.setStyleSheet("border: 2px solid #fff;")

    def update_spectrum(self, data):
        """
        更新视图数据
        :param: data 归一化后的频谱数组（0~1），长度为 self.column_num
        """
        self.target_spectrum = data

        self.update()  # 触发重绘

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 启用抗锯齿
        painter.setPen(Qt.PenStyle.NoPen)  # 只填充颜色，不绘制边框

        w, h = self.width(), self.height()
        bar_count = len(self.target_spectrum)
        bar_w = max(2, w // bar_count)  # 留出间隙

        total_bar_width = bar_count * bar_w
        left_margin = max(0, (w - total_bar_width) // 2)

        # 更新频谱（带衰减和平滑）
        for i in range(bar_count):
            target = self.target_spectrum[i]
            current = self.current_spectrum[i]

            current += (target - current) * self.decay_rate

            # 上升快，下降慢
            # if target > current:
            #     current += (target - current) * 0.9
            # else:
            #     current -= (current - target) * self.decay_rate

            self.current_spectrum[i] = np.clip(current, 0, 1)

        # 绘制柱子
        for i, mag in enumerate(self.current_spectrum):
            bar_h = int(mag * h * 0.9)
            x = left_margin + i * bar_w
            y = h - bar_h

            # 垂直渐变
            gradient = QLinearGradient(x, h, x, y)
            gradient.setColorAt(0.0, QColor(100, 200, 255, 220))  # 底部
            gradient.setColorAt(1.0, QColor(30, 120, 200, 200))  # 顶部
            painter.setBrush(gradient)

            # 圆角矩形
            radius = min(bar_w // 2, 6)
            painter.drawRoundedRect(x, y, bar_w - 1, bar_h, radius, radius)
