import pytest
import glob
import os
import tempfile
import shutil
import sys
import deepdiff
import json

script_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, f'{script_dir}/../src')
from greptile_pr_bot import patches

test_folders = glob.glob(script_dir + "/patch_testcases/*")

def get_directory_tree(directory):
    directory_tree = {}
    for root, dirs, files in os.walk(directory):
        for name in dirs + files:
            path = os.path.relpath(os.path.join(root, name), directory)
            directory_tree[path] = os.path.getsize(os.path.join(root, name))
    return directory_tree

def deep_diff_directories(dir1, dir2):
    t1 = get_directory_tree(dir1)
    t2 = get_directory_tree(dir2)
    diff = deepdiff.DeepDiff(t1, t2, ignore_order=True)

    if diff:
        return str(diff)
    else:
        return None

# Dynamically create test functions
for test_folder in test_folders:
    def dynamic_test(test_folder=test_folder):
        patch_content = None
        with open(f'{test_folder}/patch.txt', 'rb') as file:
            patch_content = file.read()

        patchset = patches.create_patchset(patch_content)

        patches.summarize_changes(patchset)

        temp_dir = tempfile.mkdtemp()
        keep_temp_dir = False

        try:
            try:
                reference = f'{test_folder}/after_reference'
                shutil.copytree(f'{test_folder}/before', temp_dir, dirs_exist_ok=True)
                patches.apply_patchset(patchset, temp_dir)

                diff = deep_diff_directories(temp_dir, reference)
                assert diff == None, f'A diff was found with the reference output. Inspect with e.g: diff -u {reference} {temp_dir}'
            except:
                keep_temp_dir = True
                raise
        finally:
            if not keep_temp_dir:
                shutil.rmtree(temp_dir)


    dynamic_test.__name__ = f'test_patches_{os.path.basename(test_folder)}'
    globals()[dynamic_test.__name__] = dynamic_test
