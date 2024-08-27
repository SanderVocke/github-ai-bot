import patch_ng
import io
import logging

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())

def create_patchset(patch_contents):
    logger.debug(f'creating patchset from:\n{patch_contents}')
    return patch_ng.PatchSet(io.BytesIO(patch_contents.encode('utf-8')))

def changes_summary(patchset):
    added = set()
    removed = set()
    modified = set()
    is_addition = lambda patch: patch.source == b'/dev/null' and patch.target != b'/dev/null'
    is_remove = lambda patch: patch.source != b'/dev/null' and patch.target == b'/dev/null'
    for patch in patchset:
        if is_addition(patch):
            added.add(patch.target)
        elif is_remove(patch):
            removed.add(patch.source)
        else:
            modified.add(patch.target)
    return {
        'added': added,
        'removed': removed,
        'modified': modified
    }

def apply_patchset(patchset, directory, strip=0):
    patchset.apply(root=directory, strip=strip)