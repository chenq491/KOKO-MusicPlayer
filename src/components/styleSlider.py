from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtWidgets import QSlider

from singleton.themeManager import theme_manager


class StyleSlider(QSlider):
    """自定义样式进度条"""

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)

        self.setFixedHeight(30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # 鼠标样式变化

        self.groove_height = 10
        self.groove_rect = QRect(
            self.rect().left() + 20,
            self.rect().top() + ((self.rect().height() - self.groove_height) // 2),
            self.rect().width() - 40,
            self.groove_height
        )

    def get_ratio(self):
        # 计算进度条的宽度
        if self.maximum() == self.minimum():
            progress_ratio = 0.0
        else:
            progress_ratio = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
        return progress_ratio

    def resizeEvent(self, event, /):
        super().resizeEvent(event)
        self.groove_rect = QRect(
            self.rect().left() + 20,
            self.rect().top() + ((self.rect().height() - self.groove_height) // 2),
            self.rect().width() - 40,
            self.groove_height
        )

    def paintEvent(self, ev, /):
        """重写绘画事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        progress_width = int(self.groove_rect.width() * self.get_ratio())
        progress_rect = QRect(
            self.groove_rect.left(),
            self.groove_rect.top(),
            progress_width,
            self.groove_rect.height()
        )

        """
        绘制滑槽
        """
        painter.save()
        # painter.setPen(Qt.PenStyle.NoPen)
        painter.setPen(QPen(QColor(theme_manager.current.slider_bg), 2))  # 边框
        painter.setBrush(QBrush(QColor(theme_manager.current.slider_bg)))  # 背景
        painter.drawRoundedRect(
            self.groove_rect, 5, 5
        )

        # 绘制滑槽进度
        painter.setBrush(QBrush(QColor(theme_manager.current.slider_progress)))
        painter.drawRoundedRect(
            progress_rect,
            5 if progress_width > 0 else 0,  # 有进度才显示圆角
            5 if progress_width > 0 else 0,
        )
        painter.restore()

        """
        绘制手柄
        """
        center_x = progress_rect.right()
        center_y = progress_rect.center().y()

        painter.save()
        painter.setClipping(False)
        painter.translate(center_x, center_y)
        if self.underMouse() or self.isSliderDown():  # 鼠标悬浮
            painter.scale(1.2, 1.2)
        painter.setPen(QPen(QColor(theme_manager.current.text_bold), 2))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(QPoint(0, 0), 8, 8)
        painter.restore()
