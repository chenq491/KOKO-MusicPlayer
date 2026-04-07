from PySide6.QtCore import Signal, Qt, QRect, Slot
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout

from singleton.playListManager import PlayListManager
from singleton.themeManager import theme_manager
from .songListToolBar import SongListToolBar
from .songListView import MusicListView


class SongListPage(QWidget):
    songItemDoubleClicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # 总歌曲数
        self.total = 0

        # 工具栏
        self.tool_bar = SongListToolBar(self)

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

        self.tool_bar.searchSignal.connect(self.on_search)

    def show_music_list(self):
        """显示音乐列表"""
        # self.list_body.loading_widget.start()
        self.list_body.load_data()
        self.total = PlayListManager.get_total_song()
        self.list_title.update_total(self.total)

    def set_current(self):
        """高亮显示当前歌曲"""
        self.list_body.set_current()

    def location(self):
        self.set_current()
        self.list_body.scroll_to_current()

    @Slot()
    def on_search(self, info: list):
        self.list_body.search(*info)



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
        painter.setPen(theme_manager.current.text_bold)

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