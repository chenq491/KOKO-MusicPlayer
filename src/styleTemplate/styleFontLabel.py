from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel

from singleton.themeManager import theme_manager
from styleTemplate.themeText import TextRole, resolve_text_color


class StyleFontLabel(QLabel):
    """自动跟随主题颜色的标签。

    两种用法：
    - 声明语义角色（推荐）：`StyleFontLabel("歌名")`、`StyleFontLabel("时长", role=TextRole.MUTED)`
    - 固定颜色（少数场景）：`StyleFontLabel("x", color="#ff0000")`，此时不再跟随主题

    标签在构造时自己连上 `theme_manager.themeChanged`，Qt 会在控件销毁时
    自动断开，所以父容器不用再逐个 `set_color`。
    """

    def __init__(
        self,
        text,
        family="Microsoft YaHei",
        font_size=13,
        bold=True,
        role=TextRole.STRONG,
        color=None,
        parent=None,
    ):
        super().__init__(parent)

        font = QFont()
        font.setFamily(family)
        font.setPointSize(font_size)
        font.setBold(bold)
        self.setFont(font)
        self.setText(text)

        self._role = None
        self._fixed_color = None
        # 显式给颜色时按固定色处理，否则按角色跟随主题
        if color is not None:
            self.set_color(color)
        else:
            self.set_role(role)

        theme_manager.themeChanged.connect(self.refresh_theme)

    # ------------------------------------------------------------------ 对外接口
    def set_role(self, role):
        """切换语义角色（strong / body / muted / accent / accent_soft / on_accent）"""
        self._role = TextRole(role)
        self._fixed_color = None
        self.refresh_theme()

    def set_color(self, color):
        """固定颜色：不再跟随主题，适合“此刻就是这个色”的临时场景"""
        self._role = None
        self._fixed_color = color
        self._apply_color(color)

    # ------------------------------------------------------------------ 内部实现
    def refresh_theme(self):
        """主题变化时按角色重新取色"""
        if self._role is not None:
            self._apply_color(resolve_text_color(theme_manager.current, self._role))

    def _apply_color(self, color):
        self.setStyleSheet(f"color: {color};")
