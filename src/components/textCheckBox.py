from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QWidget, QHBoxLayout, QLabel, QSizePolicy

from singleton.themeManager import theme_manager
from styleTemplate.styleFontLabel import StyleFontLabel
from uitls.utils import create_style_label


class TextCheckBox(QWidget):
    stateChanged = Signal(bool)

    def __init__(self, label: StyleFontLabel = None, height=25, parent=None):
        super().__init__(parent)

        # 透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMaximumHeight(height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # 鼠标样式变化
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        # 逻辑勾选框，不显示
        self.logic_cb = QCheckBox(self)
        self.logic_cb.setHidden(True)

        # 显示组件
        self.label_indicator = QLabel(self)  # 用于显示方框和对勾
        self.label_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_text = StyleFontLabel("默认") if label is None else label
        self.set_indicator_style()

        # 信号连接
        self.logic_cb.stateChanged.connect(self._on_state_changed)

        # 布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        main_layout.setSpacing(10)
        main_layout.addWidget(self.label_indicator)
        main_layout.addWidget(self.label_text)
        main_layout.addStretch()

    def set_indicator_style(self, size=18, border_color=theme_manager.current.text_normal, border_width=1):
        """设置勾选框基础样式"""
        self.label_indicator.setFixedSize(size, size)
        self.label_indicator.setStyleSheet(f"""
            border: {border_width}px solid {border_color};
            border-radius: 4px;
            background-color: transparent;
        """)

    def toggle(self):
        """切换选中状态"""
        self.logic_cb.toggle()

    def is_checked(self):
        return self.logic_cb.isChecked()

    def set_checked(self, is_checked):
        self.logic_cb.setChecked(is_checked)

    def set_color(self, color):
        self.label_text.set_color(color)
        self._update_style(self.is_checked())

    def _on_state_changed(self, state):
        """内部状态改变时的处理"""
        is_checked = (state == Qt.CheckState.Checked.value)
        self._update_style(is_checked)  # 更新样式
        self.stateChanged.emit(is_checked)  # 发送信号

    def _update_style(self, is_checked):
        """根据状态更新样式（填充颜色 + 对勾）"""
        if is_checked:
            # 选中状态：填充蓝色背景，显示对勾字符
            self.label_indicator.setStyleSheet(f"""
                border: 1px solid {theme_manager.current.checkbox_bg};
                border-radius: 4px;
                background-color: {theme_manager.current.checkbox_bg};
                color: white;
                font-size: 14px;
                font-weight: bold;
            """)
            self.label_indicator.setText("✓")  # 使用 Unicode 对勾字符
        else:
            # 未选中状态：透明背景，无文字
            self.label_indicator.setStyleSheet(f"""
                border: 1px solid {theme_manager.current.text_normal};
                border-radius: 4px;
                background-color: transparent;
            """)
            self.label_indicator.setText("")

    def mousePressEvent(self, event, /):
        """点击事件"""
        self.logic_cb.toggle()

    def enterEvent(self, event):
        """鼠标进入时：改变边框颜色"""
        # 只有在未选中时才改变颜色
        if not self.is_checked():
            self.label_indicator.setStyleSheet(f"""
                border: 1px solid {theme_manager.current.text_bold};
                border-radius: 4px;
                background-color: transparent;
            """)

    def leaveEvent(self, event):
        """鼠标离开时：恢复边框颜色"""
        if not self.is_checked():
            self.label_indicator.setStyleSheet(f"""
                border: 1px solid {theme_manager.current.text_normal};
                border-radius: 4px;
                background-color: transparent;
            """)
