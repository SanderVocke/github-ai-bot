import github_ai_bot.github as github
import github_ai_bot.patches as patches

import tempfile

def submit_pr_from_patch(
        repo_name,
        patch_content,
        user_email,
        description,
        commit_msg,
        branch_name=None,
        base_branch_name=None):

    patchset = patches.create_patchset(patch_content)
    repo = github.connect_to_repository(repo_name)

    if base_branch_name == None:
        base_branch_name = github.default_branch_name(repo)

    parent_sha = github.branch_sha(
                    github.branch_object(repo, base_branch_name)
                                  )

    patchset_paths = set()
    for patch in patchset:
        for p in [patch.source, patch.target]:
            if p != b'/dev/null':
                patchset_paths.add(p)

    with tempfile.TemporaryDirectory() as temp_dir:
        tree = github.sparse_tree_checkout(repo, parent_sha, lambda path: path.encode('ascii') not in patchset_paths, temp_dir)
        patches.apply_patchset(patchset, temp_dir)
        sha = github.sparse_tree_commit(repo, tree, parent_sha, temp_dir, commit_msg)
        branch_name, branch = github.create_new_branch(repo, branch_name, base_branch_name)
        github.update_branch_tip(branch, sha)
        full_description = f"""
Automated PR submitted indirectly by: {user_email}

Description:
{description}
"""
        pr_url = github.create_pull_request(repo, commit_msg, branch_name, base_branch_name, full_description)
        return pr_url