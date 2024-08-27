from .environment_settings import GREPTILE_PRIVATE_KEY

import requests

def greptile_query(message, repo_name, branch_name, github_token):
    url = "https://api.greptile.com/v2/query"
    payload = {
        "messages": [
            {
                "id": "1",
                "content": message,
                "role": "user"
            }
        ],
        "repositories": [
            {
                "remote": "",
                "branch": branch_name,
                "repository": repo_name
            }
        ],
        "sessionId": "1",
        "stream": False,
        "genius": False
    }
    headers = {
        "Authorization": f"Bearer {GREPTILE_PRIVATE_KEY}",
        "Content-Type": "application/json",
        "X-GitHub-Token": github_token
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    return response