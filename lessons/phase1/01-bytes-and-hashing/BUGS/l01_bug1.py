"""
Bug hunt 1: "The hashes don't match"

A teammate wrote this helper to fingerprint config files before uploading them to the cloud,
so the server can check nothing changed in transit.
"""

import hashlib
from pathlib import Path


def fingerprint_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file's contents."""
    with open(path, encoding="utf-8") as f:
        contents = f.read()
    return hashlib.sha256(contents.encode("utf-8")).hexdigest()
