from pathlib import Path

from PySide6.QtCore import Signal

from singleton.config import Config
from constant import PlayMode, MUSIC_SUFFIX
from singleton.globalSignalBus import global_signal_bus
from songList.songItem import SongItem
from uitls.utils import range_loop
import random


def load_music_list_in_dir(music_dir):
    if not music_dir:  # 确保文件夹存在
        raise FileNotFoundError("文件夹不存在！")

    folder_path = Path(music_dir)
    if not folder_path.is_dir():  # 确保为文件夹
        raise Exception("该目录不为文件夹！")

    # 获取歌曲文件路径
    files = []
    try:
        files = [f for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() in MUSIC_SUFFIX]
    except Exception as e:
        print(f"ERROR: 读取文件夹出错：{e}")

    song_item_list = []
    idx = 0
    for f in files:
        song_item = SongItem(str(f), idx)
        song_item_list.append(song_item)
        idx += 1

    return song_item_list


class PlayListManager:
    """播放列表管理"""
    _playlist = []  # 索引列表
    _current_play_index = -1
    _song_list = []  # songItem 列表
    _current_song_index = -1

    @classmethod
    def init(cls):
        if Config.get_value('music_dir') == "":
            return

        cls.set_song_list(load_music_list_in_dir(Config.get_value('music_dir')))
        cls.set_playlist(Config.get_value('play_progress')['play_list'])
        cls.set_current_play_index(Config.get_value('play_progress')['current_play_index'])

    @classmethod
    def set_playlist(cls, playlist: list):
        cls._playlist = playlist

    @classmethod
    def get_playlist(cls):
        return cls._playlist

    @classmethod
    def set_song_list(cls, song_list: list):
        cls._song_list = song_list

    @classmethod
    def get_song_list(cls):
        return cls._song_list

    @classmethod
    def get_current_play_index(cls):
        return cls._current_play_index

    @classmethod
    def set_current_play_index(cls, index: int):
        cls._current_play_index = index
        if index < 0 or index >= len(cls._playlist):
            return
        cls._current_song_index = cls._playlist[index]

    @classmethod
    def get_current_song_item(cls):
        return cls._song_list[cls._current_song_index]

    @classmethod
    def get_current_song_index(cls):
        return cls._current_song_index

    @classmethod
    def set_current_song_index(cls, index: int):
        cls._current_song_index = index

    @classmethod
    def get_total_song(cls):
        return len(cls._song_list)

    @classmethod
    def reset(cls):
        cls._playlist = []
        cls._song_list = []
        cls._current_play_index = -1
        cls._current_song_index = -1
        if Config.get_value('music_dir') != "":
            cls.set_song_list(load_music_list_in_dir(Config.get_value('music_dir')))

    @classmethod
    def update_playlist(cls, play_mode: PlayMode):
        if play_mode == PlayMode.ORDER:
            # 顺序播放
            cls._playlist = range_loop(cls._current_song_index, len(cls._song_list))
        elif play_mode == PlayMode.RANDOM:
            # 随机播放
            cls._playlist = range_loop(cls._current_song_index, len(cls._song_list))
            sublist = cls._playlist[1:]
            random.shuffle(sublist)
            cls._playlist[1:] = sublist
        elif play_mode == PlayMode.REPEAT:
            # 单曲循环
            cls._playlist = [cls._current_song_index]
        cls._current_play_index = 0

    @classmethod
    def next_song(cls):
        """下一首歌"""
        cls.set_current_play_index((cls._current_play_index + 1) % len(cls._playlist))

    @classmethod
    def previous_song(cls):
        """上一首歌"""
        if cls._current_play_index == 0:
            cls.set_current_play_index(len(cls._playlist) - 1)
        else:
            cls.set_current_play_index(cls._current_play_index - 1)

    @classmethod
    def shuffle_music_list(cls):
        """打乱音乐列表"""
        indices = list(range(len(cls._song_list)))  # 映射索引
        random.shuffle(indices)  # 打乱索引
        new_song_list = [0] * len(cls._song_list)
        for i in range(len(cls._song_list)):
            song_item = cls._song_list[i]
            song_item.index = indices[i]
            new_song_list[indices[i]] = song_item
            cls._playlist[i] = indices[cls._playlist[i]]

        cls._song_list = new_song_list
        cls._current_song_index = indices[cls._current_song_index]
        global_signal_bus.song_list_shuffled_emit()  # 发射信号刷新视图