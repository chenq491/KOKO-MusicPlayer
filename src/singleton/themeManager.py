from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import QObject, Signal

from singleton.config import config
from singleton.themePalette import ThemePalette, build_palette


class ThemeMode(Enum):
    LIGHT = False
    DARK = True


class ThemeColor(Enum):
    """主题色（对应 Mizuki 的 hue 变量）"""

    BLUE = "blue"
    PURPLE = "purple"


# 站点通过 --configHue 切换整套配色，这里保留同样的思路
THEME_HUES = {
    ThemeColor.BLUE: 240,
    ThemeColor.PURPLE: 285,
}


@dataclass(frozen=True)
class Theme(ThemePalette):
    """语义化色板 + 旧字段名的兼容层。

    旧代码里到处都是 window_bg / text_bold 这种按外观命名的字段，
    一次性改完风险太大，所以这里把旧名字映射到新的语义 token 上，
    新代码请直接使用 ThemePalette 的字段。
    """

    @property
    def window_bg(self) -> str:
        return self.page_bg

    @property
    def list_item_bg(self) -> str:
        return self.surface

    @property
    def list_item_hover(self) -> str:
        return self.surface_hover

    @property
    def list_item_selected(self) -> str:
        return self.surface_selected

    @property
    def button_selected(self) -> str:
        return self.button_pressed

    @property
    def slider_bg(self) -> str:
        return self.track

    @property
    def slider_progress(self) -> str:
        return self.accent

    @property
    def playlist_bg(self) -> str:
        return self.card_bg

    @property
    def playlist_hover(self) -> str:
        return self.card_hover

    @property
    def playlist_selected(self) -> str:
        return self.surface_selected

    @property
    def line_edit_bg(self) -> str:
        return self.input_bg

    @property
    def checkbox_bg(self) -> str:
        return self.accent

    @property
    def text_light(self) -> str:
        return self.text_muted

    @property
    def text_normal(self) -> str:
        return self.text_body

    @property
    def text_bold(self) -> str:
        return self.text_strong

    @property
    def text_theme_normal(self) -> str:
        return self.text_accent

    @property
    def text_theme_light(self) -> str:
        return self.text_accent_soft


class ThemeManager(QObject):
    themeChanged = Signal()

    def __init__(self, /):
        super().__init__()

        self._current_mode = self._read_mode()
        self._current_color = self._read_color()
        self.current = self._build()

    # ------------------------------------------------------------------ 读取配置
    @staticmethod
    def _read_mode() -> ThemeMode:
        value = config.get_value(["style_setting", "dark_mode"])
        return ThemeMode.DARK if value else ThemeMode.LIGHT

    @staticmethod
    def _read_color() -> ThemeColor:
        value = config.get_value(["style_setting", "theme_color"])
        try:
            return ThemeColor(value)
        except ValueError:
            return ThemeColor.BLUE

    def _build(self) -> Theme:
        palette = build_palette(
            self._current_mode == ThemeMode.DARK,
            THEME_HUES[self._current_color],
        )
        return Theme(**palette.__dict__)

    # ------------------------------------------------------------------ 对外接口
    def set_theme(self, mode: ThemeMode | None = None, color: ThemeColor | None = None):
        """只改变运行时的主题，不写配置文件（由设置页负责持久化）。"""
        changed = False
        if mode is not None and mode != self._current_mode:
            self._current_mode = mode
            changed = True
        if color is not None and color != self._current_color:
            self._current_color = color
            changed = True

        if not changed:
            return

        self.current = self._build()
        self.themeChanged.emit()

    def get_representative_color(self, color: ThemeColor) -> str:
        """主题色按钮上要显示的主色"""
        return build_palette(False, THEME_HUES[color]).accent

    @property
    def mode(self) -> ThemeMode:
        return self._current_mode

    @property
    def color(self) -> ThemeColor:
        return self._current_color


theme_manager = ThemeManager()
