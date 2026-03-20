import json
import os
from tracemalloc import Statistic

from constant import PlayMode


# class Config:
#     def __init__(self):
#         self.FILE_PATH = "config.json"
#
#         self._data = {}
#
#         if os.path.exists(self.FILE_PATH):
#             with open(self.FILE_PATH, "r") as f:
#                 self._data = json.load(f)
#         else:
#             # 先写入默认配置
#             self._data = {
#                 'music_dir': '',
#                 'play_mode': PlayMode.ORDER.value
#             }
#             self.save()
#
#     def save(self):
#         with open(self.FILE_PATH, "w") as f:
#             json.dump(self._data, f)
#
#     def get_value(self, key):
#         return self._data.get(key)
#
#     def save_value(self, key, value):
#         self._data[key] = value
#         self.save()

class Config:
    FILE_PATH = "data/config.json"
    _data = {}

    @classmethod
    def init(cls):
        if os.path.exists(cls.FILE_PATH):
            with open(cls.FILE_PATH, "r") as f:
                cls._data = json.load(f)
        else:
            # 先写入默认配置
            cls._data = {
                'music_dir': '',
                'play_mode': PlayMode.ORDER.value,
                'startup_setting': {
                    'keep_last_progress': 0
                }
            }
            cls.save()

    @classmethod
    def save(cls):
        with open(cls.FILE_PATH, "w") as f:
            json.dump(cls._data, f)

    @classmethod
    def get_value(cls, key):
        if isinstance(key, str):
            return cls._data.get(key)
        else:
            temp = cls._data
            for k in key:
                temp = temp.get(k)
            return temp

    @classmethod
    def save_value(cls, key, value):
        cls._data[key] = value
        cls.save()
