import sys

from PySide6.QtCore import (
    QAbstractListModel,
    QEasingCurve,
    QModelIndex,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QPainter, QPainterPath
from PySide6.QtWidgets import (
    QApplication,
    QListView,
    QMainWindow,
    QStyle,
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
)

from singleton.playListManager import PlayListManager
from singleton.themeManager import theme_manager
from styleTemplate.styleFontLabel import StyleFontLabel


class PlayListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []  # 音乐信息列表

    def update_data(self):
        # 提示重置数据，用于及时重绘
        self.beginResetModel()
        self._data = PlayListManager.get_playlist()
        self.endResetModel()

    def rowCount(self, /, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, /, role=Qt.ItemDataRole.UserRole):
        """获取数据"""
        if not index.isValid():
            return None

        row = index.row()
        item = PlayListManager.get_song_list()[self._data[row]]

        if role == Qt.ItemDataRole.DisplayRole:
            # 默认文本显示
            return "loading...", None
        elif role == Qt.ItemDataRole.DecorationRole:
            return None, None  # 返回图标
        elif role == Qt.ItemDataRole.UserRole:
            return item  # 返回完整数据对象

        return None


class PlayListItemDelegate(QStyledItemDelegate):
    def __init__(self, cover_size, parent=None):
        super().__init__(parent)
        self.cover_size = cover_size
        self.margin = 10
        self.ratio = [0.8, 0.2]

    def sizeHint(self, option, index, /):
        return QSize(100, self.cover_size + self.margin * 2)  # 固定每行高度

    def paint(self, painter: QPainter, option, index):
        painter.save()  # 保存绘画状态，防止污染
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing, True
        )  # 开启抗锯齿，边缘更平滑
        painter.setRenderHint(
            QPainter.RenderHint.SmoothPixmapTransform, True
        )  # 开启图像平滑变换

        # 绘制选中和悬停状态，背景透明
        if option.state & QStyle.StateFlag.State_Selected:  # 选中
            painter.fillRect(option.rect, theme_manager.current.playlist_selected)
        elif option.state & QStyle.StateFlag.State_MouseOver:  # 悬停
            painter.fillRect(option.rect, theme_manager.current.playlist_hover)

        text_color = QColor(theme_manager.current.text_bold)

        # 获取数据
        data = index.data(Qt.ItemDataRole.UserRole)
        title = data.title
        artist = data.artist
        duration = data.duration
        cover = data.cover
        cover = cover.scaled(
            self.cover_size,
            self.cover_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        """
        绘制封面
        """
        cover_rect = QRect(
            option.rect.left() + 10,
            option.rect.top() + self.margin,
            self.cover_size,
            self.cover_size,
        )
        # 圆角
        path = QPainterPath()
        path.addRoundedRect(
            cover_rect.x(),
            cover_rect.y(),
            cover_rect.width(),
            cover_rect.height(),
            10,
            10,
        )
        # painter.setClipPath(path)
        painter.drawPixmap(cover_rect, cover)

        # 绘制文字信息
        text_height = option.rect.height() - self.margin * 4
        text_width = option.rect.width() - (cover_rect.right() + 5)
        text_top = option.rect.top() + self.margin * 2
        text_left = cover_rect.right() + 5

        """
        绘制歌名
        """
        title_rect = QRect(
            text_left, text_top, int(text_width * self.ratio[0]), int(text_height * 0.6)
        )
        font = painter.font()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(text_color)
        # 简单处理文字过长 (添加省略号)
        fm = QFontMetrics(font)
        elided_title = fm.elidedText(
            title, Qt.TextElideMode.ElideRight, title_rect.width() - 10
        )
        painter.drawText(
            title_rect,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
            elided_title,
        )

        """
        绘制歌手
        """
        artist_rect = QRect(
            text_left,
            title_rect.bottom() + 2,
            int(text_width * self.ratio[0]),
            int(text_height * 0.4),
        )
        font.setBold(False)
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(theme_manager.current.text_light)
        elided_artist = fm.elidedText(
            artist, Qt.TextElideMode.ElideRight, artist_rect.width() - 10
        )
        painter.drawText(
            artist_rect,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
            elided_artist,
        )

        """
        绘制时长
        """
        duration_rect = QRect(
            title_rect.right(), text_top, int(text_width * self.ratio[1]), text_height
        )
        painter.drawText(duration_rect, Qt.AlignmentFlag.AlignCenter, duration)

        painter.restore()


class PlayListView(QListView):
    itemDoubleClicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUniformItemSizes(True)  # 开启优化，告诉 Qt 所有行高一样
        self.setMouseTracking(True)  # 开启鼠标追踪，以便绘制悬停效果
        # 滚动模式为像素级
        self.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)

        self.sensitivity = 3
        self.cover_size = 55

        self.model = PlayListModel()
        self.setModel(self.model)

        self.setAutoFillBackground(False)

        # 平滑滚动动画
        self._animation = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.setDuration(300)  # 毫秒

        self.doubleClicked.connect(self.on_item_double_clicked)
        self.setObjectName("MusicList")
        self.update_style()
        theme_manager.themeChanged.connect(self.update_style)

        self.update_data()

    def update_style(self):
        """设置样式"""
        self.setStyleSheet(
            f"""
            #MusicList{{
                background: transparent;
                border-top: 1px solid {theme_manager.current.list_item_bg};
            }}
            /* --- 垂直滚动条 --- */
            QScrollBar:vertical {{
                border: none;
                background-color: {theme_manager.current.list_item_bg};
                width: 6px;       /* 滚动条宽度 */
                border-radius: 3px; /* 整体圆角 */
                margin: 0;
            }}

            /* --- 滑块 (Handle) --- */
            QScrollBar::handle:vertical {{
                background: {theme_manager.current.slider_bg};
                min-height: 50px;  /* 滑块最小高度，防止太短 */
                border-radius: 3px; /* 滑块圆角 */
            }}

            /* 滑块悬停效果 */
            QScrollBar::handle:vertical:hover {{
                background: {theme_manager.current.slider_progress};
            }}

            /* --- 上下箭头按钮 (隐藏) --- */
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;       /* 高度设为0即隐藏 */
                background: none;
            }}

            /* --- 点击的轨道区域 (上下空白处) --- */
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: {theme_manager.current.playlist_bg};
            }}
        """
        )

    def _animate_scroll(self, target):
        scroll_bar = self.verticalScrollBar()
        # 限制目标值在有效范围内
        target = max(0, min(target, scroll_bar.maximum()))
        if self._animation.state() == QPropertyAnimation.State.Running:
            self._animation.stop()
        self._animation.setStartValue(scroll_bar.value())
        self._animation.setEndValue(target)
        self._animation.start()

    def update_data(self):
        """加载列表数据"""
        self.model.update_data()
        self.setItemDelegate(PlayListItemDelegate(self.cover_size))

    def set_current(self):
        """高亮显示当前音乐"""
        target = self.model.index(PlayListManager.get_current_play_index())
        self.setCurrentIndex(target)
        self.scrollTo(
            target,
            QListView.ScrollHint.PositionAtCenter,
        )

    def get_current(self):
        """获取当前音乐"""
        idx = self.currentIndex()
        data = self.model.data(idx, Qt.ItemDataRole.UserRole)
        return data

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


class DimOverly(QWidget):
    """遮罩层"""

    def __init__(self, parent, target_widget: QWidget):
        super().__init__(parent)
        self.target = target_widget

        # 设置属性
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 背景透明
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # 无边框
        self.setGeometry(self.parent().geometry())  # 覆盖父窗口

        self.hide()

    def update_geomoetry(self):
        self.setGeometry(self.parent().geometry())

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if self.target.isVisible():
            self.target.show_or_hidden(False)


class PlayListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 1. 去掉窗口边框
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # 2. 设置窗口背景透明（关键步骤，否则会有白色矩形底色）
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setFixedWidth(self.parent().width() * 0.3)
        self.setFixedHeight(self.parent().height() * 0.8)
        self.hide()

        self.overlay = DimOverly(parent, self)

        self.playlist_title = QWidget(self)
        self.playlist_title.setFixedHeight(50)
        self.playlist_title.setStyleSheet(
            f"border-bottom: 1px solid {theme_manager.current.slider_bg};"
        )
        title_layout = QVBoxLayout(self.playlist_title)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(StyleFontLabel("播放列表", font_size=14))

        self.playlist_view = PlayListView(self)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 5)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.playlist_title)
        main_layout.addWidget(self.playlist_view)

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def update_geometry(self):
        """更新面板的位置"""
        rect = self.parent().rect()
        self.setGeometry(
            rect.width(),
            self.parent().height() * 0.05,
            self.width(),
            self.height(),  # 位置  # 大小
        )
        self.overlay.update_geomoetry()

    def show_or_hidden(self, is_show):
        """展示或隐藏面板"""
        start_geo = self.geometry()
        if is_show:
            self.playlist_view.set_current()
            self.overlay.show()
            self.show()
            end_geo = QRect(
                self.parent().width() - self.width(),
                self.parent().height() * 0.05,
                self.width(),
                self.height(),
            )
        else:
            # 收起，滑到右侧外
            end_geo = QRect(
                self.parent().width(),
                self.parent().height() * 0.05,
                self.width(),
                self.height(),
            )
            self.anim.finished.connect(self._on_hiden_finished)

        self.setGeometry(start_geo)
        self.setVisible(True)
        self.raise_()  # 确保在最上面

        # 动画
        if self.anim.state == QPropertyAnimation.State.Running:
            self.anim.setEndValue(end_geo)
            self.anim.start()
        else:
            self.anim.setStartValue(start_geo)
            self.anim.setEndValue(end_geo)
            self.anim.start()

    def update_data(self):
        self.playlist_view.update_data()

    def _on_hiden_finished(self):
        self.hide()
        self.overlay.hide()
        self.anim.finished.disconnect()  # 断开连接防止内存泄漏或重复触发

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 开启抗锯齿

        # 绘制一个填充的圆角矩形
        painter.setBrush(QBrush(QColor(theme_manager.current.playlist_bg)))  # 背景色
        painter.setPen(Qt.PenStyle.NoPen)  # 无边框

        # 绘制圆角矩形覆盖整个窗口
        rect = QRect(0, 0, self.width(), self.height())
        painter.drawRoundedRect(rect, 10, 10)


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(1200, 800)
        self.playlistview = PlayListWidget(self)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.playlistview)


if __name__ == "__main__":
    # QApplication.setStyle("Windows")
    app = QApplication(sys.argv)

    PlayListManager.init()  # 初始化播放管理器

    player = TestWindow()
    player.show()
    sys.exit(app.exec())
