import subprocess
from pathlib import Path
from typing import Optional

from mt_aligner_prep_tool.config import _mkdir

ORG = "MonlamAI"


def clone_github_repo(
    repository,
    destination_folder: Path,
    organization: str = ORG,
):
    if not destination_folder.exists():
        _mkdir(destination_folder)
        repo_url = f"https://github.com/{organization}/{repository}.git"
        """make a new folder in destination_folder and clone the repo there"""
        command = ["git", "clone", repo_url, str(destination_folder)]
        subprocess.run(command)


def find_first_txt_file(folder_path: Path) -> Optional[Path]:
    folder = Path(folder_path)
    for file in folder.rglob("*.txt"):
        if file.is_file():
            return file
    return None
