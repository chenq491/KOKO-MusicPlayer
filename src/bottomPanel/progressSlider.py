from PySide6.QtCore import Qt, QRect, QRectF
from PySide6.QtGui import QPixmap, QColor, QPainter, QBrush
from PySide6.QtWidgets import QSlider

from singleton.themeManager import theme_manager


class ProgressSlider(QSlider):
    """进度条"""

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)

        self.handle_pix = QPixmap("../assets/guitar.svg")

        self.setFixedHeight(10)

        self.setMouseTracking(True)  # 开启鼠标追踪以支持 hover 效果
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # 鼠标样式变化

        self.groove_height = 4
        self.groove_border_color = QColor(255, 255, 255)
        self.groove_border_width = 1
        self.groove_progress_color = None
        self.groove_bg_color = None
        self.groove_radius = 2

        self.groove_rect = QRect(
            self.rect().left(),
            self.rect().top() + ((self.rect().height() - self.groove_height) // 2),
            self.rect().width(),
            self.groove_height
        )

        self.update_style()

        theme_manager.themeChanged.connect(self.update_style)

    def update_style(self):
        self.groove_bg_color = QColor(theme_manager.current.slider_bg)
        self.groove_progress_color = QColor(theme_manager.current.slider_progress)

    def resizeEvent(self, event, /):
        super().resizeEvent(event)
        self.groove_rect = QRect(
            self.rect().left(),
            self.rect().top() + ((self.rect().height() - self.groove_height) // 2),
            self.rect().width(),
            self.groove_height
        )

    def get_ratio(self):
        # 计算进度条的宽度
        if self.maximum() == self.minimum():
            progress_ratio = 0.0
        else:
            progress_ratio = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
        return progress_ratio

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # TODO 这里可以选择性地重绘背景，达到性能优化
        """
        绘制滑槽
        """
        # 计算进度条的宽度
        # if self.maximum() == self.minimum():
        #     progress_ratio = 0.0
        # else:
        #     progress_ratio = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
        progress_width = int(self.groove_rect.width() * self.get_ratio())
        progress_rect = QRect(
            self.groove_rect.left(),
            self.groove_rect.top(),
            progress_width,
            self.groove_rect.height()
        )

        # 绘制滑槽边框和背景
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        # painter.setPen(QPen(self.groove_border_color, self.groove_border_width))  # 边框
        painter.setBrush(QBrush(self.groove_bg_color))  # 背景
        painter.drawRoundedRect(
            self.groove_rect,
            self.groove_radius,
            self.groove_radius
        )
        painter.restore()

        # 绘制滑槽进度
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)  # 无边框
        painter.setBrush(QBrush(self.groove_progress_color))
        painter.drawRoundedRect(
            progress_rect,
            self.groove_radius if progress_width > 0 else 0,  # 有进度才显示圆角
            self.groove_radius if progress_width > 0 else 0,
        )
        painter.restore()

        """
        绘制手柄
        """
        handle_rect = QRect(
            progress_rect.right() - 16,
            self.rect().top() + ((self.rect().height() - 32) // 2),
            32, 32
        )
        center_x = handle_rect.center().x()
        center_y = handle_rect.center().y()

        painter.save()
        painter.setClipping(False)
        painter.translate(center_x, center_y)
        if self.underMouse():  # 鼠标悬浮
            painter.rotate(15)
        if self.isSliderDown():  # 鼠标按下
            painter.scale(1.2, 1.2)
        w = self.handle_pix.width()
        h = self.handle_pix.height()
        target_rect = QRectF(-w / 2, -h / 2, w, h)
        # painter.drawPixmap(target_rect.toRect(), self.handle_pix)
        painter.restore()

    def mousePressEvent(self, event):
        # 如果需要自定义点击区域（比如只点击图片有效区域），可以在这里拦截
        # 否则直接调用父类，保持默认拖动行为
        super().mousePressEvent(event)
