from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor

from singleton.config import config


class ThemeMode(Enum):
    LIGHT = False
    DARK = True


class ThemeColor(Enum):
    PURPLE = "purple"
    GREEN = "green"


@dataclass(frozen=True)
class Theme:
    window_bg: str

    list_item_bg: str
    list_item_hover: str
    list_item_selected: str

    button_bg: str
    button_hover: str
    button_selected: str

    slider_bg: str
    slider_progress: str

    line_edit_bg: str
    checkbox_bg: str

    text_light: str
    text_normal: str
    text_bold: str


class ThemeManager(QObject):
    themeChanged = Signal()

    def __init__(self, /):
        super().__init__()

        self.theme_colors = {"purple": "#8778ff", "green": "#8fd3f4"}

        self._current_mode = ThemeMode(config.get_value(["style_setting", "dark_mode"]))
        self._current_color = None
        self.current = Theme("", "", "", "", "", "", "", "", "", "", "", "", "", "")

        self.set_theme(self._current_mode, ThemeColor.GREEN)

    def set_theme(self, mode: ThemeMode, color: ThemeColor):
        if not mode is None:
            self._current_mode = mode
        if not color is None:
            self._current_color = color

        color = QColor(self.theme_colors[self._current_color.value])
        if self._current_mode == ThemeMode.LIGHT:
            self.current = Theme(
                window_bg=color.lighter(140).name(),
                list_item_bg=color.lighter(135).name(),
                list_item_hover=color.lighter(130).name(),
                list_item_selected=color.lighter(125).name(),
                button_bg=color.name(),
                button_hover=color.lighter(105).name(),
                button_selected=color.lighter(110).name(),
                slider_bg=color.lighter(120).name(),
                slider_progress=color.darker(110).name(),
                line_edit_bg=color.lighter(135).name(),
                checkbox_bg=color.name(),
                text_light="#7b7b8b",
                text_normal="#5c6175",
                text_bold="#4a4c57",
            )
        else:
            self.current = Theme(
                window_bg="#13131a",
                list_item_bg="#13131a",
                list_item_hover="#272734",
                list_item_selected="#3C3C4D",
                button_bg=color.darker(120).name(),
                button_hover=color.darker(110).name(),
                button_selected=color.darker(105).name(),
                slider_bg="#404049",
                slider_progress=color.darker(130).name(),
                line_edit_bg="#121212",
                checkbox_bg=color.darker(150).name(),
                text_light="#B4B4B4",
                text_normal="#CBCBCB",
                text_bold="#d0d0d1",
            )

        self.themeChanged.emit()

    def get_representative_color(self, color: ThemeColor):
        return self.theme_colors[color.value]


theme_manager = ThemeManager()
