from PySide6.QtCore import Slot, Signal, QPropertyAnimation, QEasingCurve, Qt
from PySide6.QtWidgets import QListWidget, QWidget, QVBoxLayout, QListWidgetItem, QHBoxLayout, \
    QLabel, QLineEdit

from components.loadingWidget import LoadingWidget
from songItem import SongItemWidget, SongItem
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
        self.list_body = ListBody(self)
        self.list_body.itemDoubleClicked.connect(self.on_song_list_item_double_clicked)
        self.list_body.currentRowChanged.connect(self.on_song_list_current_row_changed)

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
        self.list_body.update_display(song_list)

        self.total = len(song_list)
        self.list_title.update_total(self.total)

    def jump2current(self, current_song_index: int):
        """跳转到指定的歌曲项并高亮显示"""
        current_item = self.list_body.item(current_song_index)
        self.list_body.scrollToItem(current_item)
        self.set_current(current_song_index)

    def set_current(self, current_song_index: int):
        """设置被播放音乐高亮"""
        item = self.list_body.item(current_song_index)
        self.list_body.setCurrentItem(item)
        self.list_body.setCurrentRow(current_song_index)
        # widget = self.list_body.itemWidget(item)
        # widget.set_selected()

    @Slot()
    def on_song_list_item_double_clicked(self, item: QListWidgetItem):
        """双击音乐列表的里的歌曲"""
        current_song_index = self.list_body.row(item)
        self.songItemDoubleClicked.emit(current_song_index)

    @Slot()
    def on_song_list_current_row_changed(self, row: int):
        if row < 0:
            return
        item = self.list_body.item(row)
        widget = self.list_body.itemWidget(item)
        if self.current_song_item_widget:
            self.current_song_item_widget.set_unselected()
        widget.set_selected()
        self.current_song_item_widget = widget


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

        self.total_label = QLabel(f"#{str(total)}")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 14, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # 垂直居中显示
        main_layout.addWidget(self.total_label, 2)
        main_layout.addWidget(QLabel("封面"), 3)
        main_layout.addWidget(QLabel("歌名"), 10)
        main_layout.addWidget(QLabel("歌手"), 9)
        main_layout.addWidget(QLabel("专辑"), 14)
        main_layout.addWidget(QLabel("时长"), 3)
        self.setStyleSheet("""
                    QLabel{
                        color:#4c4e5d;
                        font-weight:bold;
                        font-size:13px;
                    }
                """)

    def update_total(self, total: int):
        self.total_label.setText(f"#{str(total)}")


class ListBody(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAutoScroll(False)  # 禁用自动滚动

        self.loading_widget = LoadingWidget(self)
        self.loading_widget.hide()

        # 平滑滚动动画
        self._animation = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.setDuration(300)  # 毫秒

        # 滚动模式为像素级
        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)

        self.sensitivity = 2

        self.setStyleSheet("""
            QListWidget {
                background-color: #e0e1f3;
                border: none;
                color: #626473;
                outline: 0;
                show-decoration-selected: 0;
            }
            QListWidget::item:current {
                border: none;
            }
        """)

    def resizeEvent(self, e, /):
        rect = self.viewport().rect()  # 获取可视区域
        # 计算loading的居中坐标
        x = (rect.width() - self.loading_widget.width()) // 2
        y = (rect.height() - self.loading_widget.height()) // 2
        # 设置loading位置
        self.loading_widget.move(x, y)
        super().resizeEvent(e)

    def add_song_item(self, song_item: SongItem):
        """添加音乐项目到音乐列表中"""
        item = QListWidgetItem()
        widget = SongItemWidget(song_item)
        item.setSizeHint(widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widget)

    def update_display(self, song_list):
        """更新列表展示"""
        self.clear()
        # self.loading_widget.start()

        self.setUpdatesEnabled(False)  # 禁用UI更新，避免每添加一个Item就重绘
        self.blockSignals(True)  # 临时阻断所有信号
        self.setAutoScroll(False)

        try:
            for song_item in song_list:
                self.add_song_item(song_item)
        finally:
            self.blockSignals(False)  # 恢复信号
            self.setUpdatesEnabled(True)  # 恢复UI更新
            self.setAutoScroll(True)
        self.loading_widget.stop()


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

    def _animate_scroll(self, target):
        scroll_bar = self.verticalScrollBar()
        # 限制目标值在有效范围内
        target = max(0, min(target, scroll_bar.maximum()))
        if self._animation.state() == QPropertyAnimation.State.Running:
            self._animation.stop()
        self._animation.setStartValue(scroll_bar.value())
        self._animation.setEndValue(target)
        self._animation.start()


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
        self.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

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
