from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QFileDialog, QHBoxLayout, QPushButton, \
    QLineEdit, QFrame

from components.styleSlider import StyleSlider
from components.textCheckBox import TextCheckBox
from singleton.config import config
from singleton.themeManager import theme_manager, ThemeMode, ThemeColor
from styleTemplate.styleFontLabel import StyleFontLabel
from uitls.utils import create_style_label


def create_divider(color=theme_manager.current.slider_bg, height=1):
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
        self.title = StyleFontLabel("设置", font_size=14)

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
        self.title.set_color(theme_manager.current.text_bold)
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
        self.immersive_mode_setting = ImmersiveModeSetting(self)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(create_divider())
        main_layout.addWidget(self.select_music_dir_setting)
        main_layout.addWidget(self.music_volume_setting)
        main_layout.addWidget(self.startup_setting)
        main_layout.addWidget(create_divider())
        main_layout.addWidget(self.style_setting)
        main_layout.addWidget(self.immersive_mode_setting)

    def init_config(self):
        """初始化配置项"""
        self.select_music_dir_setting.music_dir_path_line.setText(config.get_value('music_dir'))
        self.music_volume_setting.volume_slider.setValue(int(config.get_value('volume') * 100))

    def update_style(self):
        """更新样式"""
        self.select_music_dir_setting.update_style()
        self.music_volume_setting.update_style()
        self.startup_setting.update_style()
        self.style_setting.update_style()
        self.immersive_mode_setting.update_style()


class SelectMusicDirSetting(QWidget):
    dirSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(50)

        self.label = StyleFontLabel("音乐文件夹")

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
        self.label.set_color(theme_manager.current.text_bold)
        self.music_dir_path_line.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {theme_manager.current.list_item_hover};
                color: {theme_manager.current.text_normal};
                border-radius: 10px;
                padding: 4px 6px;
                font-size: 14px;
                font-weight: bold;
                font-family: Microsoft YaHei;
                background-color: {theme_manager.current.line_edit_bg};
            }}
        """)
        self.select_music_dir_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.current.button_bg};      /* 背景色 */
                border: none;                   /* 无边框 */
                color: {theme_manager.current.text_bold};                   /* 文字颜色 */
                padding: 8px 20px;             /* 内边距 */
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                font-weight: bold;
                margin: 4px 2px;
                border-radius: 10px;             /* 圆角 */
            }}
            QPushButton:hover {{
                background-color: {theme_manager.current.button_hover};      /* 悬停时变深 */
            }}
            QPushButton:pressed {{
                background-color: {theme_manager.current.button_selected};      /* 按下时更深 */
            }}
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

        self.label = StyleFontLabel("播放音量")

        self.volume_slider = StyleSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)

        self.zero_label = StyleFontLabel("0%", font_size=10)
        # self.zero_label.setFixedWidth(20)
        self.zero_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.volume_label = StyleFontLabel("50%", font_size=10)
        self.volume_label.setFixedWidth(30)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.zero_label)
        content_layout.addWidget(self.volume_slider)
        content_layout.addWidget(self.volume_label)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.label, 2)
        main_layout.addLayout(content_layout, 8)

        self.setLayout(main_layout)

    def update_style(self):
        self.label.set_color(theme_manager.current.text_bold)
        self.zero_label.set_color(theme_manager.current.text_bold)
        self.volume_label.set_color(theme_manager.current.text_bold)

    def on_volume_changed(self, value):
        """音量变化"""
        self.volumeChanged.emit(value / 100.0)
        self.volume_label.setText(f"{value}%")


class StartUpSetting(QWidget):
    """启动设置"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setting = config.get_value("startup_setting")

        self.label = StyleFontLabel("启动设置")
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 是否保存上一次播放进度设置
        self.keep_last_process = TextCheckBox(label=StyleFontLabel("保留上一次播放进度", font_size=12, bold=False))
        self.keep_last_process.set_checked(self.setting["keep_last_progress"])

        # 启动时是否打乱音乐列表
        self.shuffle_music_list = TextCheckBox(label=StyleFontLabel("启动时打乱音乐列表", font_size=12, bold=False))
        self.shuffle_music_list.set_checked(self.setting["shuffle_music_list"])

        self.init_ui()
        self.bind()

    def init_ui(self):
        klp_layout = QHBoxLayout()
        klp_layout.addWidget(self.keep_last_process)
        klp_layout.addStretch(1)

        sml_layout = QHBoxLayout()
        sml_layout.addWidget(self.shuffle_music_list)
        sml_layout.addStretch(1)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(40)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.addLayout(klp_layout)
        content_layout.addLayout(sml_layout)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 40, 0, 40)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.label, 2)
        main_layout.addLayout(content_layout, 8)

    def update_style(self):
        self.label.set_color(theme_manager.current.text_bold)
        self.keep_last_process.set_color(theme_manager.current.text_bold)
        self.shuffle_music_list.set_color(theme_manager.current.text_bold)

    def bind(self):
        """绑定事件"""
        self.keep_last_process.stateChanged.connect(self.on_keep_last_process_changed)
        self.shuffle_music_list.stateChanged.connect(self.on_shuffle_music_list_changed)

    @Slot()
    def on_keep_last_process_changed(self, checked):
        """修改是否保留上次播放进度设置"""
        self.setting["keep_last_progress"] = checked
        config.save_value("startup_setting", self.setting)

    @Slot()
    def on_shuffle_music_list_changed(self, checked):
        """修改是否打乱音乐列表设置"""
        self.setting["shuffle_music_list"] = checked
        config.save_value("startup_setting", self.setting)


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

        self.setting = config.get_value("style_setting")

        self.label = StyleFontLabel("样式设置")
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.dark_mode = TextCheckBox(label=StyleFontLabel("暗黑模式", font_size=12, bold=False))
        self.dark_mode.set_checked(self.setting["dark_mode"])

        self.theme_green = ThemeBlockButton(theme_manager.get_representative_color(ThemeColor.GREEN))
        self.theme_purple = ThemeBlockButton(theme_manager.get_representative_color(ThemeColor.PURPLE))

        self.dark_mode.stateChanged.connect(self.on_theme_mode_changed)
        self.theme_green.clicked.connect(lambda: theme_manager.set_theme(None, ThemeColor.GREEN))
        self.theme_purple.clicked.connect(lambda: theme_manager.set_theme(None, ThemeColor.PURPLE))

        self.init_ui()

    def init_ui(self):
        theme_layout = QHBoxLayout()
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setSpacing(10)
        theme_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        theme_layout.addWidget(StyleFontLabel("主题"))
        theme_layout.addWidget(self.theme_green)
        theme_layout.addWidget(self.theme_purple)
        theme_layout.addStretch(5)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(40)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.addWidget(self.dark_mode)
        content_layout.addLayout(theme_layout)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 40, 0, 40)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.label, 2)
        main_layout.addLayout(content_layout, 8)


    def update_style(self):
        self.label.set_color(theme_manager.current.text_bold)
        self.dark_mode.set_color(theme_manager.current.text_bold)

    @Slot()
    def on_theme_mode_changed(self, checked):
        if checked:
            theme_manager.set_theme(ThemeMode.DARK, None)
        else:
            theme_manager.set_theme(ThemeMode.LIGHT, None)
        self.setting["dark_mode"] = checked
        config.save_value("style_setting", self.setting)

    # @Slot()
    # def theme_change(self, theme: Theme):
    #     theme_manager.set_theme(theme)


class ImmersiveModeSetting(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = StyleFontLabel("沉浸模式设置")
        self.setting = config.get_value("immersive_mode_setting")

        # 是否开启全景模式
        self.panoramic_mode = TextCheckBox(label=StyleFontLabel("全景模式", font_size=12, bold=False))
        self.panoramic_mode.set_checked(self.setting["panoramic_mode"])
        self.panoramic_mode.stateChanged.connect(self.on_panoramic_mode_changed)

        self.init_ui()

    def init_ui(self):
        pml = QHBoxLayout()
        pml.setContentsMargins(0, 0, 0, 0)
        pml.setSpacing(0)
        pml.addWidget(self.panoramic_mode)
        pml.addStretch(1)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.label, 2)
        main_layout.addLayout(pml, 8)

    def update_style(self):
        self.label.set_color(theme_manager.current.text_bold)
        self.panoramic_mode.set_color(theme_manager.current.text_bold)

    @Slot()
    def on_panoramic_mode_changed(self, checked):
        """全景模式设置改变"""
        self.setting["panoramic_mode"] = checked
        config.save_value("immersive_mode_setting", self.setting)
