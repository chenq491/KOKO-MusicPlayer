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

from singleton.playListManager import play_list_manager
from singleton.themeManager import theme_manager
from styleTemplate.cardPainter import draw_card
from styleTemplate.styleFontLabel import StyleFontLabel


class PlayListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []  # 音乐信息列表

    def update_data(self):
        # 提示重置数据，用于及时重绘
        self.beginResetModel()
        self._data = play_list_manager.get_playlist()
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
        theme = theme_manager.current
        painter.setPen(Qt.PenStyle.NoPen)
        row_rect = option.rect.adjusted(6, 3, -6, -3)
        if option.state & QStyle.StateFlag.State_Selected:  # 选中
            painter.setBrush(QBrush(QColor(theme.surface_selected)))
            painter.drawRoundedRect(row_rect, 10, 10)
        elif option.state & QStyle.StateFlag.State_MouseOver:  # 悬停
            painter.setBrush(QBrush(QColor(theme.surface_hover)))
            painter.drawRoundedRect(row_rect, 10, 10)

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

        if data.idx == play_list_manager.get_current_song_index():
            title_color = QColor(theme.text_accent)
            artist_color = QColor(theme.text_accent_soft)
        else:
            title_color = QColor(theme.text_strong)
            artist_color = QColor(theme.text_muted)

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
        painter.setPen(title_color)
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
        painter.setPen(artist_color)
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
        theme = theme_manager.current
        self.setStyleSheet(
            f"""
            #MusicList{{
                background: transparent;
                border-top: 1px solid {theme.divider};
            }}
            /* --- 垂直滚动条 --- */
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 6px;       /* 滚动条宽度 */
                border-radius: 3px; /* 整体圆角 */
                margin: 0;
            }}

            /* --- 滑块 (Handle) --- */
            QScrollBar::handle:vertical {{
                background: {theme.scrollbar};
                min-height: 50px;  /* 滑块最小高度，防止太短 */
                border-radius: 3px; /* 滑块圆角 */
            }}

            /* 滑块悬停效果 */
            QScrollBar::handle:vertical:hover {{
                background: {theme.scrollbar_hover};
            }}

            /* --- 上下箭头按钮 (隐藏) --- */
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;       /* 高度设为0即隐藏 */
                background: none;
            }}

            /* --- 点击的轨道区域 (上下空白处) --- */
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
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
        target = self.model.index(play_list_manager.get_current_play_index())
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
        self.itemDoubleClicked.emit(data.idx)


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
    # 宽度固定，不随主窗口宽度变化
    WIDTH = 360
    # 高度按主窗口高度的比例（窗口很矮时用 MIN_HEIGHT 兜底）
    HEIGHT_RATIO = 0.8
    TOP_RATIO = 0.05
    MIN_HEIGHT = 320

    def __init__(self, parent=None):
        super().__init__(parent)
        # 1. 去掉窗口边框
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # 2. 设置窗口背景透明（关键步骤，否则会有白色矩形底色）
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 尺寸不写死，交给 update_geometry() 按主窗口比例算
        self.is_showing = False
        self.hide()

        self.overlay = DimOverly(parent, self)

        # 标题栏
        self.playlist_title = QWidget(self)
        self.playlist_title.setFixedHeight(50)
        title_layout = QVBoxLayout(self.playlist_title)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(StyleFontLabel("播放列表", font_size=14))

        # 列表视图
        self.playlist_view = PlayListView(self)

        # 布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 12)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.playlist_title)
        main_layout.addWidget(self.playlist_view)

        self.update_style()
        theme_manager.themeChanged.connect(self.update_style)

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def panel_size(self):
        """宽度固定，高度按主窗口高度比例算（并做最小/最大兜底）"""
        parent = self.parent()
        height = int(parent.height() * self.HEIGHT_RATIO)
        height = min(max(height, self.MIN_HEIGHT), parent.height())
        width = min(self.WIDTH, parent.width())
        return width, height

    def panel_top(self):
        """垂直方向留白，同样按窗口高度取比例"""
        return int(self.parent().height() * self.TOP_RATIO)

    def shown_rect(self):
        """展开后的几何：贴右侧、垂直居中偏上"""
        width, height = self.panel_size()
        return QRect(
            self.parent().width() - width,
            self.panel_top(),
            width,
            height,
        )

    def hidden_rect(self):
        """收起后的几何：整体滑到窗口右侧外"""
        width, height = self.panel_size()
        return QRect(
            self.parent().width(),
            self.panel_top(),
            width,
            height,
        )

    def update_geometry(self):
        """主窗口尺寸/位置变化时，重算面板的位置与高度（宽度固定）"""
        target = self.shown_rect() if self.is_showing else self.hidden_rect()
        if self.anim.state == QPropertyAnimation.State.Running:
            # 动画过程中只改终点，避免面板突然跳一下
            self.anim.setEndValue(target)
        else:
            self.setGeometry(target)
        self.overlay.update_geomoetry()

    def show_or_hidden(self, is_show):
        """展示或隐藏面板"""
        start_geo = self.geometry()
        self.is_showing = is_show
        if is_show:
            self.playlist_view.set_current()
            self.overlay.show()
            self.show()
            end_geo = self.shown_rect()
        else:
            # 收起，滑到右侧外
            end_geo = self.hidden_rect()
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

    def update_style(self):
        """跟随主题刷新标题分隔线与卡片"""
        self.playlist_title.setStyleSheet(
            f"background: transparent; border-bottom: 1px solid {theme_manager.current.divider};"
        )
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 开启抗锯齿

        # 圆角卡片：面板本身是透明窗口，卡片四周留出一点空间给阴影
        draw_card(
            painter,
            self.rect().adjusted(6, 8, -6, -8),
            fill=theme_manager.current.card_bg,
            border=theme_manager.current.divider,
            shadow=theme_manager.current.shadow,
        )


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

    play_list_manager.init()  # 初始化播放管理器

    player = TestWindow()
    player.show()
    sys.exit(app.exec())
