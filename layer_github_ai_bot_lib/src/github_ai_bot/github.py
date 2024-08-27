from .environment_settings import GITHUB_APP_ID, GITHUB_PRIVATE_KEY
import logging
import github
import os
import glob
import json
import base64

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

def connect_to_repository(repo_name):
    logger.info("Authenticating with GitHub app")
    # github.enable_console_debug_logging()
    # logging.basicConfig(level=logging.DEBUG)
    auth = github.Auth.AppAuth(GITHUB_APP_ID, GITHUB_PRIVATE_KEY)
    gi = github.GithubIntegration(auth=auth,seconds_between_requests=0,seconds_between_writes=0)
    installation = gi.get_installations()[0]
    gh = installation.get_github_for_installation()
    logger.info("Getting repository handle")
    repo = gh.get_repo(repo_name)
    if not repo:
        raise Exception("Could not get a repository handle")
    return repo

def get_branch_names(repo):
    logger.debug("Getting branches")
    return [b.name for b in repo.get_branches()]

def create_new_branch(repo, name=None, base_branch_name=None):
    if not base_branch_name:
        base_branch_name = repo.default_branch
        logger.info(f"Using default base branch {base_branch_name} as base branch, as none supplied")
    base_branch_obj = repo.get_branch(base_branch_name)
    if not base_branch_obj:
        raise Exception(f"Could not find base branch {base_branch_name}")

    branches = get_branch_names(repo)
    if name is None:
        idx = 0
        while name is None or name in branches:
            logger.debug(f'attempt auto-gen branch name {name}')
            name = f'auto-branch-{idx}'
            idx = idx + 1
        logger.info(f"Using auto-generated branch name {name}, as none supplied")

    logger.info(f"Creating branch {name} from {base_branch_name}")
    ref = repo.create_git_ref(ref=f"refs/heads/{name}", sha=base_branch_obj.commit.sha)
    return (name, ref)

def default_branch_name(repo):
    return repo.default_branch

def branch_object(repo, branch_name):
    return repo.get_branch(branch_name)

def branch_sha(branch):
    return branch.commit.sha

def sparse_tree_checkout(repo, sha, file_paths_filter, target_dir):
    logger.debug(f'sparse checkout of {sha} into {target_dir}')
    if not os.path.exists(target_dir):
        raise Exception("Cannot check out into empty dir")
    tree = repo.get_git_tree(sha)
    for tree_item in tree.tree:
        path = tree_item.path
        if not file_paths_filter(path):
            logger.debug(f"Skipping {path}, filtered out")
        logger.debug(f'Attempting to check out {path} into {target_dir}')

        def checkout_contentfile(c):
            if isinstance (c, list):
                for cc in c:
                    checkout_contentfile(cc)
            else:
                full_path = target_dir + '/' + path
                logger.debug(f'full item path: {full_path}')
                full_dir_path = os.path.dirname(full_path)
                os.makedirs(full_dir_path, exist_ok=True)
                if c.type in ['blob', 'file'] and c.content:
                    with open(full_path, 'w') as file: # TODO: set mode
                        content = c.content
                        logger.debug(f'encoding: {c.encoding}. content: {content}')
                        if c.encoding and c.encoding == "base64":
                            content = base64.b64decode(content).decode('utf-8')
                        logger.debug(f"Writing blob tree item {path}")
                        file.write(content)
                else:
                    logger.debug(f'not writing because not blob or no content. type: {c.type}. has content: {c.content != None}')

        contentfile = repo.get_contents(path, ref=sha)
        checkout_contentfile(contentfile)

    globbed = glob.glob("**/*", root_dir=target_dir, recursive=True) + glob.glob("**/.*", root_dir=target_dir, recursive=True)
    logger.debug(f'result of sparse checkout:\n{json.dumps(globbed, indent=2)}')
    return tree

def sparse_tree_commit(repo, parent_tree, parent_sha, checked_out_dir, message):
    logger.debug(f'sparse checkin onto {parent_sha} from {checked_out_dir}')
    if not os.path.exists(checked_out_dir):
        raise Exception("Cannot check in empty dir")

    tree_input_items = []
    candidates = set(glob.glob("**/*", root_dir=checked_out_dir, recursive=True) + \
                     glob.glob("**/.*", root_dir=checked_out_dir, recursive=True))
    for path in candidates:
        full_path = f'{checked_out_dir}/{path}'
        if (not os.path.exists(full_path)) or os.path.isdir(full_path):
            logger.debug(f'skipping inclusion of {path} ({full_path}): not existing or not a file')
            continue
        maybe_parent_items = [i for i in parent_tree.tree if i.path == path]
        maybe_parent_item = (maybe_parent_items[0] if len(maybe_parent_items) > 0 else None)
        mode = (maybe_parent_item.mode if maybe_parent_item else '100644')
        type = (maybe_parent_item.type if maybe_parent_item else 'blob')

        logger.debug(f'including {path} ({full_path}). In parent tree: {maybe_parent_item != None}. Is dir: {os.path.isdir(full_path)}. mode: {mode}. type: {type}.')

        with open(full_path, 'r') as file:
            tree_input_items.append(github.InputGitTreeElement(
                path, mode, type, content=file.read()
            ))

    new_tree = repo.create_git_tree(tree_input_items, base_tree=parent_tree)
    commit = repo.create_git_commit(
        message=message,
        tree=new_tree,
        parents=[repo.get_commit(parent_sha).commit]
    )
    return commit.sha

def update_branch_tip(branch_object, sha):
    branch_object.edit(sha=sha)

def create_pull_request(repo, title, branch_name, base_branch_name, body):
    logger.debug("Creating pull request")
    pr = repo.create_pull(title=title,
                     body=body,
                     head=branch_name,
                     base=base_branch_name)
    return pr.html_url