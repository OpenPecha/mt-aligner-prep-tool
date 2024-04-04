import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import requests
from github import Github

ORG = "MonlamAI"


def clone_github_repo(
    repository: str,
    destination_folder: Path,
    organization: str = ORG,
):
    if destination_folder.exists():
        shutil.rmtree(destination_folder)
    destination_folder.mkdir(parents=True, exist_ok=True)
    try:
        repo_url = f"git@github.com:{organization}/{repository}.git"
        # Make a new folder in destination_folder and clone the repo there
        command = [
            "git",
            "clone",
            repo_url,
            str(destination_folder),
        ]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:  # noqa
        """could be due to file name too long"""
        clone_github_repo_with_api(repository, destination_folder)
    except Exception as e:
        print(f"An error occurred while cloning repository {repo_url}: {e}")


def clone_github_repo_with_api(
    repository: str, destination_folder: Path, organization: str = ORG
):
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token is None:
        print("GitHub token not found in environment variables.")
        return None

    g = Github(github_token)
    try:

        repo = g.get_repo(f"{organization}/{repository}")
        contents = repo.get_contents("")

        target_file_suffix = ".txt"
        txt_file_name = ""
        for content_file in contents:
            if content_file.name.endswith(target_file_suffix):
                txt_file_name = content_file.name

        # Get the file contents
        file_contents = repo.get_contents(txt_file_name)
        download_file_with_url(
            file_contents.download_url, f"{repository}.txt", destination_folder
        )
    except Exception as error:
        print(f"An error occurred: {error}")
        return None


def download_file_with_url(
    download_url: str, new_downloaded_file_name: str, destination_folder: Path
):

    if download_url is None:
        return
    # Send a GET request to download the file
    response = requests.get(download_url)

    local_file_path = Path(destination_folder) / new_downloaded_file_name
    if response.status_code == 200:
        # Open the local file and save the downloaded content
        with open(local_file_path, "wb") as local_file:
            local_file.write(response.content)
        print(f"File downloaded and saved to {local_file_path}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")


def find_first_txt_file(folder_path: Path) -> Optional[Path]:
    folder = Path(folder_path)
    for file in folder.rglob("*.txt"):
        if file.is_file():
            return file
    raise FileNotFoundError(f"No .txt file found in folder {folder_path}")
