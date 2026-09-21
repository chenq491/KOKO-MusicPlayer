from pathlib import Path

from constant import MUSIC_SUFFIX

PROJECT_ROOT = Path(__file__).parent.parent.parent


def get_file_path(*path):
    return PROJECT_ROOT.joinpath(*path)

def get_music_file_paths_in_dir(music_dir: str | None) -> list[Path]:
    """
    获取文件夹内的音乐文件路径
    :param music_dir: str
    :return: files: List[Path]
    """
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

    return files
