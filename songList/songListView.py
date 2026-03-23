from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, QSize, QRect, Slot, Signal, QPropertyAnimation, \
    QEasingCurve
from PySide6.QtGui import QFontMetrics, QColor, QPen, QPainterPath, QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QStyle, QListView
from singleton.playListManager import PlayListManager
from theme import theme_manager


class MusicListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []  # 音乐信息列表

    def load_data(self):
        self._data = PlayListManager.get_song_list()

    def search_filter(self, key="title", value=""):
        """搜索条件过滤"""
        # 提示重置数据，用于及时重绘
        self.beginResetModel()

        # 更新数据
        data_list = PlayListManager.get_song_list()
        self._data = []
        if value is None or value == "":
            self._data = data_list
        else:
            for item in data_list:
                v = getattr(item, key)
                if value in v:
                    self._data.append(item)

        # 提示重置数据完成
        self.endResetModel()

    def rowCount(self, /, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, /, role=Qt.ItemDataRole.UserRole):
        """获取数据"""
        if not index.isValid():
            return None

        row = index.row()
        item = self._data[row]

        if role == Qt.ItemDataRole.DisplayRole:
            # 默认文本显示
            return "loading...", None
        elif role == Qt.ItemDataRole.DecorationRole:
            return None, None  # 返回图标
        elif role == Qt.ItemDataRole.UserRole:
            return item  # 返回完整数据对象

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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)  # 开启抗锯齿，边缘更平滑
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)  # 开启图像平滑变换

        # 绘制背景，选中和悬停状态
        if option.state & QStyle.StateFlag.State_Selected:  # 选中
            painter.fillRect(option.rect, QColor(theme_manager.current.bg_color_500))
        elif option.state & QStyle.StateFlag.State_MouseOver:  # 悬停
            painter.fillRect(option.rect, QColor(theme_manager.current.bg_color_300))
        else:
            painter.fillRect(option.rect, QColor(theme_manager.current.bg_color_100))

        text_color = QColor(theme_manager.current.text_color_300)

        # 获取数据
        data = index.data(Qt.ItemDataRole.UserRole)
        idx = data.index
        title = data.title
        artist = data.artist
        album = data.album
        duration = data.duration
        cover = data.cover

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
        if idx == PlayListManager.get_current_song_index():
            font.setPointSize(12)
            painter.setFont(font)
            painter.setPen(text_color)
            painter.drawText(idx_rect, Qt.AlignmentFlag.AlignCenter, "🎵")
        else:
            font.setPointSize(10)
            painter.setFont(font)
            painter.setPen(text_color)
            painter.drawText(idx_rect, Qt.AlignmentFlag.AlignCenter, str(idx + 1))

        """
        绘制封面
        """
        cover_rect = QRect(
            # idx_rect.left(),
            idx_rect.right(), option.rect.top() + self.margin,
            self.cover_size,
            self.cover_size
        )
        # 圆角
        path = QPainterPath()
        path.addRoundedRect(cover_rect.x(), cover_rect.y(), cover_rect.width(), cover_rect.height(), 10, 10)
        # painter.setClipPath(path)
        painter.drawPixmap(cover_rect, cover)
        # 边框
        # painter.setClipping(False)  # 关闭剪切，以便画边框在圆角轮廓上
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
        painter.setPen(theme_manager.current.text_color_100)
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
        painter.setPen(text_color)
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
        """加载列表数据"""
        self.model.load_data()
        self.setItemDelegate(MusicListItemDelegate(self.cover_size))

    def set_current(self):
        """高亮显示当前音乐"""
        target = self.model.index(PlayListManager.get_current_song_index())
        self.setCurrentIndex(target)

    def get_current(self):
        """获取当前音乐"""
        idx = self.currentIndex()
        data = self.model.data(idx, Qt.ItemDataRole.UserRole)
        return data

    def search(self, value: str):
        """搜索功能实现"""
        self.model.search_filter(value=value)

    def scroll_to_current(self):
        """跳转到当前音乐"""
        self.scrollTo(self.model.index(PlayListManager.get_current_song_index()), QListView.ScrollHint.PositionAtCenter)

    def wheelEvent(self, event):
        """实现平滑滚动"""
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

    @Slot()
    def on_item_double_clicked(self, idx):
        """双击音乐事件，播放歌曲"""
        data = idx.data(Qt.ItemDataRole.UserRole)
        self.itemDoubleClicked.emit(data.index)
