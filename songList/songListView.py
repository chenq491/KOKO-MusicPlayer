import time

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, QSize, QRect, Slot, Signal, QPropertyAnimation, \
    QEasingCurve
from PySide6.QtGui import QPixmap, QFontMetrics, QColor, QPen, QPainterPath, QPainter, QFont
from PySide6.QtWidgets import QStyledItemDelegate, QStyle, QListView, QStyleOptionViewItem

from singleton.playListManager import PlayListManager
from uitls.utils import load_default_cover


class MusicListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []  # 音乐信息列表
        self._cover_size = None  # 封面尺寸
        self._total_cover_pixmap = []
        self._cover_pixmap = []

    def load_data(self, cover_size):
        self._data = PlayListManager.get_song_list()
        self._cover_size = cover_size
        self._total_cover_pixmap = self.load_pixmap()
        self._cover_pixmap = list(range(len(self._total_cover_pixmap)))

    def load_pixmap(self):
        cover_pixmap = []

        default = load_default_cover((self._cover_size, self._cover_size), "#bdc3c7")

        for song_item in self._data:
            pixmap = QPixmap()
            pixmap.loadFromData(song_item.cover_bytes)
            if pixmap.isNull():
                cover_pixmap.append(default)
            else:
                pixmap = pixmap.scaled(
                    self._cover_size,
                    self._cover_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                cover_pixmap.append(pixmap)

        return cover_pixmap

    def search_filter(self, key="title", value=""):
        """搜索条件过滤"""
        self.beginResetModel()
        data_list = PlayListManager.get_song_list()
        self._data = []
        self._cover_pixmap = []
        if value is None or value == "":
            self._data = data_list
            self._cover_pixmap = list(range(len(self._total_cover_pixmap)))
        else:
            for i in range(len(data_list)):
                v = getattr(data_list[i], key)
                if value in v:
                    self._data.append(data_list[i])
                    self._cover_pixmap.append(i)
        self.endResetModel()

    def rowCount(self, /, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, /, role=Qt.ItemDataRole.UserRole):
        """获取数据"""
        if not index.isValid():
            return None

        row = index.row()
        item = self._data[row]
        cover = self._total_cover_pixmap[self._cover_pixmap[row]]

        if role == Qt.ItemDataRole.DisplayRole:
            # 默认文本显示
            return "loading...", None
        elif role == Qt.ItemDataRole.DecorationRole:
            return None, None  # 返回图标
        elif role == Qt.ItemDataRole.UserRole:
            return item, cover  # 返回完整数据对象

        return None


class MusicListItemDelegate(QStyledItemDelegate):
    def __init__(self, cover_size, parent=None):
        super().__init__(parent)
        self.cover_size = cover_size
        self.margin = 10
        self.ratio = [0.6, 0.32, 0.08]

    def sizeHint(self, option, index, /):
        return QSize(100, self.cover_size + self.margin * 2)  # 固定每行高度

    def paint(self, painter, option, index):
        painter.save()  # 保存绘画状态，防止污染

        # 绘制背景，选中和悬停状态
        if option.state & QStyle.StateFlag.State_Selected:  # 选中
            painter.fillRect(option.rect, QColor("#adb2e9"))
        elif option.state & QStyle.StateFlag.State_MouseOver:  # 悬停
            painter.fillRect(option.rect, QColor("#d9dbf2"))
        else:
            painter.fillRect(option.rect, QColor("#e9ebfa"))

        text_color = QColor("#4c4e5d")

        # 获取数据
        data, pixmap = index.data(Qt.ItemDataRole.UserRole)
        idx = data.index
        title = data.title
        artist = data.artist
        album = data.album
        duration = data.duration

        """
        绘制索引
        """
        idx_rect = QRect(
            option.rect.left(),
            option.rect.top(),
            int(option.rect.width() * 0.04),
            option.rect.height()
        )
        font = painter.font()
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(idx_rect, Qt.AlignmentFlag.AlignCenter, str(idx + 1))

        """
        绘制封面
        """
        cover_rect = QRect(
            # idx_rect.left(),
            idx_rect.right(),            option.rect.top() + self.margin,
            self.cover_size,
            self.cover_size
        )
        # 圆角
        path = QPainterPath()
        path.addRoundedRect(cover_rect.x(), cover_rect.y(), cover_rect.width(), cover_rect.height(), 10, 10)
        painter.setClipPath(path)
        painter.drawPixmap(cover_rect, pixmap)
        # 边框
        painter.setClipping(False)  # 关闭剪切，以便画边框在圆角轮廓上
        painter.setPen(QPen(QColor("#333"), 2))  # 黑色边框
        painter.setBrush(Qt.BrushStyle.NoBrush)  # 无填充
        painter.drawPath(path)  # 再次绘制路径作为边框

        # 绘制文字信息
        text_height = option.rect.height() - self.margin * 4
        text_width = option.rect.width() - (cover_rect.right() + 15)
        text_top = option.rect.top() + self.margin * 2
        text_left = cover_rect.right() + 15

        """
        绘制歌名
        """
        title_rect = QRect(
            text_left,
            text_top,
            int(text_width * self.ratio[0]),
            int(text_height * 0.6)
        )
        font.setPointSize(12)
        painter.setFont(font)
        painter.setPen(text_color)
        # 简单处理文字过长 (添加省略号)
        fm = QFontMetrics(font)
        elided_title = fm.elidedText(title, Qt.TextElideMode.ElideRight, title_rect.width() - 10)  # 留50px给时长
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, elided_title)

        """
        绘制歌手
        """
        artist_rect = QRect(
            text_left,
            title_rect.bottom() + 2,
            int(text_width * self.ratio[0]),
            text_height
        )
        font.setBold(False)
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(QColor("#7f8c8d"))
        elided_artist = fm.elidedText(artist, Qt.TextElideMode.ElideRight, artist_rect.width() - 10)
        painter.drawText(artist_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, elided_artist)

        """
        绘制专辑名
        """
        album_rect = QRect(
            title_rect.right(),
            text_top,
            int(text_width * self.ratio[1]),
            text_height
        )
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("#4c4e5d"))
        elided_album = fm.elidedText(album, Qt.TextElideMode.ElideRight, album_rect.width())
        painter.drawText(album_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, elided_album)

        """
        绘制时长
        """
        duration_rect = QRect(
            album_rect.right(),
            text_top,
            int(text_width * self.ratio[2]),
            text_height
        )
        painter.drawText(duration_rect, Qt.AlignmentFlag.AlignCenter, duration)

        painter.restore()


class MusicListView(QListView):
    itemDoubleClicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUniformItemSizes(True)  # 开启优化，告诉 Qt 所有行高一样
        self.setMouseTracking(True)  # 开启鼠标追踪，以便绘制悬停效果
        # 滚动模式为像素级
        self.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)
        self.setAutoScroll(False)

        self.sensitivity = 2
        self.cover_size = 60

        self.model = MusicListModel()
        self.setModel(self.model)

        self.setAutoFillBackground(False)
        self.setStyleSheet("background-color: transparent;")

        # 平滑滚动动画
        self._animation = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.setDuration(300)  # 毫秒

        self.doubleClicked.connect(self.on_item_double_clicked)

    def _animate_scroll(self, target):
        scroll_bar = self.verticalScrollBar()
        # 限制目标值在有效范围内
        target = max(0, min(target, scroll_bar.maximum()))
        if self._animation.state() == QPropertyAnimation.State.Running:
            self._animation.stop()
        self._animation.setStartValue(scroll_bar.value())
        self._animation.setEndValue(target)
        self._animation.start()

    def load_data(self):
        self.model.load_data(self.cover_size)
        self.setItemDelegate(MusicListItemDelegate(self.cover_size))

    def set_current(self, idx: int):
        target = self.model.index(idx)
        self.setCurrentIndex(target)

    def get_current(self):
        idx = self.currentIndex()
        data = self.model.data(idx, Qt.ItemDataRole.UserRole)
        return data

    def search(self, value: str):
        self.model.search_filter(value=value)
        # self.setItemDelegate(MusicListItemDelegate(self.cover_size))

    def wheelEvent(self, event):
        event.accept()  # 消费事件，阻止默认滚动

        delta = event.angleDelta().y()  # 鼠标滚动量，单位是1/8度
        scroll_bar = self.verticalScrollBar()
        current_value = scroll_bar.value()  # 当前滚轮值

        # 获取单行高度（假设所有项高度相同）
        item_height = self.sizeHintForRow(0) or 30  # 默认 30

        # 计算要滚动的“行数”（基于 delta）
        lines_to_scroll = delta / 120  # 120 = 一格，即15度
        pixel_delta = lines_to_scroll * item_height  # 鼠标滚动量（像素值）

        target_value = current_value - int(self.sensitivity * pixel_delta)  # 目标值

        self._animate_scroll(target_value)

    def mouseMoveEvent(self, event, /):
        super().mouseMoveEvent(event)

    @Slot()
    def on_item_double_clicked(self, idx):
        data, _ = idx.data(Qt.ItemDataRole.UserRole)
        self.itemDoubleClicked.emit(data.index)
