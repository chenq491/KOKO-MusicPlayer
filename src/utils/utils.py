import re
import sys

import numpy as np
from PySide6.QtCore import QByteArray, Qt, QRect
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPainterPath
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication, QLabel
from scipy.fft import rfft

from singleton.themeManager import theme_manager


def ms_to_str(ms: int) -> str:
    """将ms毫秒转为 MM:SS 时间格式"""
    secs = ms // 1000  # 总秒
    mins = secs // 60  # 分钟
    secs = secs % 60
    return f"{mins:02}:{secs:02}"


def secs_to_str(secs: float) -> str:
    """将s秒转为 MM:SS 时间格式"""
    mins = int(secs // 60)
    secs = int(secs % 60)
    return f"{mins:02}:{secs:02}"


def range_loop(start: int, size: int) -> list:
    """
    生成从start开始，大小为size的循环列表
    比如：start=3, size=7, 则生成[3,4,5,6,0,1,2]
    """
    return [x % size for x in range(start, start + size)]


def fft_from_chunk(chunk, bins):
    """FFT频谱转换"""
    N = len(chunk)
    windowed = chunk * np.hanning(N)
    fft_mag = np.abs(rfft(windowed))

    fft_mag = fft_mag / N

    # 降维到指定数量 bins
    # step = len(fft_mag) // bins
    # binned = np.array([
    #     np.mean(fft_mag[i * step:(i + 1) * step])
    #     for i in range(bins)
    # ])

    # 对数降维
    binned = log_bins(fft_mag, bins)

    # 对数 + 归一化
    # binned = np.log10(binned + 1e-9)
    # bmin, bmax = binned.min(), binned.max()
    # if bmax > bmin:
    #     binned = (binned - bmin) / (bmax - bmin)
    # else:
    #     binned = np.zeros_like(binned)

    # 对数+归一化
    binned = 20 * np.log10(binned + 1e-9)

    db_min, db_max = -60, -20
    binned = np.clip(binned, db_min, db_max)
    binned = (binned - db_min) / (db_max - db_min)

    # 频域平滑
    binned = smooth_freq_bins(binned, 5)

    return binned


def log_bins(fft_mag, num_bins):
    """
    频谱对数降维
    :param fft_mag: 原始FFT频谱图
    :param num_bins: 目标频段数
    """
    L = len(fft_mag)
    # 生成对数间隔的索引
    log_index = np.round(np.logspace(0, np.log10(L), num_bins + 1)).astype(int)
    # 确保不越界
    log_index = np.clip(log_index, 0, L - 1)
    # 去重，防止相邻索引相同
    log_index = np.unique(log_index)

    if len(log_index) < 2:
        return np.zeros(num_bins)

    binned = []
    for i in range(len(log_index) - 1):
        start = log_index[i]
        end = log_index[i + 1]
        if end > start:
            binned.append(np.mean(fft_mag[start:end]))
        else:
            binned.append(fft_mag[start])

    return np.array(binned[:num_bins])


def smooth_freq_bins(spectrum, window_size=5):
    """对频谱进行频率平滑"""
    if window_size <= 1:
        return spectrum
    padded = np.pad(spectrum, (window_size // 2, window_size // 2), mode='edge')
    smoothed = np.convolve(padded, np.ones(window_size) / window_size, mode='valid')
    return smoothed


def create_svg_icon(svg_content: str, fill_color: str = None, size: int = 32) -> QIcon:
    """
    从 SVG 字符串创建 QIcon，并可选修改填充颜色
    :param svg_content: 原始 SVG 字符串
    :param fill_color: 要设置的填充颜色，如 "#ff0000" 或 "red"
    :param size: 图标尺寸
    :return: QIcon
    """
    # 如果指定了 fill_color，则替换 fill 属性
    if fill_color:
        # 方法1：简单替换（适用于 fill 是独立属性的情况）
        # 匹配 fill="..." 或 fill='...'
        svg_content = re.sub(
            r'fill\s*=\s*["\'][^"\']*["\']',
            f'fill="{fill_color}"',
            svg_content,
            flags=re.IGNORECASE
        )

        # 如果 SVG 中没有 fill 属性，可以注入 style（更健壮）
        # 但上述方法对大多数图标已足够

    # 使用 QSvgRenderer 渲染为 QPixmap
    renderer = QSvgRenderer(QByteArray(svg_content.encode('utf-8')))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)  # 透明背景
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)


def create_default_cover(size, bg_color="#bdc3c7", note_color="#f891a7"):
    """
    创建默认的无封面图
    :param size: 封面大小
    :param bg_color: 背景颜色
    :param note_color: 音符颜色
    :return: 封面pixmap
    """
    pixmap = QPixmap(*size)
    pixmap.fill(bg_color)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿
    painter.setPen(QColor(note_color))

    font = QFont("Arial", size[0] // 2)
    painter.setFont(font)

    text_rect = QRect(0, 0, size[0], size[1])
    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "♪")
    painter.end()

    return pixmap


def draw_rounded_pixmap(pixmap, radius=10):
    """
    创建带圆角的pixmap
    :param pixmap: 图片
    :param radius: 圆角半径
    :return: 带圆角地pixmap
    """
    if pixmap is None:
        return QPixmap()

    if radius <= 0:
        return pixmap

    w, h = pixmap.width(), pixmap.height()

    max_radio = min(w, h) / 2.0
    if radius > max_radio:
        radius = int(max_radio)

    rounded_pixmap = QPixmap(pixmap.size())
    rounded_pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(rounded_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)  # 开启抗锯齿，边缘更平滑
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)  # 开启图像平滑变换

    # 画圆角图片
    path = QPainterPath()
    path.addRoundedRect(0, 0, w, h, radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pixmap)

    painter.end()
    return rounded_pixmap


def create_style_label(text, font_size=13, bold=True, color=theme_manager.current.text_bold):
    label = QLabel(text)
    font = QFont("Microsoft YaHei", font_size)
    font.setBold(bold)
    label.setFont(font)
    label.setStyleSheet(f"color: {color}")
    return label

if __name__ == "__main__":
    app = QApplication(sys.argv)
    default_cover = create_default_cover((800, 800))
    success = default_cover.save("../assets/default_cover.png")
    print(success)
    sys.exit(0)
