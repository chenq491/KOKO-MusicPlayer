from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from constant import MessageType


class Message(QWidget):
    _instances = []  # 存储所有活跃消息，垂直堆叠
    parent_global = None

    @classmethod
    def set_parent(cls, parent):
        cls.parent_global = parent

    def __init__(
        self,
        text: str,
        duration=2000,
        msg_type: MessageType = MessageType.INFO,
        min_width=300,
        parent=None,
    ):
        super().__init__(parent if parent else Message.parent_global)
        self.setWindowFlag(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool  # 避免任务栏图标
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)  # 不抢焦点

        self.setMinimumWidth(min_width)

        # 样式配置
        styles = {
            "info": "#e1f5fe; color: #01579b;",
            "success": "#e8f5e9; color: #2e7d32;",
            "warning": "#fff8e1; color: #ff8f00;",
            "error": "#ffebee; color: #c62828;",
        }
        bg_style = styles.get(msg_type.value, styles["info"])

        # 创建标签
        self.label = QLabel(text)
        self.label.setFont(QFont("Microsoft YaHei", 10))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {bg_style.split(";")[0]};
                        color: {bg_style.split(";")[1].replace(" color: ", "")};
                        padding: 12px 20px;
                        border-radius: 6px;
                    }}
                """)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)

        # 动画相关
        self._duration = duration
        self._animation = None

    def show_message(self):
        """显示消息（外部调用此方法）"""
        if not self.parent_global and not self.parent():
            raise ValueError("Message 必须设置 parent（通常是主窗口）")

        # 计算位置：在 parent 顶部居中，并考虑已有消息的高度
        parent = self.parent()
        parent_rect = parent.geometry()
        offset_y = 20  # 初始偏移

        # 堆叠：每个新消息在上一个下方
        for msg in Message._instances:
            if msg.isVisible():
                offset_y += msg.height() + 10

        x = parent_rect.center().x() - self.width() // 2
        y = parent_rect.top() + offset_y

        self.move(x, y - 50)  # 从上方滑入
        self.show()
        self.raise_()

        # 添加到实例列表
        Message._instances.append(self)

        # 滑入动画
        self._animation = QPropertyAnimation(self, b"pos")
        self._animation.setDuration(300)
        self._animation.setStartValue(QPoint(x, y - 50))
        self._animation.setEndValue(QPoint(x, y))
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.start()

        # 自动关闭
        QTimer.singleShot(self._duration, self.close)

    def closeEvent(self, event):
        """关闭时清理"""
        if self in Message._instances:
            Message._instances.remove(self)

        # 添加淡出动画
        self._animation = QPropertyAnimation(self, b"windowOpacity")
        self._animation.setDuration(100)
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.0)
        self._animation.finished.connect(self.deleteLater)  # TODO deleLater什么意思？
        self._animation.start()
        event.ignore()  # 阻止立即关闭，等动画结束


def show_message(
    text: str,
    duration=2000,
    msg_type: MessageType = MessageType.INFO,
    min_width=300,
    parent=None,
):
    """全局调用函数，简化使用"""
    msg = Message(
        text, parent=parent, duration=duration, msg_type=msg_type, min_width=min_width
    )
    msg.show_message()
    return msg
