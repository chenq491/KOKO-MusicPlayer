from dataclasses import dataclass
from enum import Enum
from PySide6.QtCore import QObject, Signal


@dataclass(frozen=True)
class ThemeColor:
    bg_color_0: str
    bg_color_100: str
    bg_color_200: str
    bg_color_300: str
    bg_color_400: str
    bg_color_500: str
    bg_color_600: str
    bg_color_700: str
    bg_color_800: str

    text_color_100: str
    text_color_200: str
    text_color_300: str

class Theme(Enum):
    PURPLE_THEME = ThemeColor(
        bg_color_0="#e5e5e5", bg_color_100="#e9ebfa", bg_color_200="#dfe0f5", bg_color_300="#d9dbf2",
        bg_color_400="#cbcfea", bg_color_500="#adb2e9", bg_color_600="#9295d3", bg_color_700="#6e74c4",
        bg_color_800="#5a4ae0", text_color_100="#7b7b8b", text_color_200="#5c6175", text_color_300="#4a4c57"
    )
    DARK_THEME = ThemeColor(
        bg_color_0="#e5e5e5", bg_color_100="#1e1e1e", bg_color_200="#121212", bg_color_300="#2c2c2c",
        bg_color_400="#404040", bg_color_500="#3a3a3a", bg_color_600="#6e74c4", bg_color_700="#5a4ae0",
        bg_color_800="#121212", text_color_100="#6b6b6b", text_color_200="#b3b3b3", text_color_300="#cdcacc",
    )

class ThemeManager(QObject):
    themeChanged = Signal()

    def __init__(self):
        super().__init__()
        self._current = Theme.DARK_THEME

    def set_theme(self, theme: Theme):
        self.current = theme
        self.themeChanged.emit()

    @property
    def current(self) -> ThemeColor:
        return self._current.value

    @current.setter
    def current(self, value):
        self._current = value

    @staticmethod
    def get_representative_color(theme: Theme) -> str | None:
        if theme == Theme.DARK_THEME:
            return Theme.DARK_THEME.value.bg_color_100
        elif theme == Theme.PURPLE_THEME:
            return Theme.PURPLE_THEME.value.bg_color_600

        return None

theme_manager = ThemeManager()
