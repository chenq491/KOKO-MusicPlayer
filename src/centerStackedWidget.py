from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    Signal,
)
from PySide6.QtWidgets import QGraphicsOpacityEffect, QStackedWidget


class CenterStackedWidget(QStackedWidget):
    animationFinished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_direction = None  # 动画方向
        self.m_duration = 300  # 动画时长：300ms
        self.m_animation_type = "slider"  # or 'fade'
        self.m_now = 0  # 当前页面索引
        self.m_next = 0  # 下一个页面索引
        self.m_wrap = False
        self.m_pnow = QPoint(0, 0)
        self.m_active = False  # 是否正在动画中

    def slide_in_next(self):
        """切换到下一个页面"""
        now = self.currentIndex()
        if now < self.count() - 1:
            self.slide_in_idx(now + 1)
        elif self.m_wrap:
            self.slide_in_idx(self.count() - 1)

    def slide_in_prev(self):
        now = self.currentIndex()
        if now > 0:
            self.slide_in_idx(now - 1)
        elif self.m_wrap:
            self.slide_in_idx(self.count() - 1)

    def slide_in_idx(self, idx, direction="next"):
        """根据索引切换页面"""
        if idx > self.count() - 1:
            direction = "next"
            idx = idx % self.count()
        elif idx < 0:
            direction = "prev"
            idx = (idx + self.count()) % self.count()

        self.slide_in_widget(self.widget(idx), direction)

    def slide_in_widget(self, new_widget, direction="next"):
        """滑入新的widget"""
        if self.m_active:
            return
        self.m_active = True

        self.m_direction = direction
        self.m_next = self.indexOf(new_widget)
        self.m_now = self.currentIndex()

        if self.m_now == self.m_next:
            self.m_active = False
            return

        width = self.frameRect().width()
        height = self.frameRect().height()

        # 设置新页面初始位置
        if direction == "next":
            offset = QPoint(width, 0)  # 从右侧进入
        else:
            offset = QPoint(-width, 0)  # 从左侧进入

        new_widget.setGeometry(0, 0, width, height)
        new_widget.move(offset)
        new_widget.show()
        new_widget.raise_()

        # 获取当前页面
        current_widget = self.widget(self.m_now)

        # 动画1：移动位置
        anim_old = QPropertyAnimation(current_widget, b"pos")
        anim_old.setDuration(self.m_duration)
        anim_old.setEasingCurve(QEasingCurve.Type.OutQuad)
        anim_old.setStartValue(QPoint(0, 0))
        if direction == "next":
            anim_old.setEndValue(QPoint(-width, 0))  # 向左滑出
        else:
            anim_old.setEndValue(QPoint(width, 0))  # 向右滑出

        anim_new = QPropertyAnimation(new_widget, b"pos")
        anim_new.setDuration(self.m_duration)
        anim_new.setEasingCurve(QEasingCurve.Type.OutQuad)
        anim_new.setStartValue(offset)
        anim_new.setEndValue(QPoint(0, 0))

        # 动画2：淡入淡出
        effect_old = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(effect_old)
        anim_opacity_old = QPropertyAnimation(effect_old, b"opacity")
        anim_opacity_old.setDuration(self.m_duration)
        anim_opacity_old.setStartValue(1.0)
        anim_opacity_old.setEndValue(0.0)

        effect_new = QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(effect_new)
        anim_opacity_new = QPropertyAnimation(effect_new, b"opacity")
        anim_opacity_new.setDuration(self.m_duration)
        anim_opacity_new.setStartValue(0.0)
        anim_opacity_new.setEndValue(1.0)

        group = QParallelAnimationGroup()
        group.addAnimation(anim_old)
        group.addAnimation(anim_new)
        group.addAnimation(anim_opacity_old)
        group.addAnimation(anim_opacity_new)

        def on_animation_finished():
            self.m_active = False
            self.setCurrentIndex(self.m_next)
            self.animationFinished.emit()

        group.finished.connect(on_animation_finished)
        group.start()
