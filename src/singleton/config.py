import json
import os
from pathlib import Path
from constant import PlayMode


class Config:
    def __init__(self):
        self.file_path = Path(__file__).resolve().parent.parent / "data" / "config.json"
        self._data = {}

        self.load_from_file()

    def load_from_file(self):

        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self._data = json.load(f)
        else:
            # 先写入默认配置
            self._data = {
                'music_dir': '',
                'volume': 0.5,
                'play_mode': PlayMode.ORDER.value,
                'startup_setting': {
                    'keep_last_progress': True,
                    'shuffle_music_list': False
                },
                'style_setting': {
                    'dark_mode': False,
                },
                'immersive_mode_setting': {
                    'panoramic_mode': True,
                }
            }
            self.save()

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self._data, f)

    def get_value(self, key):
        if isinstance(key, str):
            return self._data.get(key)
        else:
            temp = self._data
            for k in key:
                temp = temp.get(k)
            return temp

    def save_value(self, key, value):
        self._data[key] = value
        self.save()

config = Config()