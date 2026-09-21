import random
from pathlib import Path

from Logger import logger
from constant import MUSIC_SUFFIX, PlayMode
from singleton.config import config
from entity.songItem import SongItem
from singleton.musicListManager import music_list_manager
from utils.utils import range_loop
from typing import List

def load_music_list_in_dir(music_dir):
    if not music_dir:  # 确保文件夹存在
        raise FileNotFoundError("文件夹不存在！")

    folder_path = Path(music_dir)
    if not folder_path.is_dir():  # 确保为文件夹
        raise Exception("该目录不为文件夹！")

    # 获取歌曲文件路径
    files = []
    try:
        files = [
            f
            for f in folder_path.iterdir()
            if f.is_file() and f.suffix.lower() in MUSIC_SUFFIX
        ]
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

    def __init__(self):
        self._playlist: List[SongItem] = []
        self._current_play_index = -1
        self._current_song_index = -1

        # if config.get_value(["startup_setting", "shuffle_music_list"]):
        #     self.shuffle_music_list()

    def load_play_list_from_config(self, playlist: list):
        logger.info(f"load playlist from config")
        song_items = music_list_manager.get_song_items()
        self._playlist = [song_items[i] for i in playlist]

    def get_playlist(self, index = False):
        if index:
            return [i.idx for i in self._playlist]
        else:
            return self._playlist

    def get_current_play_index(self):
        return self._current_play_index

    def set_current_play_index(self, index: int):
        self._current_play_index = index
        if index < 0 or index >= len(self._playlist):
            return
        self._current_song_index = self._playlist[index].idx

    def get_current_song_item(self):
        return self._playlist[self._current_play_index]

    def get_current_song_index(self):
        return self._current_song_index

    def set_current_song_index(self, index: int):
        self._current_song_index = index

    def reset(self):
        self._playlist = []
        # self._song_list = []
        self._current_play_index = -1
        self._current_song_index = -1
        # if config.get_value("music_dir") != "":
        #     self.set_song_list(load_music_list_in_dir(config.get_value("music_dir")))

    def update_playlist(self, play_mode: PlayMode):
        logger.info(f"update playlist, current song index: {self._current_song_index + 1}, current play mode: {play_mode.value}")
        if play_mode == PlayMode.ORDER:
            # 顺序播放
            play_index = range_loop(self._current_song_index, music_list_manager.get_total_song())
            song_items = music_list_manager.get_song_items()
            self._playlist = [song_items[i] for i in play_index]
        elif play_mode == PlayMode.RANDOM:
            # 随机播放
            play_index = range_loop(self._current_song_index, music_list_manager.get_total_song())
            sublist = play_index[1:]
            random.shuffle(sublist)
            play_index = [play_index[0]] + sublist
            song_items = music_list_manager.get_song_items()
            self._playlist = [song_items[i] for i in play_index]
        elif play_mode == PlayMode.REPEAT:
            # 单曲循环
            self._playlist = [self._playlist[self._current_play_index]]
        self._current_play_index = 0

    def next_song(self):
        """下一首歌"""
        self.set_current_play_index((self._current_play_index + 1) % len(self._playlist))

    def previous_song(self):
        """上一首歌"""
        if self._current_play_index == 0:
            self.set_current_play_index(len(self._playlist) - 1)
        else:
            self.set_current_play_index(self._current_play_index - 1)

play_list_manager = PlayListManager()