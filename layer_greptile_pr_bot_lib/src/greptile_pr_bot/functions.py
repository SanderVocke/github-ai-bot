import greptile_pr_bot.github as github
import greptile_pr_bot.patches as patches

import tempfile

def submit_pr_from_patch(
        repo_name,
        patch_content,
        user_email,
        description,
        branch_name=None,
        base_branch=None):

    patchset = patches.create_patchset(patch_content)
    repo = github.connect_to_repository(repo_name)
    parent_sha = github.branch_sha(github.default_branch(repo))

    patchset_paths = set()
    for patch in patchset:
        for p in [patch.source, patch.target]:
            if p != b'/dev/null':
                patchset_paths.add(p)

    with tempfile.TemporaryDirectory() as temp_dir:
        github.sparse_tree_checkout(repo, parent_sha, lambda path: path.decode() not in patchset_paths, temp_dir)
        patches.apply_patchset(patchset, temp_dir)




    # # Get branches
    # print("Getting branches...")
    # branches = [b.name for b in repo.get_branches()]
    # print(f"branches: {branches}")

    # # Create a new branch
    # print("Creating branch...")
    # if base_branch is None:
    #     base_branch = repo.default_branch
    #     print(f"Using default base branch {base_branch} as base branch, as none supplied")
    # base_branch_obj = repo.get_branch(base_branch)
    # if branch_name is None:
    #     idx = 0
    #     while branch_name is None or branch_name in branches:
    #         branch_name = f'auto-branch-{idx}'
    #         idx = idx + 1
    #     print(f"Using auto-generated branch name {branch_name}, as none supplied")
    # ref = repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_branch_obj.commit.sha)

    # # Apply the patch
    # print(f"Patch: {patch_content}")
    # print("Applying patch...")
    # diff = unidiff.PatchSet(patch_content)
    # changes = {}

    # for patch in diff:
    #     for hunk in patch:
    #         for line in hunk:
    #             if line.line_type == 'change':
    #                 filepath = patch.path
    #                 if filepath not in changes:
    #                     # Create a file entry if it doesn't exist
    #                     file_contents = repo.get_contents(filepath, ref=branch_name)
    #                     changes[filepath] = {
    #                         'content': file_contents.decoded_content.decode('utf-8'),
    #                         'sha': file_contents.sha
    #                     }
    #                 # Apply the diff line to the file content
    #                 if line.line_type == 'addition':
    #                     changes[filepath]['content'] += line.value
    #                 elif line.line_type == 'deletion':
    #                     changes[filepath]['content'] = changes[filepath]['content'].replace(line.value, '')

    # print(f'changed files: {changes}')

    # # Create a single commit with all changes
    # print("Committing changes...")
    # commit_message = f"Apply patch: {description}"
    # commit_tree = repo.create_git_tree([
    #     github.InputGitTreeElement(
    #         path=filepath,
    #         mode='100644',  # File mode
    #         type='blob',
    #         content=changes[filepath]['content']
    #     ) for filepath in changes
    # ], base_tree=
    #     repo.get_git_tree(base_branch_obj.commit.commit.tree.sha)
    # )

    # commit = repo.create_git_commit(
    #     message=commit_message,
    #     tree=commit_tree.sha,
    #     parents=[base_branch_obj.commit.sha]
    # )

    # # Update the branch to point to the new commit
    # ref.edit(sha=commit.sha)

    # # Create a pull request
    # pr = repo.create_pull(title="Automated PR by GitHub Bot",
    #                       body=description,
    #                       head=branch_name,
    #                       base="main")

    # return {
    #     'statusCode': 200,
    #     'body': json.dumps({
    #         'message': f"Pull Request created: {pr.html_url}"
    #     })
    # }
