from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QFileDialog, QHBoxLayout, QPushButton, \
    QLineEdit, QSlider, QFrame, QButtonGroup, QRadioButton

from config import Config


def create_style_label(text, font_size=14, bold=True, color="#3a3f92"):
    label = QLabel(text)
    font = QFont("Microsoft YaHei", font_size)
    font.setBold(bold)
    label.setFont(font)
    label.setStyleSheet(f"color: {color}")
    return label


def create_divider(color="#ccc", height=1):
    """创建一个自定义样式的水平分割线"""
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)  # 水平线
    line.setFrameShadow(QFrame.Shadow.Sunken)  # 可选：Sunken / Plain / Raised
    line.setLineWidth(0)
    line.setMidLineWidth(0)

    # 使用样式表设置颜色和高度
    line.setStyleSheet(f"""
        QFrame {{
            background-color: {color};
            max-height: {height}px;
            min-height: {height}px;
            border: none;
        }}
    """)
    return line


class SettingsContentWidget(QWidget):
    musicDirSelected = Signal(str)
    volumeChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.select_music_dir_setting = SelectMusicDirSetting(self)
        self.select_music_dir_setting.dirSelected.connect(self.musicDirSelected)

        self.music_volume_setting = MusicVolumeSetting(self)
        self.music_volume_setting.volumeChanged.connect(self.volumeChanged)

        self.startup_setting = StartUpSetting(self)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.select_music_dir_setting)
        main_layout.addWidget(create_divider())
        main_layout.addWidget(self.music_volume_setting)
        main_layout.addWidget(self.startup_setting)

    def init_config(self):
        """初始化配置项"""
        self.select_music_dir_setting.music_dir_path_line.setText(Config.get_value('music_dir'))


class SettingsWidget(QWidget):
    musicDirSelected = Signal(str)
    volumeChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            background-color: #e0e1f3;
        """)

        # 页面标题
        self.title = QLabel("设置")

        # 页面主要内容区域
        self.main_area = QScrollArea(self)
        self.main_area.setWidgetResizable(True)  # 让内容自动缩放以适应滚动区域宽度
        self.main_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)  # 垂直滚动条显示策略：需要时显示
        self.main_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 不显示水平滚动条

        self.content_widget = SettingsContentWidget(self)
        self.content_widget.musicDirSelected.connect(self.musicDirSelected)
        self.content_widget.volumeChanged.connect(self.volumeChanged)
        self.content_widget.init_config()

        self.main_area.setWidget(self.content_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.title)
        main_layout.addWidget(self.main_area)

        self.setLayout(main_layout)


class SelectMusicDirSetting(QWidget):
    dirSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.label = create_style_label("音乐文件夹目录：")

        self.music_dir_path_line = QLineEdit()
        self.music_dir_path_line.setPlaceholderText("请选择音乐文件夹")
        self.music_dir_path_line.setReadOnly(True)
        self.music_dir_path_line.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ced4da;
                color: #3a3f92;
                border-radius: 20px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: bold;
                font-family: Microsoft YaHei;
                background-color: #b6b8e2;
            }
        """)

        self.select_music_dir_button = QPushButton("选择文件夹")
        self.select_music_dir_button.clicked.connect(self.on_select_music_dir_clicked)
        self.select_music_dir_button.setStyleSheet("""
            QPushButton {
                background-color: #9295d3;      /* 背景色 */
                border: none;                   /* 无边框 */
                color: #545361;                   /* 文字颜色 */
                padding: 10px 24px;             /* 内边距 */
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                font-weight: bold;
                margin: 4px 2px;
                border-radius: 10px;             /* 圆角 */
            }
            QPushButton:hover {
                background-color: #6e74c4;      /* 悬停时变深 */
            }
            QPushButton:pressed {
                background-color: #4a51b5;      /* 按下时更深 */
            }
        """)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.label)
        main_layout.addWidget(self.music_dir_path_line)
        main_layout.addWidget(self.select_music_dir_button)

        self.setLayout(main_layout)

    @Slot()
    def on_select_music_dir_clicked(self):
        """选择音乐文件夹"""
        music_dir = QFileDialog.getExistingDirectory(
            self,  # 父组件
            "请选择音乐文件夹",
            "",  # 默认文件夹
            QFileDialog.ShowDirsOnly  # 只选择文件夹
        )
        if music_dir:
            self.music_dir_path_line.setText(music_dir)
            self.dirSelected.emit(music_dir)


class MusicVolumeSetting(QWidget):
    volumeChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.label = create_style_label("播放音量：")

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)

        self.volume_label = QLabel("50%")

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.label)
        main_layout.addWidget(self.volume_slider)
        main_layout.addWidget(self.volume_label)

        self.setLayout(main_layout)

    def on_volume_changed(self, value):
        """音量变化"""
        self.volumeChanged.emit(value / 100.0)
        self.volume_label.setText(f"{value}%")


class StartUpSetting(QWidget):
    """启动设置"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setting = Config.get_value("startup_setting")

        radio_button_style = """
                QRadioButton {
                    color: #5c5b69;
                    font-size: 14px;
                    background: transparent;
                }

                QRadioButton::indicator {
                    width: 15px;
                    height: 15px;
                    border-radius: 9px; /* 圆形 */
                    border: 2px solid #3a3f92;
                    background: transparent;
                }

                QRadioButton::indicator:checked {
                    background-color: #5a4ae0;
                    border: 2px solid #7a6aff;
                }

                QRadioButton::indicator:unchecked:hover {
                    border: 2px solid #7274f3;
                }
                """

        self.label = create_style_label("启动设置")

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 是否保存上一次播放进度设置
        keep_last_process_layout = QHBoxLayout()
        keep_last_process_layout.setContentsMargins(0, 0, 0, 0)
        keep_last_process_layout.setSpacing(0)
        self.keep_last_process_button_group = QButtonGroup(self)
        yes = QRadioButton("是")
        no = QRadioButton("否")
        yes.setStyleSheet(radio_button_style)
        no.setStyleSheet(radio_button_style)
        self.keep_last_process_button_group.addButton(yes, 0)
        self.keep_last_process_button_group.addButton(no, 1)
        self.keep_last_process_button_group.button(self.setting["keep_last_progress"]).setChecked(True)  # 设置默认为是
        keep_last_process_layout.addWidget(create_style_label("保留上一次播放进度", font_size=12), 2)
        keep_last_process_layout.addWidget(yes, 1)
        keep_last_process_layout.addWidget(no, 1)
        keep_last_process_layout.addStretch(5)

        content_layout.addLayout(keep_last_process_layout)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.label, 2)
        main_layout.addLayout(content_layout, 14)

        self.bind()

    def bind(self):
        """绑定事件"""
        self.keep_last_process_button_group.idClicked.connect(self.on_keep_last_process_changed)


    @Slot()
    def on_keep_last_process_changed(self, checked_id):
        """修改是否保留上次播放进度设置"""
        if checked_id == self.setting["keep_last_progress"]:
            return
        else:
            self.setting["keep_last_progress"] = checked_id
            Config.save_value("startup_setting", self.setting)
