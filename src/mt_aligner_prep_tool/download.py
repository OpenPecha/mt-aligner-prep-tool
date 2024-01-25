import subprocess
from pathlib import Path
from typing import List

from mt_aligner_prep_tool.config import BO_FILES_PATH, EN_FILES_PATH, _mkdir

ORG = "MonlamAI"


def download_github_repo(
    repository,
    destination_folder: Path,
    organization: str = ORG,
):
    repo_url = f"https://github.com/{organization}/{repository}.git"
    """make a new folder in destination_folder and clone the repo there"""
    command = ["git", "clone", repo_url, str(destination_folder)]
    subprocess.run(command)


def download_tibetan_english_files(ids: List[str]):
    """Download a repository from GitHub using git clone."""
    for id in ids:
        tibetan_id, english_id = f"BO{id}", f"EN{id}"
        tibetan_repo_path = BO_FILES_PATH / tibetan_id
        english_repo_path = EN_FILES_PATH / english_id

        if not tibetan_repo_path.exists():
            _mkdir(BO_FILES_PATH / tibetan_id)
            download_github_repo(tibetan_id, destination_folder=tibetan_repo_path)
        if not english_repo_path.exists():
            _mkdir(EN_FILES_PATH / english_id)
            download_github_repo(english_id, destination_folder=english_repo_path)


if __name__ == "__main__":
    download_tibetan_english_files(["0001", "0002", "0003"])
