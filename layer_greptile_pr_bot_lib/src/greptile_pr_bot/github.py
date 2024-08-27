from .environment_settings import GITHUB_APP_ID, GITHUB_PRIVATE_KEY
import logging
import github
import os
import glob
import json

logger = logging.getLogger(__name__)

def connect_to_repository(repo_name):
    logger.info("Authenticating with GitHub app")
    auth = github.Auth.AppAuth(GITHUB_APP_ID, GITHUB_PRIVATE_KEY)
    gi = github.GithubIntegration(auth=auth)
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
        base_branch = repo.default_branch
        logger.info(f"Using default base branch {base_branch} as base branch, as none supplied")
    base_branch_obj = repo.get_branch(base_branch)
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

    logger.info(f"Creating branch {name} from {base_branch}")
    return repo.create_git_ref(ref=f"refs/heads/{name}", sha=base_branch_obj.commit.sha)

def default_branch(repo):
    return repo.default_branch

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
        logger.debug(f'Checking out {path} into {target_dir}')
        full_path = target_dir + '/' + path
        full_dir_path = os.path.dirname(full_path)
        os.makedirs(full_dir_path)
        content = repo.get_contents(path, ref=sha)
        with open(full_path, 'wb') as file: # TODO: set mode
            file.write(content)
    logger.debug(f"result of sparse checkout:\n{json.dumps(glob.glob("*", root_dir=target_dir, recursive=True), indent=2)}")