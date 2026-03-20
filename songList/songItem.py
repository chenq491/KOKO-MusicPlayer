from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from uitls.utils import secs_to_str

def get_tag(audio, keys):
    """从不同格式中尝试获取标签值"""
    for key in keys:
        if key in audio:
            val = audio[key]
            if isinstance(val, list):
                return str(val[0]) if val else ""
            return str(val)
    return ""

def load_meta_data(music_file_path):
    """获取音乐文件的元数据（标题、歌手、专辑、时长、封面）"""
    audio = File(music_file_path)
    duration = secs_to_str(audio.info.length)

    # 获取通用信息
    title = get_tag(audio, ['title', 'TIT2', '\xa9nam']) or "未知标题"  # 标题
    artist = get_tag(audio, ['artist', 'TPE1', '\xa9ART']) or "未知歌手"  # 歌手
    album = get_tag(audio, ['album', 'TALB', '\xa9alb']) or "未知专辑"  # 专辑

    # 提取封面(Bytes)
    cover_data = None
    if isinstance(audio, MP3):  # MP3文件
        if audio.tags and "APIC:" in audio.tags:
            apic = audio.tags.getall("APIC")[0]
            cover_data = apic.data
    elif isinstance(audio, FLAC):  # FLAC文件
        if audio.pictures:
            cover_data = audio.pictures[0].data
    elif isinstance(audio, MP4):  # MP4文件
        if 'covr' in audio.tags:
            cover_data = audio['covr'][0]

    return title, artist, album, duration, cover_data


class SongItem:
    def __init__(self, music_file_path, index):
        self.index = index
        self.music_file_path = music_file_path
        self.title, self.artist, self.album, self.duration, self.cover_bytes = load_meta_data(music_file_path)