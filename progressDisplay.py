from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSlider, QLabel, QApplication
from uitls.utils import ms_to_str

class ProgressDisplay(QWidget):
    songProgressChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(1200, 800)

        # 歌曲进度条
        self.song_progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.song_progress_slider.valueChanged.connect(self.on_song_progress_slider_changed)

        # 歌曲进度数字
        self.song_progress_label = QLabel("00:00 / 00:00")

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.song_progress_slider)
        main_layout.addWidget(self.song_progress_label)

        self.setLayout(main_layout)

    def reset_progress(self):
        """重置进度"""
        self.song_progress_slider.setValue(0)
        self.song_progress_slider.setEnabled(True)
        self.song_progress_label.setText("00:00 / 00:00")

    def update_progress(self, position, duration):
        """更新进度"""
        if duration < 0:
            return

        # 更新进度条
        # TODO 不清楚什么意思，以后再弄明白
        self.song_progress_slider.blockSignals(True)
        self.song_progress_slider.setMaximum(duration)
        self.song_progress_slider.setValue(position)
        self.song_progress_slider.blockSignals(False)

        # 更新时间标签
        self.song_progress_label.setText(f"{ms_to_str(position)} / {ms_to_str(duration)}")

    def on_song_progress_slider_changed(self, value):
        """歌曲进度条值改变"""
        self.songProgressChanged.emit(value)


if __name__ == "__main__":
    app = QApplication([])
    bottom = ProgressDisplay()
    bottom.show()
    app.exec()
