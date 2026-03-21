from PySide6.QtCore import Signal, Qt, QRect, QSize, Slot
from PySide6.QtGui import QPainter, QFont, QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton

from singleton.playListManager import PlayListManager
from .songListView import MusicListView
from styleTemplate.svgIconButton import SvgIconButton
from assets.svg import refresh_icon, shuffle_icon
from uitls.utils import create_svg_icon


class SongListPage(QWidget):
    songItemDoubleClicked = Signal(int)
    refresh = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # 总歌曲数
        self.total = 0

        # 工具栏
        self.tool_bar = ListToolBar(self)

        # 列表头
        self.list_title = ListTitle(self.total, self)

        # 列表体
        self.list_body = MusicListView(self)
        self.list_body.itemDoubleClicked.connect(self.songItemDoubleClicked)

        self.current_song_item_widget = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.tool_bar)
        main_layout.addWidget(self.list_title)
        main_layout.addWidget(self.list_body)

        self.tool_bar.refresh.connect(self.refresh)
        self.tool_bar.searchSignal.connect(self.on_search)

    def show_music_list(self):
        """显示音乐列表"""
        # self.list_body.loading_widget.start()
        self.list_body.load_data()
        self.total = PlayListManager.get_total_song()
        self.list_title.update_total(self.total)

    def set_current(self):
        """跳转到指定的歌曲项并高亮显示"""
        self.list_body.set_current(PlayListManager.get_current_song_index())

    @Slot()
    def on_search(self, value: str):
        self.list_body.search(value)


class ListToolBar(QWidget):
    refresh = Signal()
    searchSignal = Signal(str)

    """工具栏"""

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

        self.refresh_button.clicked.connect(self.refresh)
        self.search_box.searchSignal.connect(self.searchSignal)


class ListTitle(QWidget):
    """标题栏"""

    def __init__(self, total, parent=None):
        super().__init__(parent)

        self.total = total
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(15)

    def update_total(self, total: int):
        self.total = total
        self.update()

    def paintEvent(self, event, /):
        rect = self.rect()

        painter = QPainter(self)
        font = painter.font()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen("#4c4e5d")

        w = rect.left()
        idx_width = int(rect.width() * 0.04)
        painter.drawText(QRect(
            w, rect.top(), idx_width, rect.height()
        ), Qt.AlignmentFlag.AlignCenter, f"#{self.total}")

        w += idx_width
        cover_width = 60
        painter.drawText(QRect(
            w, 0, cover_width, rect.height()
        ), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "封面")

        w += cover_width
        text_width = rect.width() - (w + 15)
        title_width = int(text_width * 0.6)
        painter.drawText(QRect(
            w + 15, 0, title_width, rect.height()
        ), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "歌名/歌手")

        w += title_width
        album_width = int(text_width * 0.32)
        painter.drawText(QRect(
            w, 0, album_width, rect.height()
        ), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "专辑")

        w += album_width
        duration_width = int(text_width * 0.08)
        painter.drawText(QRect(
            w, 0, duration_width, rect.height()
        ), Qt.AlignmentFlag.AlignCenter, "时长")


class SearchBox(QWidget):
    """搜索框"""
    searchSignal = Signal(str)

    def __init__(self, placeholder="搜索...", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setObjectName("SearchBox")
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

        main_layout.addWidget(self.search_button)
        main_layout.addWidget(self.search_edit)

        self.setFixedHeight(30)

    def init_style(self):
        """设置样式表，核心美化逻辑"""
        self.setStyleSheet("""
            /* 搜索框容器 */
            #SearchBox {
                background: #b6b8e2;
                border-radius: 5px;  /* 圆角（高度的一半）*/
                border: 1px solid #6e74c4;
            }

            /* 输入框基础样式 */
            #SearchLineEdit {
                background: transparent;  /* 透明背景，继承容器渐变 */
                color: #212529;
                border: none;
                outline: none;
            }

            /* 输入框聚焦效果 */
            #SearchLineEdit:focus {
                color: #4a4c57;
            }

            /* 输入框占位符文字样式 */
            #SearchLineEdit::placeholder {
                color: #adb5bd;
                font-style: italic;
            }

            /* 搜索按钮默认样式 */
            #SearchButton {
                border-radius: 5px;
                background: transparent;
            }

            /* 按钮hover效果 */
            #SearchButton:hover {
                background: #9295d3;
            }

            /* 按钮按下效果 */
            #SearchButton:pressed {
                background: #6e74c4;
            }
        """)

    def on_text_emit(self):
        """回车键按下时"""
        self.searchSignal.emit(self.search_edit.text())


class RefreshButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        h = self.parent().height()
        ph = h - 5

        self.pressed_size = (ph, ph)
        self.normal_size = (h, h)

        self.btn_icon = create_svg_icon(refresh_icon, self.normal_color, 25)
        self.hover_icon = create_svg_icon(refresh_icon, self.hover_color, 25)

        self.setFixedSize(*self.normal_size)
        self.setIconSize(QSize(*self.normal_size))

        self.setIcon(self.btn_icon)
        self.setToolTip("刷新")


class ShuffleButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        h = self.parent().height()
        ph = h - 5

        self.pressed_size = (ph, ph)
        self.normal_size = (h, h)

        self.btn_icon = create_svg_icon(shuffle_icon, self.normal_color, 25)
        self.hover_icon = create_svg_icon(shuffle_icon, self.hover_color, 25)

        self.setFixedSize(*self.normal_size)
        self.setIconSize(QSize(*self.normal_size))

        self.setIcon(self.btn_icon)
        self.setToolTip("打乱")
