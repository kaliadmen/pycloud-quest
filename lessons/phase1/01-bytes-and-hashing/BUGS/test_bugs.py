"""Bug-hunt tests. They FAIL until you fix the bug in each l01_bugN.py.

Run:  uv run pytest -m bughunt lessons/phase1/01-bytes-and-hashing
Fix the code, not the test.
"""

import hashlib

import pytest
from blobstore import BlobStore, corrupt_one_byte
from l01_bug1 import fingerprint_file
from l01_bug2 import read_blob
from l01_bug3 import scrub

pytestmark = pytest.mark.bughunt


# --- Bug 1 -----------------------------------------------------------------------------
def test_bug1_fingerprint_matches_sha256sum_for_windows_file(tmp_path):
    f = tmp_path / "settings.ini"
    raw = b"[server]\r\nport=8443\r\n"  # saved by Notepad on Windows
    f.write_bytes(raw)
    # `sha256sum settings.ini` (Linux) or `certutil -hashfile settings.ini SHA256` (Windows) says:
    expected = hashlib.sha256(raw).hexdigest()
    assert fingerprint_file(f) == expected


def test_bug1_fingerprint_works_on_binary_files(tmp_path):
    f = tmp_path / "logo.png"
    raw = bytes([0x89, 0x50, 0x4E, 0x47, 0xFF, 0xFE, 0x00, 0x80])
    f.write_bytes(raw)
    assert fingerprint_file(f) == hashlib.sha256(raw).hexdigest()


# --- Bug 2 -----------------------------------------------------------------------------
@pytest.mark.parametrize("attack", ["absolute", "relative"])
def test_bug2_cannot_read_outside_the_store(tmp_path, attack):
    root = tmp_path / "store"
    root.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_bytes(b"db_password=hunter2")
    # Two classic traversal payloads. Neither is a hex digest, so both must be refused up front.
    payload = str(secret) if attack == "absolute" else "abcd/../../../../secret.txt"
    with pytest.raises(ValueError):
        read_blob(root, payload)


def test_bug2_real_blobs_still_work(tmp_path):
    store = BlobStore(root=tmp_path / "store")
    d = store.put(b"legit")
    assert read_blob(store.root, d) == b"legit"


# --- Bug 3 -----------------------------------------------------------------------------
def test_bug3_scrub_finds_corruption(tmp_path):
    store = BlobStore(root=tmp_path / "store")
    good = store.put(b"good")
    bad = store.put(b"bad")
    corrupt_one_byte(store, bad)
    assert scrub(store.root) == [bad]
    assert good not in scrub(store.root)
