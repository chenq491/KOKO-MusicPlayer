from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import QLabel

from assets.svg import guitar_icon_1
from singleton.themeManager import theme_manager
from utils.utils import create_svg_icon

# 指针尺寸：小一点才能正好压在进度条的细线上
THUMB_SIZE = 24


class HandleLabel(QLabel):
    """进度条上的“吉他”指针。

    它跟着播放进度横向移动，颜色取当前主题色，垂直方向以进度条中心线为准，
    这样在白色卡片里它是一枚安静的进度标记，不会像以前那样悬在卡片边缘外。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bp_rect = QRect(0, 0, 0, 0)
        self.bar_rect = QRect(0, 0, 0, 0)
        self.progress_fraction = 0.0

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.refresh_icon()
        theme_manager.themeChanged.connect(self.on_theme_changed)

    def refresh_icon(self):
        """按主题色重新生成吉他图标"""
        color = theme_manager.current.accent
        icon = create_svg_icon(guitar_icon_1, color, THUMB_SIZE)
        self.setPixmap(icon.pixmap(THUMB_SIZE, THUMB_SIZE))
        self.setFixedSize(THUMB_SIZE, THUMB_SIZE)

    def on_theme_changed(self):
        self.refresh_icon()
        self.set_geometry(self.progress_fraction)

    def set_geometry(self, fraction):
        """fraction 是播放进度（0~1），指针横向对齐进度条的对应位置"""
        self.progress_fraction = fraction
        bar = self.bar_rect if not self.bar_rect.isNull() else self.bp_rect
        x = bar.left() + int(bar.width() * fraction) - THUMB_SIZE // 2
        # 没拿到进度条矩形时，退回到面板顶部
        top = self.bar_rect.top() if not self.bar_rect.isNull() else self.bp_rect.top()
        height = self.bar_rect.height() if not self.bar_rect.isNull() else 0
        self.move(x, top + height // 2 - THUMB_SIZE // 2)

    def update_bp_rect(self, bp):
        """底部面板矩形（父坐标系），仅在没有进度条矩形时兜底"""
        self.bp_rect = QRect(
            bp.mapTo(self.parent(), bp.rect().topLeft()),
            bp.size(),
        )

    def update_bar_rect(self, progress_slider):
        """进度条矩形（父坐标系），指针按它的中心线对齐"""
        self.bar_rect = QRect(
            progress_slider.mapTo(self.parent(), progress_slider.rect().topLeft()),
            progress_slider.size(),
        )
        self.set_geometry(self.progress_fraction)
