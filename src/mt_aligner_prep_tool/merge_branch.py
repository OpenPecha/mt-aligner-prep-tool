import argparse
import os
import shutil 
import subprocess
from pathlib import Path

from tqdm import tqdm

from mt_aligner_prep_tool.config import TM_FILES_PATH
from mt_aligner_prep_tool.pipeline import get_file_content_by_lines


def merge_branch_to_main(repo_name: str, branch_name: str, org_name: str):
    """ssh cloning url"""
    clone_url = f"git@github.com:{org_name}/{repo_name}.git"
    clone_dir = os.path.join(TM_FILES_PATH, repo_name)

    repo_path = TM_FILES_PATH/ repo_name
    if repo_path.exists():
        shutil.rmtree(TM_FILES_PATH/repo_name)
    """ clone the repository """
    subprocess.run(
        ["git", "clone", clone_url, clone_dir], check=True, cwd=TM_FILES_PATH
    )
    
    """ merge branch with main without committing """
    subprocess.run(["git", "checkout", "main"], check=True, cwd=clone_dir)
    subprocess.run(
        ["git", "merge", f"origin/{branch_name}", "--no-commit", "--no-ff"],
        check=True,
        cwd=clone_dir,
    )
    """ Reset and checkout the README.md file to be excluded """
    subprocess.run(
        ["git", "reset", "HEAD", "README.md"],
        check=True,
        cwd=clone_dir,
    )
    subprocess.run(
        ["git", "checkout", "--", "README.md"],
        check=True,
        cwd=clone_dir,
    )

    """ Commit the merge excluding the README.md file """
    subprocess.run(
        ["git", "commit", "-m", f"Merged branch '{branch_name}' into main."],
        check=True,
        cwd=clone_dir,
    )

    """ Push the changes """
    subprocess.run(["git", "push", "origin", "main"], check=True, cwd=clone_dir)



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

