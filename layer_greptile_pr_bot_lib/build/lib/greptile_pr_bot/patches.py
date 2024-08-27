import patch_ng
import io
import json

def create_patchset(patch_contents):
    return patch_ng.PatchSet(io.BytesIO(patch_contents))

def summarize_changes(patchset):
    for p in patchset:
        print(json.dumps({
            'source': p.source.decode('utf-8'),
            'target': p.target.decode('utf-8'),
            'n': len(p.hunks),
            'hunks': [
                [t.decode('utf-8') for t in h.text] for h in p.hunks
            ]
        }, indent=3))

def apply_patchset(patchset, directory, strip=0):
    patchset.apply(root=directory, strip=strip)