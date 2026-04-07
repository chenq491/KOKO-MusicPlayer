from PySide6.QtCore import QObject, Signal


class GlobalSignalBus(QObject):
    songListShuffled = Signal()

    def song_list_shuffled_emit(self):
        self.songListShuffled.emit()

global_signal_bus = GlobalSignalBus()