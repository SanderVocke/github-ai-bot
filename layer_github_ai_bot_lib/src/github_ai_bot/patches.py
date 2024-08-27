import patch_ng
import io
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

def create_patchset(patch_contents):
    logger.debug(f'creating patchset from:\n{patch_contents}')
    return patch_ng.PatchSet(io.BytesIO(patch_contents.encode('utf-8')))

def apply_patchset(patchset, directory, strip=0):
    patchset.apply(root=directory, strip=strip)