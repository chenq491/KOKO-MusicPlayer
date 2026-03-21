from PySide6.QtCore import Signal, QSize, QRect, QPropertyAnimation, QEasingCurve, Qt, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QListWidget, QLabel, QVBoxLayout, QListWidgetItem

from bak.songItem import create_pixmap_from_bytes
from singleton.playListManager import PlayListManager


class PlayListPanel(QListWidget):
    """播放列表界面"""
    selectMusic = Signal()

    def __init__(self, playlist: PlayListManager, parent=None):
        super().__init__(parent)

        self.playlist = playlist
        self.w = int(self.parent().width() * .3)
        self.h = int(self.parent().height() * .7)
        self.top = int(self.parent().height() * .1)

        self.anim = None
        self.is_showing = False

        self.setFixedWidth(self.w)
        self.setFixedHeight(self.h)
        self.setVisible(False)  # 初始隐藏

        self.list_panel = QListWidget(self)

        self.list_panel.setWordWrap(True)  # 允许换行
        self.list_panel.setIconSize(QSize(50, 50))
        self.list_panel.itemDoubleClicked.connect(self.on_song_double_clicked)

        header = QLabel("我的播放列表 🎵")
        header.setStyleSheet("""
                    background-color: #4CAF50;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    border-bottom: 1px solid #45a049;
                """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setStyleSheet("""
            background-color: #191a1c;
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(header)
        main_layout.addWidget(self.list_panel)

        self.setLayout(main_layout)

    def show_or_hidden(self):
        """展示或隐藏面板"""
        start_geo = QRect(
            self.parent().width(), self.top,
            self.width(), self.height()
        )
        end_geo = QRect(
            self.parent().width() - self.width(), self.top,
            self.width(), self.height()
        )
        if self.is_showing:
            # 收起，滑到右侧外
            start_geo, end_geo = end_geo, start_geo

        self.setGeometry(start_geo)
        self.setVisible(True)
        self.raise_()  # 确保在最上面

        # 动画
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setStartValue(start_geo)
        self.anim.setEndValue(end_geo)
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

        self.is_showing = not self.is_showing

        if self.is_showing:  # 设置内容
            self.set_content()
            self.set_current()
        else:  # 动画结束后隐藏（仅收起时）
            self.anim.finished.connect(lambda: self.setVisible(False))

    def update_geometry(self):
        """更新面板的位置"""
        rect = self.parent().rect()
        self.setGeometry(
            rect.width(), self.top,  # 位置
            self.width(), self.height()  # 大小
        )

    def set_content(self):
        """设置显示播放列表"""
        if not self.is_showing:
            return

        self.list_panel.clear()
        for song_index in PlayListManager.get_playlist():
            song_item = PlayListManager.get_song_list()[song_index]
            item = QListWidgetItem()
            item.setText(song_item.title)
            item.setIcon(QIcon(create_pixmap_from_bytes(song_item.cover_bytes, (60, 60))))
            item.setSizeHint(QSize(0, 80))
            self.list_panel.addItem(item)

    def set_current(self):
        """设置当前播放歌曲高亮"""
        if not self.is_showing:
            return
        self.list_panel.setCurrentRow(PlayListManager.get_current_play_index())

    @Slot()
    def on_song_double_clicked(self, item: QListWidgetItem):
        """双击播放列表里的音乐"""
        PlayListManager.set_current_play_index(self.list_panel.row(item))
        self.selectMusic.emit()
