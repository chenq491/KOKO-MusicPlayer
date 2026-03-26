from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QComboBox

from assets.svg import refresh_icon, shuffle_icon
from singleton.playListManager import PlayListManager
from styleTemplate.svgIconButton import SvgIconButton
from theme import theme_manager, Theme
from uitls.utils import create_svg_icon


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
        self.shuffle_button.clicked.connect(PlayListManager.shuffle_music_list)
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
        self.setStyleSheet(f"""
            /* 搜索框容器 */
            #SearchBox {{
                background: {theme_manager.current.bg_color_200 if theme_manager.current == Theme.DARK_THEME.value else theme_manager.current.bg_color_300};
                border-radius: 5px;  /* 圆角 */
                border: 1px solid {theme_manager.current.bg_color_400};
            }}

            /* 输入框基础样式 */
            #SearchLineEdit {{
                background: transparent;  /* 透明背景，继承容器渐变 */
                color: {theme_manager.current.text_color_300};
                border: none;
                outline: none;
            }}

            /* 输入框聚焦效果 */
            #SearchLineEdit:focus {{
                color: {theme_manager.current.text_color_300};
            }}

            /* 输入框占位符文字样式 */
            #SearchLineEdit::placeholder {{
                color: {theme_manager.current.text_color_200};
                font-style: italic;
            }}

            /* 搜索按钮默认样式 */
            #SearchButton {{
                border-radius: 5px;
                background: transparent;
            }}

            /* 按钮hover效果 */
            #SearchButton:hover {{
                background: {theme_manager.current.bg_color_500};
            }}

            /* 按钮按下效果 */
            #SearchButton:pressed {{
                background: {theme_manager.current.bg_color_600};
            }}
            
            /* 下拉框样式 */
            #SearchComboBox{{
                background-color: {theme_manager.current.bg_color_300};      /* 背景色 */
                color: {theme_manager.current.text_color_300};                 /* 文字颜色 */
                border-radius: 5px;             /* 圆角 */
                padding: 5px 8px;              /* 内边距 */
                margin: 0 1px;
                font-size: 13px;
                font-weight: bold;
            }}
            #SearchComboBox:hover {{
                background-color: {theme_manager.current.bg_color_400};
            }}
            #SearchComboBox::drop-down {{
                border: none;                   /* 去除下拉按钮的边框 */
                width: 5px;                    /* 下拉按钮宽度 */
            }}

            /* 下拉列表的样式 */
            #SearchComboBox QAbstractItemView {{
                background-color: {theme_manager.current.bg_color_300};
                color: {theme_manager.current.text_color_200};
                outline: none;
                border: none;
            }}
            
            #SearchComboBox QAbstractItemView::item {{
                height: 30px;                   /* 选项高度 */
                padding-left: 5px;
            }}
            
            #SearchComboBox QAbstractItemView::item:hover {{
                background-color: {theme_manager.current.bg_color_400};      /* 悬停背景色 (浅灰) */
                color: {theme_manager.current.text_color_300};                 /* 悬停文字变色 (可选) */
                cursor: pointer;
            }}
            
            /* --- 5. 选项选中样式 --- */
            QComboBox QAbstractItemView::item:selected {{
                background-color: {theme_manager.current.bg_color_400};      /* 选中项背景 (浅蓝) */
                color: {theme_manager.current.text_color_300};                 /* 选中项文字 (主题色) */
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
