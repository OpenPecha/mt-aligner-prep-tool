import argparse
import os
from pathlib import Path

import requests
from tqdm import tqdm

from mt_aligner_prep_tool.pipeline import get_file_content_by_lines


def merge_branch_to_main(repo_name: str, branch_name: str, org_name: str):
    """
    Merge a specified branch into the main branch of a given GitHub repository.

    Parameters:
    - org_name: Name of the organization or username.
    - repo_name: Name of the repository.
    - branch_name: Name of the branch to merge into main.
    - token: GitHub personal access token with repo permissions.
    """

    token = os.environ.get("GITHUB_TOKEN")

    api_url = f"https://api.github.com/repos/{org_name}/{repo_name}/merges"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "base": "main",
        "head": branch_name,
        "commit_message": f"Merging {branch_name} into main",
    }

    response = requests.post(api_url, json=data, headers=headers)
    if response.status_code == 201:
        print(f"Branch '{branch_name}' successfully merged into main.")
    else:
        print(
            f"Failed to merge branch '{branch_name}' into main. Response: {response.text}"
        )


def merge_multiple_branches_to_main(
    repo_file_path: Path, branch_name: str, org_name="MonlamAI"
):
    """get ids from the txt files (by new lines)"""
    repo_ids = get_file_content_by_lines(repo_file_path)

    for repo in tqdm(repo_ids, desc="Merging branches to main"):
        merge_branch_to_main(f"TM{repo}", branch_name, org_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merging multiple branches to main")
    parser.add_argument(
        "file_path",
        type=Path,
        help="TM ids to be added",
    )
    parser.add_argument(
        "--branch_name",
        type=str,
        help="The branch name to merged with main",
    )
    args = parser.parse_args()

    if args.file_path:
        merge_multiple_branches_to_main(args.file_path, args.branch_name)
    else:
        print("Please provide a file path that contains TM ids and branch name")
