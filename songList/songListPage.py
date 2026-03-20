from PySide6.QtCore import Signal, Qt, QRect
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit
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

    def show_music_list(self, song_list: list):
        """显示音乐列表"""
        # self.list_body.loading_widget.start()
        self.list_body.load_data(song_list)

        self.total = len(song_list)
        self.list_title.update_total(self.total)

    def set_current(self, current_song_index: int):
        """跳转到指定的歌曲项并高亮显示"""
        self.list_body.set_current(current_song_index)


class ListToolBar(QWidget):
    refresh = Signal()

    """工具栏"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.refresh_button = RefreshButton()
        self.shuffle_button = ShuffleButton()

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(SearchBox(parent=self))
        main_layout.addWidget(self.shuffle_button)
        main_layout.addWidget(self.refresh_button)

        main_layout.setContentsMargins(10, 0, 10, 0)

        self.setFixedHeight(45)

        self.refresh_button.clicked.connect(self.refresh)


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


class SearchBox(QLineEdit):
    """搜索框"""
    searchSignal = Signal(str)

    def __init__(self, placeholder="搜索...", parent=None):
        super().__init__(parent)
        self.setup_ui(placeholder)
        self.setup_style()
        self.setup_connections()

    def setup_ui(self, placeholder):
        """设置 UI 组件"""
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(30)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # 创建图标和清除按钮容器
        # self.left_widget = QWidget()
        # self.left_layout = QHBoxLayout(self.left_widget)
        # self.left_layout.setContentsMargins(12, 0, 0, 0)
        # self.left_layout.setSpacing(0)

        # # 搜索图标
        # self.search_icon = SearchIcon(color="#999999", size=18)
        # self.left_layout.addWidget(self.search_icon)
        #
        # # 清除按钮
        # self.clear_btn = ClearButton(self)
        # self.clear_btn.clicked.connect(self.clear_search)

        # 设置边距
        self.setTextMargins(36, 0, 36, 0)

    def setup_style(self):
        """设置样式"""
        self.base_style = """
                    QLineEdit {
                        border: 2px solid #e0e0e0;
                        border-radius: 15px;
                        background-color: #f8f9fa;
                        padding: 0px 12px;
                        font-size: 15px;
                        font-family: "微软雅黑", "SimHei", Arial, sans-serif;
                        color: #333333;
                    }
                    QLineEdit:focus {
                        border: 2px solid #4A90E2;
                        background-color: #ffffff;
                    }
                    QLineEdit:hover {
                        border: 2px solid #cccccc;
                    }
                """
        self.setStyleSheet(self.base_style)

    def setup_connections(self):
        """设置信号连接"""
        self.textChanged.connect(self.on_text_changed)
        self.returnPressed.connect(self.on_return_pressed)

    def on_text_changed(self, text):
        """文本变化时"""
        # self.clear_btn.setVisible(len(text) > 0)
        # if len(text) > 0:
        #     self.clear_btn.setParent(self)
        #     self.clear_btn.move(self.width() - 36, (self.height() - 24) // 2)
        #     self.clear_btn.raise_()
        #     self.clear_btn.show()

    def on_return_pressed(self):
        """回车键按下时"""
        self.searchSignal.emit(self.text())

    def clear_search(self):
        """清除搜索内容"""
        self.clear()
        self.setFocus()

    # def focusInEvent(self, event):
    #     """获得焦点时"""
    #     super().focusInEvent(event)
    #     self.search_icon.color = "#4A90E2"
    #     self.search_icon.update()
    #
    #
    # def focusOutEvent(self, event):
    #     """失去焦点时"""
    #     super().focusOutEvent(event)
    #     self.search_icon.color = "#999999"
    #     self.search_icon.update()


class RefreshButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.pressed_size = (23, 23)

        self.btn_icon = create_svg_icon(refresh_icon, self.normal_color, 25)
        self.hover_icon = create_svg_icon(refresh_icon, self.hover_color, 25)

        self.setIcon(self.btn_icon)
        self.setToolTip("刷新")


class ShuffleButton(SvgIconButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.pressed_size = (23, 23)

        self.btn_icon = create_svg_icon(shuffle_icon, self.normal_color, 25)
        self.hover_icon = create_svg_icon(shuffle_icon, self.hover_color, 25)

        self.setIcon(self.btn_icon)
        self.setToolTip("打乱")
