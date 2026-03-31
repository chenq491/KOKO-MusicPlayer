from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QFileDialog, QHBoxLayout, QPushButton, \
    QLineEdit, QSlider, QFrame, QButtonGroup, QRadioButton

from singleton.config import Config
from singleton.themeManager import theme_manager, Theme
from uitls.utils import create_style_label


def create_divider(color=theme_manager.current.bg_color_300, height=1):
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


class SettingPage(QWidget):
    musicDirSelected = Signal(str)
    volumeChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("SettingPage")
        self.setStyleSheet("""
            background: transparent;
            border: none;
        """)

        # 页面标题
        self.title = create_style_label("设置", font_size=14)

        # 页面主要内容区域
        self.main_area = QScrollArea(self)
        self.main_area.setWidgetResizable(True)  # 让内容自动缩放以适应滚动区域宽度
        self.main_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)  # 垂直滚动条显示策略：需要时显示
        self.main_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 不显示水平滚动条

        self.content_widget = SettingsContentWidget(self)
        self.content_widget.musicDirSelected.connect(self.musicDirSelected)
        self.content_widget.volumeChanged.connect(self.volumeChanged)
        self.content_widget.init_config()  # 初始化配置内容

        self.main_area.setWidget(self.content_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 0, 30, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.title)
        main_layout.addWidget(self.main_area)

        self.setLayout(main_layout)
        theme_manager.themeChanged.connect(self.update_style)

    def update_style(self):
        self.title.setStyleSheet(f"color: {theme_manager.current.text_color_300};")
        self.content_widget.update_style()


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
        self.style_setting = StyleSetting(self)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(create_divider())
        main_layout.addWidget(self.select_music_dir_setting)
        main_layout.addWidget(self.music_volume_setting)
        main_layout.addWidget(self.startup_setting)
        main_layout.addWidget(self.style_setting)

    def init_config(self):
        """初始化配置项"""
        self.select_music_dir_setting.music_dir_path_line.setText(Config.get_value('music_dir'))
        self.music_volume_setting.volume_slider.setValue(int(Config.get_value('volume') * 100))

    def update_style(self):
        """更新样式"""
        self.select_music_dir_setting.update_style()
        self.music_volume_setting.update_style()
        self.startup_setting.update_style()
        self.style_setting.update_style()


class SelectMusicDirSetting(QWidget):
    dirSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(50)

        self.label = create_style_label("音乐文件夹")

        self.music_dir_path_line = QLineEdit()
        self.music_dir_path_line.setPlaceholderText("请选择音乐文件夹")
        self.music_dir_path_line.setReadOnly(True)

        self.select_music_dir_button = QPushButton("选择文件夹")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.label, 2)
        main_layout.addWidget(self.music_dir_path_line, 7)
        main_layout.addWidget(self.select_music_dir_button, 1)

        self.update_style()
        self.select_music_dir_button.clicked.connect(self.on_select_music_dir_clicked)

    def update_style(self):
        self.label.setStyleSheet(f"color: {theme_manager.current.text_color_300};")
        self.music_dir_path_line.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {theme_manager.current.bg_color_400};
                color: {theme_manager.current.text_color_200};
                border-radius: 10px;
                padding: 4px 6px;
                font-size: 14px;
                font-weight: bold;
                font-family: Microsoft YaHei;
                background-color: {theme_manager.current.bg_color_300};
            }}
        """)
        self.select_music_dir_button.setStyleSheet("""
            QPushButton {
                background-color: #9295d3;      /* 背景色 */
                border: none;                   /* 无边框 */
                color: #545361;                   /* 文字颜色 */
                padding: 8px 20px;             /* 内边距 */
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

    @Slot()
    def on_select_music_dir_clicked(self):
        """选择音乐文件夹"""
        music_dir = QFileDialog.getExistingDirectory(
            self,  # 父组件
            "请选择音乐文件夹",
            "",  # 默认文件夹
            QFileDialog.Option.ShowDirsOnly  # 只选择文件夹
        )
        if music_dir:
            self.music_dir_path_line.setText(music_dir)
            self.dirSelected.emit(music_dir)


class MusicVolumeSetting(QWidget):
    volumeChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.label = create_style_label("播放音量")

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)

        self.volume_label = QLabel("50%")

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.label, 2)
        main_layout.addWidget(self.volume_slider, 7)
        main_layout.addWidget(self.volume_label, 1)

        self.setLayout(main_layout)

    def update_style(self):
        self.label.setStyleSheet(f"color: {theme_manager.current.text_color_300};")


    def on_volume_changed(self, value):
        """音量变化"""
        self.volumeChanged.emit(value / 100.0)
        self.volume_label.setText(f"{value}%")


class StartUpSetting(QWidget):
    """启动设置"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setting = Config.get_value("startup_setting")

        radio_button_style = f"""
                QRadioButton {{
                    color: {theme_manager.current.text_color_200};
                    font-size: 14px;
                    background: transparent;
                }}

                QRadioButton::indicator {{
                    width: 15px;
                    height: 15px;
                    border-radius: 9px; /* 圆形 */
                    border: 2px solid #3a3f92;
                    background: transparent;
                }}

                QRadioButton::indicator:checked {{
                    background-color: #5a4ae0;
                    border: 2px solid #7a6aff;
                }}

                QRadioButton::indicator:unchecked:hover {{
                    border: 2px solid #7274f3;
                }}
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
        main_layout.addLayout(content_layout, 8)

        self.bind()

    def update_style(self):
        self.label.setStyleSheet(f"color: {theme_manager.current.text_color_300};")

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


class ThemeBlockButton(QPushButton):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(30, 30)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background: {QColor(color).lighter(110).name()};
            }}
            QPushButton:pressed {{
                background: {QColor(color).lighter(120).name()};
            }}
        """)


class StyleSetting(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = create_style_label("样式设置")

        theme_dark = ThemeBlockButton(theme_manager.get_representative_color(Theme.DARK_THEME))
        theme_purple = ThemeBlockButton(theme_manager.get_representative_color(Theme.PURPLE_THEME))
        theme_layout = QHBoxLayout()
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setSpacing(10)
        theme_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        theme_layout.addWidget(create_style_label("主题"))
        theme_layout.addWidget(theme_dark)
        theme_layout.addWidget(theme_purple)
        theme_layout.addStretch(5)

        theme_dark.clicked.connect(lambda: self.theme_change(Theme.DARK_THEME))
        theme_purple.clicked.connect(lambda: self.theme_change(Theme.PURPLE_THEME))

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.label, 2)
        main_layout.addLayout(theme_layout, 8)

    def update_style(self):
        self.label.setStyleSheet(f"color: {theme_manager.current.text_color_300};")

    @Slot()
    def theme_change(self, theme: Theme):
        theme_manager.set_theme(theme)
