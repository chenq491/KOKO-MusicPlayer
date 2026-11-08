"""卡片绘制工具。

Mizuki 的页面是「浅色底 + 白色圆角卡片」的分层效果，
Qt 里没有现成的 box-shadow，所以这里用几层透明度递减的圆角矩形近似。
"""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen

CARD_RADIUS = 12


def draw_card(
    painter: QPainter,
    rect,
    *,
    fill: str,
    border: str | None = None,
    radius: int = CARD_RADIUS,
    shadow: str | None = None,
):
    """在 rect 里画一张圆角卡片，可带 1px 描边和向下偏移的柔和阴影。"""
    area = QRectF(rect)
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    if shadow:
        shadow_color = QColor(shadow)
        painter.setPen(Qt.PenStyle.NoPen)
        # 从外到内三层，越靠外越透明，阴影整体向下偏移一点
        for spread, opacity in ((4.0, 0.25), (2.5, 0.45), (1.0, 0.8)):
            layer = QColor(shadow_color)
            layer.setAlphaF(min(1.0, shadow_color.alphaF() * opacity))
            painter.setBrush(layer)
            painter.drawRoundedRect(
                area.adjusted(-spread, -spread + 1.5, spread, spread + 1.5),
                radius + spread,
                radius + spread,
            )

    if border:
        painter.setPen(QPen(QColor(border), 1))
    else:
        painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(fill))
    painter.drawRoundedRect(area, radius, radius)

    painter.restore()
