from enum import Enum


class PlayMode(Enum):
    ORDER = "顺序播放"
    RANDOM = "随机播放"
    REPEAT = "单曲循环"


class SongChanged(Enum):
    NEXT = 1
    PREV = 0


class MessageType(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


MUSIC_SUFFIX = [".mp3", ".flac"]
COVER_SiZE = 60
