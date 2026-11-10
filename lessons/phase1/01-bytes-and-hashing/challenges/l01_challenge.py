"""
Lesson 01 challenges. Replace each `raise NotImplementedError` with your code.

Test them:  uv run pytest -m challenge lessons/phase1/01-bytes-and-hashing
One at a time:  add  -k hash_file_streaming  (or find_duplicates, put_stream)

Rules: standard library only. Read the docstrings; the hints get stronger toward the bottom.
"""

from __future__ import annotations

from pathlib import Path

from blobstore import BlobStore

CHUNK_SIZE = 64 * 1024


def hash_file_streaming(path: Path, algo: str = "sha256", chunk_size: int = CHUNK_SIZE) -> str:
    """Return the hex digest of a file WITHOUT loading the whole file into memory.

    Why: `Path.read_bytes()` on a 20 GB VM disk image needs 20 GB of RAM. Real storage services hash
    uploads piece by piece as they stream in. The test checks your peak memory use.

    Hint 1: hashlib objects have an .update() method you can call many times.
    Hint 2: open the file in binary mode and call f.read(chunk_size) in a loop until it returns b"".
    Hint 3 (Python 3.8+): `while chunk := f.read(chunk_size):` is the idiomatic loop.
    Note: Python 3.11 added hashlib.file_digest(). Write the loop yourself first, then compare.
    """
    raise NotImplementedError("TODO: challenge 1")


def find_duplicates(folder: Path) -> dict[str, list[Path]]:
    """Find files with identical content anywhere under `folder` (recursively).

    Return {digest: [paths...]} containing ONLY digests shared by 2 or more files, with each list
    of paths sorted. Empty files count as content too.

    This is a real tool: run it on your Downloads folder afterwards. It's also exactly how dedup in
    backup systems and cloud storage decides what to store once.

    Hint 1: use your hash_file_streaming().
    Hint 2: Path.rglob("*") walks recursively; skip anything that isn't a file.
    Hint 3: collections.defaultdict(list) makes grouping easy.
    """
    raise NotImplementedError("TODO: challenge 2")


def put_stream(store: BlobStore, path: Path, chunk_size: int = CHUNK_SIZE) -> str:
    """Store a (possibly huge) file into `store` without loading it into memory. Return its digest.

    The puzzle: the blob's file name IS its hash, but you don't know the hash until you've read
    the whole file. Real object stores have the same problem with uploads.

    Requirements (the tests check every one):
      - The stored bytes and returned digest match `store.put(path.read_bytes())`.
      - Use the store's algorithm (store.algo) and its path layout (store.path_for).
      - No temp files left behind, not even when the content already exists (dedup).
      - Readers must never see a half-written blob under its final name.

    Hint 1: copy chunks into a temp file in the store while updating a hash object.
    Hint 2: once you know the digest, os.replace() the temp file to store.path_for(digest).
    Hint 3: the temp file should live inside store.root (same filesystem) so the rename is atomic.
            Look at BlobStore._atomic_write for the pattern, including the cleanup on failure.
    """
    raise NotImplementedError("TODO: challenge 3")
