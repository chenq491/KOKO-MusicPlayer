from mutagen import File
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4

from utils.utils import secs_to_str


def get_tag(audio, keys):
    """从不同格式中尝试获取标签值"""
    for key in keys:
        if key in audio:
            val = audio[key]
            if isinstance(val, list):
                return str(val[0]) if val else ""
            return str(val)
    return ""


def load_cover_bytes(audio):
    """从音乐文件中加载封面数据
    :param audio: 音乐文件路径 或 mutagen 的 File 类
    :return 封面图像的 byte 数据
    """
    if isinstance(audio, str):
        audio = File(audio)

    cover_data = None
    if isinstance(audio, MP3):  # MP3文件
        if audio.tags and "APIC:" in audio.tags:
            apic = audio.tags.getall("APIC")[0]
            cover_data = apic.data
    elif isinstance(audio, FLAC):  # FLAC文件
        if audio.pictures:
            cover_data = audio.pictures[0].data
    elif isinstance(audio, MP4):  # MP4文件
        if "covr" in audio.tags:
            cover_data = audio["covr"][0]
    return cover_data


def get_song_info(music_file_path):
    """获取音乐文件的元数据（标题、歌手、专辑、时长、封面）"""
    audio = File(music_file_path)
    duration = secs_to_str(audio.info.length)

    # 获取通用信息
    title = get_tag(audio, ["title", "TIT2", "\xa9nam"]) or "未知标题"  # 标题
    artist = get_tag(audio, ["artist", "TPE1", "\xa9ART"]) or "未知歌手"  # 歌手
    album = get_tag(audio, ["album", "TALB", "\xa9alb"]) or "未知专辑"  # 专辑

    # 提取封面(Bytes)
    cover_data = load_cover_bytes(audio)

    return title, artist, album, duration, cover_data
