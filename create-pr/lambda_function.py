import json
import boto3
import hmac
import hashlib
import base64
import os
import github
import unidiff

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('DYNAMODB_TABLE'))

# Load GitHub credentials from environment variables
GITHUB_APP_ID = os.getenv('GITHUB_APP_ID')
GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY').strip().replace('\\n', '\n')

def lambda_handler(event, context):
    print(f"Event body: {event['body']}")

    body = json.loads(event['body'])

    # Extract details from the request body
    patch_content = body['patch_content']
    branch_name = body['branch_name'] if 'branch_name' in body else None
    user_email = body['user_email']
    description = body['description']
    repo_name = body['repo_name']
    base_branch = body['base_branch'] if 'base_branch' in body else None

    # Authenticate as GitHub App
    print("Authenticating with GitHub...")
    github.enable_console_debug_logging()
    auth = github.Auth.AppAuth(GITHUB_APP_ID, GITHUB_PRIVATE_KEY)
    gi = github.GithubIntegration(auth=auth)
    installation = gi.get_installations()[0]
    gh = installation.get_github_for_installation()

    # Get the repository
    repo = gh.get_repo(repo_name)

    # Get branches
    print("Getting branches...")
    branches = [b.name for b in repo.get_branches()]
    print(f"branches: {branches}")

    # Create a new branch
    print("Creating branch...")
    if base_branch is None:
        base_branch = repo.default_branch
        print(f"Using default base branch {base_branch} as base branch, as none supplied")
    base_branch_obj = repo.get_branch(base_branch)
    if branch_name is None:
        idx = 0
        while branch_name is None or branch_name in branches:
            branch_name = f'auto-branch-{idx}'
            idx = idx + 1
        print(f"Using auto-generated branch name {branch_name}, as none supplied")
    ref = repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_branch_obj.commit.sha)

    # Apply the patch
    print("Applying patch...")
    diff = unidiff.PatchSet(patch_content)
    changes = {}

    for patch in diff:
        for hunk in patch:
            for line in hunk:
                if line.line_type == 'change':
                    filepath = patch.path
                    if filepath not in changes:
                        # Create a file entry if it doesn't exist
                        file_contents = repo.get_contents(filepath, ref=branch_name)
                        changes[filepath] = {
                            'content': file_contents.decoded_content.decode('utf-8'),
                            'sha': file_contents.sha
                        }
                    # Apply the diff line to the file content
                    if line.line_type == 'addition':
                        changes[filepath]['content'] += line.value
                    elif line.line_type == 'deletion':
                        changes[filepath]['content'] = changes[filepath]['content'].replace(line.value, '')

    print(f'changed files: {changes}')

    # Create a single commit with all changes
    print("Committing changes...")
    commit_message = f"Apply patch: {description}"
    commit_tree = repo.create_git_tree([
        github.InputGitTreeElement(
            path=filepath,
            mode='100644',  # File mode
            type='blob',
            content=changes[filepath]['content']
        ) for filepath in changes
    ], base_tree=
        repo.get_git_tree(base_branch_obj.commit.commit.tree.sha)
    )

    commit = repo.create_git_commit(
        message=commit_message,
        tree=commit_tree.sha,
        parents=[base_branch_obj.commit.sha]
    )

    # Update the branch to point to the new commit
    ref.edit(sha=commit.sha)

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
