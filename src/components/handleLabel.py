from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import QLabel
from assets.svg import guitar_icon_1
from uitls.utils import create_svg_icon


class HandleLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        icon = create_svg_icon(guitar_icon_1, "#6e74c4", 50)
        # self.setPixmap(QPixmap("./assets/guitar.svg"))
        self.setPixmap(icon.pixmap(48, 48))
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.bp_rect = QRect(0, 0, 0, 0)

    def set_geometry(self, width):
        self.setGeometry(QRect(
            width - 24,
            self.bp_rect.top() - 19,
            48, 48
        ))

    def update_bp_rect(self, bp):
        self.bp_rect = QRect(
            bp.mapTo(self.parent(), bp.rect().topLeft()),
            bp.size()
        )
