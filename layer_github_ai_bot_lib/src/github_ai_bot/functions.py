import github_ai_bot.github as github
import github_ai_bot.patches as patches
import github_ai_bot.greptile as greptile

import tempfile
import logging
import os

logger = logging.getLogger(__name__)

def submit_pr_from_patch(
        repo_name,
        patch_content,
        user_email,
        description,
        commit_msg,
        branch_name=None,
        base_branch_name=None):

    patchset = patches.create_patchset(patch_content)
    repo, _ = github.connect_to_repository(repo_name)

    if base_branch_name == None:
        base_branch_name = github.default_branch_name(repo)

    parent_sha = github.branch_sha(
                    github.branch_object(repo, base_branch_name)
                                  )

    change_types = patches.changes_summary(patchset)
    logger.debug(f"Change types: {change_types}")

    with tempfile.TemporaryDirectory() as temp_dir:
        tree = github.sparse_tree_checkout(
            repo,
            parent_sha,
            lambda path: path.encode('utf-8') in change_types['modified'],
            temp_dir)
        for f in change_types['added']:
            fp = f.decode('utf-8')
            logger.debug("Creating empty file for added file: " + fp)
            with open(os.path.join(temp_dir, fp), 'w') as file:
                file.write('')
        patches.apply_patchset(patchset, temp_dir)
        sha = github.sparse_tree_commit(repo, tree, parent_sha, temp_dir, commit_msg)
        branch_name, branch = github.create_new_branch(repo, branch_name, base_branch_name)
        github.update_branch_tip(branch, sha)
        full_description = f"""
AI-based PR submitted indirectly by: {user_email}

Description:
{description}
"""
        pr_url = github.create_pull_request(repo, commit_msg, branch_name, base_branch_name, full_description)
        return pr_url
    
def greptile_query(message, repo_name, branch_name):
    repo, token = github.connect_to_repository(repo_name)
    if branch_name == None:
        branch_name = github.default_branch_name(repo)
    return greptile.greptile_query(message, repo_name, branch_name, token)