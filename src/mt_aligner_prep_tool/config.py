from pathlib import Path


def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path


BASE_PATH = _mkdir(Path.home() / ".mt_files")
BO_FILES_PATH = _mkdir(BASE_PATH / "tibetan_files")
EN_FILES_PATH = _mkdir(BASE_PATH / "english_files")
