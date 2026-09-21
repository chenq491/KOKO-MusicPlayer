import os
import shutil
import sqlite3
import random
from io import BytesIO
from typing import Optional, List, Tuple, Any
from pathlib import Path
import hashlib
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from constant import MUSIC_SUFFIX, COVER_SiZE
from entity.songItem import SongItem
from utils.music_parser import get_song_info
from utils.path import get_file_path, get_music_file_paths_in_dir
from utils.utils import draw_rounded_pixmap, get_file_info
from Logger import logger

class MusicLibraryDB:
    def __init__(self, db_file: Optional[str]):
        self.db_file = db_file
        self.conn: Optional[sqlite3.Connection] = None
        self.cur: Optional[sqlite3.Cursor] = None

    def connect(self):
        """连接数据库"""
        if self.db_file is None:
            return
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row  # 返回字典格式
        self.cur = self.conn.cursor()

    def commit(self):
        if self.conn:
            self.conn.commit()

    def rollback(self):
        if self.conn:
            self.conn.rollback()

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def fetch_all(self, sql: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        self.cur.execute(sql, params)
        return self.cur.fetchall()

    def fetch_one(self, sql: str, params: Tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
        self.cur.execute(sql, params)
        return self.cur.fetchone()

    def delete_by_file_path(self, file_path: str):
        self.cur.execute("DELETE FROM music WHERE file_path = ?", (file_path,))
        self.commit()

    def check_exists(self, file_path: str):
        self.cur.execute("UPDATE music SET is_exists = 1 WHERE file_path = ?", (file_path,))
        self.commit()

    def reset_exists(self):
        self.cur.execute("UPDATE music SET is_exists = 0")
        self.commit()

    def clear_not_exists(self):
        self.cur.execute("DELETE FROM music WHERE is_exists = 0")
        self.commit()
        return self.cur.rowcount

    def __enter__(self):
        """进入时"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时"""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()

    def create(self):
        """创建数据库"""
        self.cur.execute("""
        CREATE TABLE music (
            file_path TEXT PRIMARY KEY,    -- 文件路径 主键
            mtime REAL,  -- 修改时间
            size INTEGER,  -- 文件大小
            title TEXT,  -- 歌曲标题
            artist TEXT,  -- 歌手
            album TEXT,  -- 专辑
            duration TEXT,  -- 歌曲时间
            cover_hash TEXT,       -- 封面图片md5，用于去重；NULL=无封面
            cover_path TEXT,       -- 缓存封面的相对路径 cache/covers/xxx.jpg
            is_exists INTEGER CHECK(is_exists IN (0,1)) DEFAULT 1  -- 是否仍存在于目录中
        );
        """)
        self.commit()

    def insert_batch(self, data: list):
        """批量插入数据"""
        self.cur.executemany("""
        INSERT INTO music(file_path, mtime, size, title, artist, album, duration, cover_hash, cover_path, is_exists)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        self.commit()


class MusicListManager:
    """音乐列表管理器"""

    def __init__(self, music_dir: Optional[str] = None, db_file: Optional[str] = None):
        self.music_dir = music_dir
        self.music_db_file = db_file
        self.song_items: List[SongItem] = []
        self.is_changed = False  # 与上次相比，音乐目录内容是否改变

        with open(str(get_file_path("src", "assets", "default_cover.png")), "rb") as f:
            self.default_cover = f.read()

        self.cover_dir_cache = get_file_path("src", "data", "cover_cache")

    def set_music_dir(self, music_dir: str):
        self.music_dir = music_dir

    def add_music_info(self, music_file_path: str):
        """获取一首歌的所有信息"""
        # TODO 可以优化cover_bytes项
        title, artist, album, duration, cover_bytes = (
            get_song_info(music_file_path)
        )
        mtime, size = get_file_info(music_file_path)

        if cover_bytes is None:
            cover_bytes = self.default_cover

        cover_hash = hashlib.new("md5", bytes(cover_bytes)).hexdigest()  # 图片哈希

        # 获取 cover Qpixmap
        cover = QPixmap()
        cover.loadFromData(cover_bytes)
        cover = cover.scaled(
            COVER_SiZE,
            COVER_SiZE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # 保存缓存图片
        cover_file = self.cover_dir_cache / f"{cover_hash}.jpg"
        if not cover_file.exists():
            cover.save(str(cover_file), "JPEG")

        return mtime, size, title, artist, album, duration, cover_hash, str(cover_file), cover

    def init_music_info_list(self):
        """初始化音乐信息存储，更改音乐目录时调用"""
        self.song_items = []

        logger.info("initialize music infomation storage")
        files = get_music_file_paths_in_dir(self.music_dir)

        # 创建封面缓存文件夹
        logger.info("create music cover cache directory")
        cover_cache_dir = get_file_path("src", "data", "cover_cache")
        if cover_cache_dir.exists():
            shutil.rmtree(cover_cache_dir)
        cover_cache_dir.mkdir(parents=True, exist_ok=True)

        # 逐个添加歌曲信息
        data = []
        for idx, f in enumerate(files):
            music_file_path = str(f)

            info = self.add_music_info(music_file_path)

            # 添加到数据库的信息
            data.append((music_file_path, *info[:-1], 1))

            cover = draw_rounded_pixmap(info[-1])
            song_item = SongItem(idx, music_file_path, info[2], info[3], info[4],info[5], cover)
            self.song_items.append(song_item)

        self.create_music_library(data)

    def load_music_info_from_db(self):
        """从数据库加载音乐信息"""
        logger.info("load and update music infomation from database")
        self.song_items = []
        data = []
        files = get_music_file_paths_in_dir(self.music_dir)
        with MusicLibraryDB(self.music_db_file) as db:
            for idx, f in enumerate(files):
                music_file_path = str(f)
                res = db.fetch_one("SELECT * FROM music WHERE file_path=?", (music_file_path,))
                if res is None:  # 如果数据库中没有歌曲信息
                    logger.info(f"song add: {music_file_path}")
                    self.is_changed = True
                    # 添加歌曲信息
                    info = self.add_music_info(music_file_path)
                    data.append((music_file_path, *info[:-1], 1))
                    cover = draw_rounded_pixmap(info[-1])
                    song_item = SongItem(idx, music_file_path, info[2], info[3], info[4],info[5], cover)
                else:  # 数据库中存在歌曲信息
                    mtime, size = get_file_info(music_file_path)
                    if mtime != res["mtime"] or size != res["size"]:
                        # 歌曲文件发生修改，删除该数据重新加入
                        logger.info(f"song modified: {music_file_path}")
                        self.is_changed = True
                        db.delete_by_file_path(music_file_path)

                        info = self.add_music_info(music_file_path)
                        data.append((music_file_path, *info[:-1], 1))
                        cover = draw_rounded_pixmap(info[-1])
                        song_item = SongItem(idx, music_file_path, info[2], info[3], info[4],info[5], cover)
                    else:
                        # 确认该数据存在
                        db.check_exists(music_file_path)
                        # 从数据库中加载信息
                        cover = QPixmap(str(res["cover_path"]))
                        cover = draw_rounded_pixmap(cover)
                        song_item = SongItem(idx, music_file_path, res["title"], res["artist"], res["album"],res["duration"], cover)
                self.song_items.append(song_item)
            # 添加新增的歌曲数据
            db.insert_batch(data)
            # 清空不存在的歌曲数据
            count = db.clear_not_exists()
            logger.info(f"delete not exits songs: {count}")

            # 重置存在字段
            db.reset_exists()


    def create_music_library(self, data: list):
        """创建音乐信息数据库"""
        logger.info("create music infomation database...")
        if self.music_db_file is None:
            logger.warning("please provide music infomation database file path!")
            return
        # 如果数据库存在则删除
        if os.path.exists(self.music_db_file):
            os.remove(self.music_db_file)
        with MusicLibraryDB(self.music_db_file) as db:
            db.create()
            db.insert_batch(data)

    def shuffle_music_list(self):
        """打乱音乐列表"""
        pass
        # indices = list(range(len(self.song_items)))  # 映射索引
        # random.shuffle(indices)  # 打乱索引
        # new_song_list = [0] * len(self.song_items)
        # for i in range(len(self.song_items)):
        #     song_item = self.song_items[i]
        #     song_item.index = indices[i]
        #     new_song_list[indices[i]] = song_item
        #     self._playlist[i] = indices[self._playlist[i]]
        #
        # self._song_list = new_song_list
        # self._current_song_index = indices[self._current_song_index]
        # global_signal_bus.song_list_shuffled_emit()  # 发射信号刷新视图

    def get_total_song(self):
        return len(self.song_items)

    def get_song_items(self):
        return self.song_items


music_list_manager = MusicListManager(
    db_file=str(get_file_path("src", "data", "music_library.db")),
)
