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
    try:
        if not destination_folder.exists():
            _mkdir(destination_folder)
            repo_url = f"https://github.com/{organization}/{repository}.git"
            # Make a new folder in destination_folder and clone the repo there
            command = [
                "git",
                "clone",
                "--no-checkout",
                repo_url,
                str(destination_folder),
            ]
            subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to clone repository {repo_url}: {e}")
    except Exception as e:
        raise Exception(f"An error occurred while cloning repository {repo_url}: {e}")


def find_first_txt_file(folder_path: Path) -> Optional[Path]:
    folder = Path(folder_path)
    for file in folder.rglob("*.txt"):
        if file.is_file():
            return file
    raise FileNotFoundError(f"No .txt file found in folder {folder_path}")
