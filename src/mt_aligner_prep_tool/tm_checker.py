import subprocess
import argparse
from tqdm import tqdm

def check_repo_exists_ssh(org_name, repo_names):
    existing_repos = []
    base_url = "git@github.com:"
    
    for repo_name in tqdm(repo_names, desc="Checking if repositories exits"):
        repo_url = f"{base_url}{org_name}/{repo_name}.git"
        result = subprocess.run(["git", "ls-remote", repo_url], capture_output=True, text=True)
        if result.returncode == 0:
            existing_repos.append(repo_name)
        else:
            # Could add logging or error handling here
            pass 
    return existing_repos

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check for existing GitHub repositories via SSH.')
    parser.add_argument('file', type=str, help='File containing a list of repository names.')
    args = parser.parse_args()
    
    """ Read repo names from the file """
    with open(args.file, 'r') as file:
        repo_names = [line.strip() for line in file if line.strip()]

    """ add TM before ids """
    TM_repo_names = [f"TM{id}" for id in repo_names]
    org_name = "MonlamAI"
    existing_repos = check_repo_exists_ssh(org_name, TM_repo_names)

    """ remove TM from the existing repo names """
    existing_repos = [repo[2:] for repo in existing_repos]

    """ Write the existing repository names to a file """
    with open('existing_TMs.txt', 'w') as file:
        for repo in existing_repos:
            file.write(repo + '\n')

    print("Complete checking for existing repositories.")
