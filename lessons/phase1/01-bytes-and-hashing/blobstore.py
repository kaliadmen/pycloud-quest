"""
Lesson 01: a content-addressed blob store.

This is the storage engine that Nimbus object storage (Lesson 16) is built on. It stores raw bytes
("blobs") under the name of their own hash. The same idea runs inside Git, Docker/OCI image layers,
backup tools, and the integrity checks of S3 and Azure Blob Storage.

Run it:
    uv run python blobstore.py demo              guided tour, start here
    uv run python blobstore.py put-text "hello"  store some text
    uv run python blobstore.py put FILE          store a file
    uv run python blobstore.py get DIGEST        print a blob (use -o FILE to save it)
    uv run python blobstore.py ls                list blobs
    uv run python blobstore.py stats             count and total size
    uv run python blobstore.py scrub             re-hash everything, report corruption
    uv run python blobstore.py corrupt DIGEST    LAB ONLY: flip one byte on disk to test scrub
    uv run python blobstore.py wipe              delete the whole store

(Run these from inside this lesson's folder, or pass the full path to blobstore.py.)
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import os
import shutil
import sys
import tempfile
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

# =====================================================================================
# KNOBS: change these, predict what happens (PREDICT.md), then run and check.
# =====================================================================================
STORE_DIR = Path(__file__).parent / "blobs"  # where blobs live (git-ignored)
HASH_ALGO = "sha256"  # try: "md5", "sha1", "sha256", "sha512", "blake2b", "sha3_256"
SHARD_DEPTH = 2  # how many folder levels: 0 = all files in one folder, 2 = ab/cd/abcd...
SHARD_WIDTH = 2  # hex characters per folder level (2 hex chars = 256 possible folders)
CHUNK_SIZE = 64 * 1024  # bytes read at a time when hashing a file (64 KiB)
VERIFY_ON_READ = True  # re-hash every blob on read and refuse corrupted data
ATOMIC_WRITES = True  # write to a temp file, then rename into place
# =====================================================================================

TEMP_PREFIX = ".tmp-"  # temp files start with this, so listing can skip them


# --- Errors -------------------------------------------------------------------------
# Custom exception types let callers handle each failure differently. Later, the Nimbus API turns
# BlobNotFound into HTTP 404, InvalidDigest into 400, and CorruptBlob into 500 plus an alert.
class BlobStoreError(Exception):
    """Base class for every blob store error."""


class BlobNotFound(BlobStoreError):
    pass


class InvalidDigest(BlobStoreError):
    pass


class CorruptBlob(BlobStoreError):
    pass


@dataclass(frozen=True)
class StoreStats:
    blob_count: int
    total_bytes: int


class BlobStore:
    """Stores bytes on disk under the hex digest of their own content."""

    def __init__(
        self,
        root: Path = STORE_DIR,
        algo: str = HASH_ALGO,
        shard_depth: int = SHARD_DEPTH,
        shard_width: int = SHARD_WIDTH,
        verify_on_read: bool = VERIFY_ON_READ,
        atomic_writes: bool = ATOMIC_WRITES,
    ) -> None:
        if algo not in hashlib.algorithms_available:
            raise ValueError(f"Unknown hash algorithm {algo!r}")
        self.root = Path(root)
        self.algo = algo
        self.shard_depth = shard_depth
        self.shard_width = shard_width
        self.verify_on_read = verify_on_read
        self.atomic_writes = atomic_writes
        # A digest always has the same length for a given algorithm: sha256 = 32 bytes = 64 hex.
        self.digest_len = len(hashlib.new(algo).hexdigest())

    # --- Hashing ---------------------------------------------------------------------
    def hash_bytes(self, data: bytes) -> str:
        """Return the hex digest of `data`. Hex is just bytes written as text, 2 chars per byte."""
        return hashlib.new(self.algo, data).hexdigest()

    # --- Paths -----------------------------------------------------------------------
    def validate_digest(self, digest: str) -> str:
        """Reject anything that is not exactly a hex digest of the right length.

        SECURITY: the digest becomes part of a filesystem path. If we accepted any string, a request
        for "../../../etc/passwd" would walk out of the store. Allow-listing the exact format is
        stronger than trying to block "bad" characters.
        """
        if not isinstance(digest, str):
            raise InvalidDigest(f"digest must be str, got {type(digest).__name__}")
        d = digest.lower()
        if len(d) != self.digest_len or any(c not in "0123456789abcdef" for c in d):
            raise InvalidDigest(f"not a valid {self.algo} hex digest: {digest!r}")
        return d

    def path_for(self, digest: str) -> Path:
        """Map a digest to its file path. With depth 2, width 2:  ab/cd/abcdef0123..."""
        d = self.validate_digest(digest)
        parts = [
            d[i * self.shard_width : (i + 1) * self.shard_width] for i in range(self.shard_depth)
        ]
        return self.root.joinpath(*parts, d)

    # --- Write -----------------------------------------------------------------------
    def put(self, data: bytes) -> str:
        """Store `data` and return its digest. Storing the same bytes twice stores them once."""
        if isinstance(data, str):
            # The most common Python 3 mistake in this area. Text has no single byte form until you
            # pick an encoding, and different encodings give different bytes and different hashes.
            raise TypeError("put() needs bytes. Encode text first, e.g. text.encode('utf-8')")
        data = bytes(data)
        digest = self.hash_bytes(data)
        path = self.path_for(digest)

        if path.exists():
            return digest  # dedup: same content, same name, nothing to do

        path.parent.mkdir(parents=True, exist_ok=True)
        if self.atomic_writes:
            self._atomic_write(path, data)
        else:
            # Non-atomic: if the program crashes halfway, a half-written file sits under a
            # valid-looking name. Readers would get garbage (or catch it, if they verify).
            path.write_bytes(data)
        return digest

    def _atomic_write(self, final_path: Path, data: bytes) -> None:
        """Write to a temp file in the same folder, flush to disk, then rename over the target.

        Rename within one filesystem is atomic: readers see either no file or the complete file,
        never half of one. Real storage systems do the same thing.
        """
        fd, tmp_name = tempfile.mkstemp(prefix=TEMP_PREFIX, dir=final_path.parent)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())  # ask the OS to really put it on disk, not just in cache
            os.replace(tmp_name, final_path)  # the atomic step
        except BaseException:
            # Clean up the temp file on any failure, including Ctrl+C, then re-raise.
            Path(tmp_name).unlink(missing_ok=True)
            raise

    def put_file(self, path: Path) -> str:
        """Store a file's raw bytes. Always binary mode. BUGS/ shows what text mode does."""
        return self.put(Path(path).read_bytes())

    # --- Read ------------------------------------------------------------------------
    def get(self, digest: str) -> bytes:
        path = self.path_for(digest)
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            raise BlobNotFound(digest) from None
        if self.verify_on_read:
            actual = self.hash_bytes(data)
            # compare_digest takes the same time whether the first or last character differs.
            # Here the digest isn't secret, so it's a habit more than a need. In Lesson 16, when we
            # compare HMAC signatures, a normal == would leak information through timing.
            if not hmac.compare_digest(actual, self.validate_digest(digest)):
                raise CorruptBlob(f"{digest}: content now hashes to {actual}")
        return data

    def exists(self, digest: str) -> bool:
        return self.path_for(digest).is_file()

    def delete(self, digest: str) -> bool:
        path = self.path_for(digest)
        if path.is_file():
            path.unlink()
            return True
        return False

    # --- Whole-store operations ------------------------------------------------------
    def list_digests(self) -> Iterator[str]:
        """Yield every stored digest. rglob walks into the shard folders."""
        if not self.root.exists():
            return
        for p in sorted(self.root.rglob("*")):
            if p.is_file() and not p.name.startswith(TEMP_PREFIX):
                yield p.name

    def stats(self) -> StoreStats:
        count = 0
        total = 0
        for digest in self.list_digests():
            count += 1
            total += self.path_for(digest).stat().st_size
        return StoreStats(count, total)

    def scrub(self) -> list[str]:
        """Re-hash every blob and return the digests whose content no longer matches.

        Real clouds run this constantly in the background ("scrubbing") because disks silently flip
        bits ("bit rot"). Corrupt copies are then repaired from replicas, a later lesson.
        """
        bad: list[str] = []
        for digest in self.list_digests():
            data = self.path_for(digest).read_bytes()
            if not hmac.compare_digest(self.hash_bytes(data), digest):
                bad.append(digest)
        return bad

    def wipe(self) -> None:
        if self.root.exists():
            shutil.rmtree(self.root)


# =====================================================================================
# Lab helper: simulate bit rot. Only ever used on your own store.
# =====================================================================================
def corrupt_one_byte(store: BlobStore, digest: str, offset: int = 0) -> None:
    path = store.path_for(digest)
    raw = bytearray(path.read_bytes())
    if not raw:
        raise ValueError("empty blob, nothing to corrupt")
    offset %= len(raw)
    raw[offset] ^= 0b0000_0001  # flip the lowest bit of one byte
    path.write_bytes(bytes(raw))


# =====================================================================================
# Guided demo
# =====================================================================================
def demo(store: BlobStore) -> None:
    def step(title: str) -> None:
        print(f"\n=== {title} ===")

    step(f"1. Store some text (algo={store.algo}, shard_depth={store.shard_depth})")
    text = "Hello from Nimbus"
    data = text.encode("utf-8")
    print(f"text  : {text!r}  ({len(text)} characters)")
    print(f"bytes : {data!r}  ({len(data)} bytes)")
    d1 = store.put(data)
    print(f"digest: {d1}")
    print(f"path  : {store.path_for(d1).relative_to(store.root.parent)}")

    step("2. Store the exact same bytes again")
    d2 = store.put(data)
    print(f"digest: {d2}")
    print(f"same digest? {d1 == d2}. Same content, same name, stored once (dedup).")

    step("3. Change ONE character")
    d3 = store.put(b"Hello from Nimbu$")
    print(f"digest: {d3}")
    diff_bits = bin(int(d1, 16) ^ int(d3, 16)).count("1")
    print(f"{diff_bits} of {len(d1) * 4} bits changed (the 'avalanche effect', roughly half)")

    step("4. Read it back (verified)")
    print(f"get -> {store.get(d1)!r}")

    step("5. Simulate bit rot: flip one bit on disk")
    corrupt_one_byte(store, d1)
    print(f"scrub found corrupt blobs: {store.scrub()}")
    try:
        store.get(d1)
    except CorruptBlob as e:
        print(f"get refused to return bad data: CorruptBlob({e})")

    step("6. Path traversal attempt")
    try:
        store.get("../../../etc/passwd")
    except InvalidDigest as e:
        print(f"blocked: InvalidDigest({e})")

    step("7. Store stats")
    print(store.stats())
    print("\nNow open PREDICT.md, change a KNOB, predict, and run again. `wipe` resets the store.")


# =====================================================================================
# Command line interface
# =====================================================================================
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Lesson 01 content-addressed blob store")
    p.add_argument("--root", type=Path, default=STORE_DIR, help="store folder")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo", help="guided tour")
    sp = sub.add_parser("put", help="store a file")
    sp.add_argument("file", type=Path)
    sp = sub.add_parser("put-text", help="store a string as UTF-8")
    sp.add_argument("text")
    sp = sub.add_parser("get", help="read a blob")
    sp.add_argument("digest")
    sp.add_argument("-o", "--out", type=Path, help="write to a file instead of the screen")
    sub.add_parser("ls", help="list digests")
    sub.add_parser("stats", help="count and total size")
    sub.add_parser("scrub", help="find corrupted blobs")
    sp = sub.add_parser("corrupt", help="LAB ONLY: flip a bit in a blob")
    sp.add_argument("digest")
    sub.add_parser("wipe", help="delete the whole store")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = BlobStore(root=args.root)
    try:
        match args.cmd:
            case "demo":
                demo(store)
            case "put":
                print(store.put_file(args.file))
            case "put-text":
                print(store.put(args.text.encode("utf-8")))
            case "get":
                data = store.get(args.digest)
                if args.out:
                    args.out.write_bytes(data)
                else:
                    # Show text if it decodes as UTF-8, otherwise show a hex preview.
                    try:
                        print(data.decode("utf-8"))
                    except UnicodeDecodeError:
                        print(f"<{len(data)} binary bytes> {data[:32].hex(' ')} ...")
            case "ls":
                for d in store.list_digests():
                    print(d)
            case "stats":
                s = store.stats()
                print(f"{s.blob_count} blobs, {s.total_bytes} bytes")
            case "scrub":
                bad = store.scrub()
                print(f"{len(bad)} corrupt blob(s)")
                for d in bad:
                    print(f"  CORRUPT {d}")
                return 1 if bad else 0
            case "corrupt":
                corrupt_one_byte(store, args.digest)
                print(f"flipped one bit in {args.digest}. Now try `scrub` and `get`.")
            case "wipe":
                store.wipe()
                print(f"wiped {store.root}")
    except BlobStoreError as e:
        print(f"error: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
