from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout


class LoadingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 透明背景
        self.setWindowFlags(Qt.WindowType.SubWindow)  # 作为子控件

        # 加载文字标签
        self.loading_label = LoadingGIFLabel(self)

        # 布局，让文字居中
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.loading_label)

    def start(self):
        """开始加载动画"""
        self.show()
        self.loading_label.play()

    def stop(self):
        """停止加载动画"""
        self.hide()
        self.loading_label.paused()


class LoadingGIFLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("loading...")
        self.setFixedSize(300, 300)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.movie = QMovie("../assets/loading.gif")

        # 是否加载成功
        if not self.movie.isValid():
            self.setText("Error: cannot loading gif file")
            self.movie = None
        else:
            self.setMovie(self.movie)
            self.movie.setScaledSize(self.size())
            self.movie.start()
            self.movie.setPaused(True)

    def play(self):
        self.movie.setPaused(False)

    def paused(self):
        self.movie.setPaused(True)

    def resizeEvent(self, event, /):
        self.movie.setScaledSize(event.size())
        super().resizeEvent(event)
