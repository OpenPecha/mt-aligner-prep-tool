import argparse
import os
import shutil 
import subprocess
from pathlib import Path

from tqdm import tqdm

from mt_aligner_prep_tool.config import TM_FILES_PATH
from mt_aligner_prep_tool.pipeline import get_file_content_by_lines

def merge_branch_to_main(repo_name: str, branch_name: str, org_name: str):

    """ Construct the clone URL and directory """
    clone_url = f"git@github.com:{org_name}/{repo_name}.git"
    clone_dir = os.path.join(TM_FILES_PATH, repo_name)

    """ Ensure the directory is clean """
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir)

    """ Clone the repository """
    subprocess.run(["git", "clone", clone_url, clone_dir], check=True)

    """ Checkout the main branch and start the merge without committing """
    subprocess.run(["git", "checkout", "main"], check=True, cwd=clone_dir)
    try:
        subprocess.run(["git", "merge", f"origin/{branch_name}", "--no-commit", "--no-ff", "--allow-unrelated-histories"], check=True, cwd=clone_dir)
        commit_message = f"Merged branch '{branch_name}' into main."
    except subprocess.CalledProcessError:
        """ Handle conflicts by preferring changes from the branch being merged """
        subprocess.run("git diff --name-only --diff-filter=U", shell=True, text=True, cwd=clone_dir)
        conflicted_files = subprocess.check_output(
            "git diff --name-only --diff-filter=U", shell=True, text=True, cwd=clone_dir
        ).splitlines()
        for file in conflicted_files:
            subprocess.run(["git", "checkout", "--theirs", file], check=True, cwd=clone_dir)
            subprocess.run(["git", "add", file], check=True, cwd=clone_dir)
        """ Commit the resolved merge """
        commit_message = f"Merged branch '{branch_name}' into main with incoming changes preferred."
    subprocess.run(["git", "commit", "-m", commit_message], check=True, cwd=clone_dir)

    """ Push the changes back to the remote repository """
    subprocess.run(["git", "push", "origin", "main"], check=True, cwd=clone_dir)
    
def merge_multiple_branches_to_main(
    repo_file_path: Path, branch_name: str, org_name="MonlamAI"
):
    
    """
    Clones a repository from GitHub, merges a specified branch into the main branch,
    automatically resolves conflicts by preferring incoming changes, and allows merging
    of unrelated histories.

    Parameters:
    repo_file_path(Path): file path of txt file containing TM ids names by separated by new lines..
    branch_name (str): Name of the feature branch to merge.
    org_name (str): Name of the organization or user the repository belongs to.
    """
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

