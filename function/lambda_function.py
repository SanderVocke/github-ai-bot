import json
import boto3
import hmac
import hashlib
import base64
import os
from github import Github
from github import InputGitAuthor

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('DYNAMODB_TABLE'))

# Load GitHub credentials from environment variables
GITHUB_APP_ID = os.getenv('GITHUB_APP_ID')
GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY')

def lambda_handler(event, context):
    body = json.loads(event['body'])

    # Extract details from the request body
    patch_content = body['patch_content']
    branch_name = body['branch_name']
    user_email = body['user_email']
    description = body['description']
    repo_name = body['repo_name']

    # Authenticate as GitHub App
    github = Github(GITHUB_APP_ID, GITHUB_PRIVATE_KEY)

    # Get the repository
    repo = github.get_repo(repo_name)

    # Create a new branch
    base_branch = repo.get_branch('main')
    ref = repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_branch.commit.sha)

    # Apply the patch
    contents = repo.get_contents("/", ref=branch_name)
    for content in contents:
        repo.update_file(content.path, description, patch_content, content.sha, branch=branch_name, author=InputGitAuthor('GitHub Bot', user_email))

    # Create a pull request
    pr = repo.create_pull(title="Automated PR by GitHub Bot",
                          body=description,
                          head=branch_name,
                          base="main")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f"Pull Request created: {pr.html_url}"
        })
    }
