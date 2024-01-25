import subprocess
from pathlib import Path
from typing import List, Optional

from mt_aligner_prep_tool.config import BO_FILES_PATH, EN_FILES_PATH, _mkdir

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


def download_tibetan_english_files(ids: List[str]):
    """Download a repository from GitHub using git clone."""
    for id_ in ids:
        tibetan_id, english_id = f"BO{id_}", f"EN{id_}"
        tibetan_path = BO_FILES_PATH / tibetan_id
        english_path = EN_FILES_PATH / english_id

        clone_github_repo(repository=tibetan_id, destination_folder=tibetan_path)
        clone_github_repo(repository=english_id, destination_folder=english_path)

        tibetan_txt_file = find_first_txt_file(tibetan_path)
        english_txt_file = find_first_txt_file(english_path)

        if tibetan_txt_file and english_txt_file:
            print("Tokenize it")


def find_first_txt_file(folder_path: Path) -> Optional[Path]:
    folder = Path(folder_path)
    for file in folder.rglob("*.txt"):
        if file.is_file():
            return file
    return None


if __name__ == "__main__":
    download_tibetan_english_files(["0001", "0002", "0003"])
