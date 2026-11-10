"""
Bug hunt 2: "The blob that wasn't a blob"

An early version of the blob store's path function, before input validation was added.
"""

from pathlib import Path

SHARD_DEPTH = 2
SHARD_WIDTH = 2


def path_for(root: Path, digest: str) -> Path:
    """Map a digest to its file path inside `root`: ab/cd/abcd..."""
    d = digest.lower()
    parts = [d[i * SHARD_WIDTH : (i + 1) * SHARD_WIDTH] for i in range(SHARD_DEPTH)]
    return root.joinpath(*parts, d)


def read_blob(root: Path, digest: str) -> bytes:
    return path_for(root, digest).read_bytes()
