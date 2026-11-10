"""
Bug hunt 3: "Scrub says everything is fine"

A standalone nightly scrub job, written by someone in a hurry. It runs against a store laid out
like blobstore.py (SHARD_DEPTH = 2) and is supposed to report every corrupted blob.
"""

import hashlib
from pathlib import Path


def scrub(root: Path) -> list[str]:
    """Return the digests of all blobs whose content no longer matches their name."""
    corrupt = []
    for path in sorted(root.glob("*")):
        if not path.is_file() or path.name.startswith(".tmp-"):
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != path.name:
            corrupt.append(path.name)
    return corrupt
