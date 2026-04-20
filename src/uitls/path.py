from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def get_file_path(*path):
    return PROJECT_ROOT.joinpath(*path)
