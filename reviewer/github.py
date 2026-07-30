import os
import requests

def fetch_pr_diff(owner: str, repo: str, pr_number: int, token: str = None) -> str:
    token = token or os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {"Accept": "application/vnd.github.v3.diff"}
    if token:
        headers["Authorization"] = f"token {token}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text