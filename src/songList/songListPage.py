from PySide6.QtCore import Signal, Qt, QRect, Slot
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout

from Logger import logger
from singleton.musicListManager import music_list_manager
from singleton.themeManager import theme_manager
from songList.songListToolBar import SongListToolBar
from songList.songListView import MusicListView


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
        self.current_song_item_widget = None

        self.set_layout()
        self.bind()
        # 表头和行内的颜色都是绘制时现取的，主题切换后要主动重绘
        theme_manager.themeChanged.connect(self.update_theme)

    def set_layout(self):
        main_layout = QVBoxLayout(self)
        # 外层卡片由主窗口绘制，这里留出卡片内边距
        main_layout.setContentsMargins(14, 14, 7, 14)
        main_layout.setSpacing(4)
        main_layout.addWidget(self.tool_bar)
        main_layout.addWidget(self.list_title)
        main_layout.addWidget(self.list_body)

    def bind(self):
        self.tool_bar.searchSignal.connect(self.on_search)
        self.list_body.itemDoubleClicked.connect(self.songItemDoubleClicked)

    def update_theme(self):
        """主题切换后重绘表头与所有行（颜色都是 paintEvent 里现取的）"""
        self.list_title.update()
        self.list_body.viewport().update()
        self.update()

    def show_music_list(self):
        """显示音乐列表"""
        logger.info("show music list")
        # self.list_body.loading_widget.start()
        self.list_body.load_data()
        self.total = music_list_manager.get_total_song()
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
        # 表头用弱化的次要文字色，避免和白卡片抢视线
        painter.setPen(theme_manager.current.text_muted)

        w = rect.left()
        idx_width = int(rect.width() * 0.04)
        painter.drawText(
            QRect(w, rect.top(), idx_width, rect.height()),
            Qt.AlignmentFlag.AlignCenter,
            f"#{self.total}",
        )

        w += idx_width
        cover_width = 60
        painter.drawText(
            QRect(w, 0, cover_width, rect.height()),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            "封面",
        )

        w += cover_width
        text_width = rect.width() - (w + 15)
        title_width = int(text_width * 0.6)
        painter.drawText(
            QRect(w + 15, 0, title_width, rect.height()),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            "歌名/歌手",
        )

        w += title_width
        album_width = int(text_width * 0.32)
        painter.drawText(
            QRect(w, 0, album_width, rect.height()),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            "专辑",
        )

        w += album_width
        duration_width = int(text_width * 0.08)
        painter.drawText(
            QRect(w, 0, duration_width, rect.height()),
            Qt.AlignmentFlag.AlignCenter,
            "时长",
        )
