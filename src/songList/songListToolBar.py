from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QComboBox

from assets.svg import refresh_icon, shuffle_icon
from singleton.musicListManager import music_list_manager
from styleTemplate.svgIconButton import SvgIconButton
from singleton.themeManager import theme_manager
from utils.utils import create_svg_icon


class SongListToolBar(QWidget):
    """工具栏"""
    searchSignal = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)

        self.refresh_button = RefreshButton(self)
        self.shuffle_button = ShuffleButton(self)
        self.search_box = SearchBox(parent=self)

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.search_box)
        main_layout.addWidget(self.shuffle_button)
        main_layout.addWidget(self.refresh_button)

        main_layout.setContentsMargins(10, 0, 10, 0)

        # self.refresh_button.clicked.connect()
        self.shuffle_button.clicked.connect(music_list_manager.shuffle_music_list)
        self.search_box.searchSignal.connect(self.searchSignal)


class SearchBox(QWidget):
    """搜索框"""
    searchSignal = Signal(list)

    def __init__(self, placeholder="搜索...", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setObjectName("SearchBox")
        self.search_combobox = QComboBox()
        self.search_combobox.setObjectName("SearchComboBox")
        self.search_combobox.addItems(["title", "artist", "album"])
        self.search_combobox.setCurrentIndex(0)

        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("SearchLineEdit")
        self.search_button = QPushButton()
        self.search_button.setObjectName("SearchButton")

        self.init_ui(placeholder)
        self.init_style()
        self.search_edit.returnPressed.connect(self.on_text_emit)
        self.search_button.clicked.connect(self.on_text_emit)

    def init_ui(self, placeholder):
        """设置 UI 组件"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.search_edit.setPlaceholderText(placeholder)
        self.search_edit.setFont(QFont("Microsoft YaHei", 10))
        self.search_edit.setFrame(False)  # 清除默认边框
        self.search_edit.setTextMargins(0, 0, 40, 0)  # 内边距
        self.search_edit.setClearButtonEnabled(True)  # 清除按钮

        self.search_button.setIcon(QIcon.fromTheme("edit-find"))
        self.search_button.setIconSize(QSize(20, 20))
        self.search_button.setFixedSize(30, 30)
        self.search_button.setFlat(True)  # 去除边框

        main_layout.addWidget(self.search_combobox)
        main_layout.addWidget(self.search_button)
        main_layout.addWidget(self.search_edit)

        self.setFixedHeight(30)
        theme_manager.themeChanged.connect(self.init_style)

    def init_style(self):
        """设置样式表，核心美化逻辑"""
        theme = theme_manager.current
        self.setStyleSheet(f"""
            /* 搜索框容器 */
            #SearchBox {{
                background: {theme.input_bg};
                border-radius: 10px;  /* 圆角，和卡片保持一致的柔和感 */
                border: 1px solid {theme.divider};
            }}

            /* 输入框基础样式 */
            #SearchLineEdit {{
                background: transparent;  /* 透明背景，继承容器样式 */
                color: {theme.text_body};
                border: none;
                outline: none;
                selection-background-color: {theme.surface_selected};
                selection-color: {theme.text_strong};
            }}

            /* 输入框聚焦效果 */
            #SearchLineEdit:focus {{
                color: {theme.text_strong};
            }}

            /* 输入框占位符文字样式 */
            #SearchLineEdit::placeholder {{
                color: {theme.text_muted};
                font-style: italic;
            }}

            /* 搜索按钮默认样式 */
            #SearchButton {{
                border-radius: 8px;
                background: transparent;
            }}

            /* 按钮hover效果 */
            #SearchButton:hover {{
                background: {theme.button_hover};
            }}

            /* 按钮按下效果 */
            #SearchButton:pressed {{
                background: {theme.button_pressed};
            }}

            /* 下拉框样式 */
            #SearchComboBox{{
                background-color: {theme.button_bg};      /* 软按钮色 */
                color: {theme.text_body};
                border: none;
                border-radius: 8px;             /* 圆角 */
                padding: 5px 8px;              /* 内边距 */
                margin: 0 1px;
                font-size: 13px;
                font-weight: bold;
            }}
            #SearchComboBox:hover {{
                background-color: {theme.button_hover};
            }}
            #SearchComboBox::drop-down {{
                border: none;                   /* 去除下拉按钮的边框 */
                width: 5px;                    /* 下拉按钮宽度 */
            }}

            /* 下拉列表的样式 */
            #SearchComboBox QAbstractItemView {{
                background-color: {theme.surface};
                color: {theme.text_body};
                border: 1px solid {theme.divider};
                outline: none;
            }}

            #SearchComboBox QAbstractItemView::item {{
                height: 30px;                   /* 选项高度 */
                padding-left: 5px;
            }}

            #SearchComboBox QAbstractItemView::item:hover {{
                background-color: {theme.surface_hover};
                color: {theme.text_strong};
                cursor: pointer;
            }}

            /* --- 5. 选项选中样式 --- */
            QComboBox QAbstractItemView::item:selected {{
                background-color: {theme.surface_selected};
                color: {theme.text_accent};
                font-weight: bold;
            }}
        """)

    def on_text_emit(self):
        """回车键按下时"""
        self.searchSignal.emit([self.search_combobox.currentText(), self.search_edit.text()])


class RefreshButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        h = self.parent().height()
        ph = h - 5

        self.pressed_size = (ph, ph)
        self.normal_size = (h, h)

        self.setFixedSize(*self.normal_size)
        self.setIconSize(QSize(*self.normal_size))

        self.setToolTip("刷新")
        self.set_icon()

    def create_icon(self):
        self.btn_icon = create_svg_icon(refresh_icon, self.normal_color, 25)
        self.hover_icon = create_svg_icon(refresh_icon, self.hover_color, 25)


class ShuffleButton(SvgIconButton):
    """随机按钮"""

    def __init__(self, parent=None):
        super().__init__(parent)

        h = self.parent().height()
        ph = h - 5

        self.pressed_size = (ph, ph)
        self.normal_size = (h, h)

        self.setFixedSize(*self.normal_size)
        self.setIconSize(QSize(*self.normal_size))

        self.setToolTip("打乱")

        self.set_icon()

    def create_icon(self):
        self.btn_icon = create_svg_icon(shuffle_icon, self.normal_color, 25)
        self.hover_icon = create_svg_icon(shuffle_icon, self.hover_color, 25)
