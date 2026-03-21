import json
import os
from pathlib import Path
from constant import PlayMode

current_script_path = Path(__file__).resolve()
current_dir = current_script_path.parent
print(current_dir)

class Config:
    file_path = Path(__file__).resolve().parent.parent / "data" / "config.json"
    _data = {}

    @classmethod
    def init(cls):

        if os.path.exists(cls.file_path):
            with open(cls.file_path, "r") as f:
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
        with open(cls.file_path, "w") as f:
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
