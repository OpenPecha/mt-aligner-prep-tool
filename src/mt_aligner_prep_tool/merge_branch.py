import requests


def merge_branch_to_main(org_name, repo_name, branch_name, token):
    """
    Merge a specified branch into the main branch of a given GitHub repository.

    Parameters:
    - org_name: Name of the organization or username.
    - repo_name: Name of the repository.
    - branch_name: Name of the branch to merge into main.
    - token: GitHub personal access token with repo permissions.
    """
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
