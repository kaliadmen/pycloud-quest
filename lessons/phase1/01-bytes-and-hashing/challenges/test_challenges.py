"""Challenge tests. They FAIL until you implement l01_challenge.py.

Run:  uv run pytest -m challenge lessons/phase1/01-bytes-and-hashing
"""

import hashlib
import os
import tracemalloc

import pytest
from blobstore import BlobStore
from l01_challenge import find_duplicates, hash_file_streaming, put_stream

pytestmark = pytest.mark.challenge

BIG = 16 * 1024 * 1024  # 16 MiB


@pytest.fixture
def big_file(tmp_path):
    f = tmp_path / "big.bin"
    with open(f, "wb") as out:
        for _ in range(BIG // (1024 * 1024)):
            out.write(os.urandom(1024 * 1024))
    return f


# --- Challenge 1 ----------------------------------------------------------------------
def test_c1_matches_hashlib(tmp_path):
    f = tmp_path / "a.bin"
    f.write_bytes(b"x" * 200_000)
    assert hash_file_streaming(f) == hashlib.sha256(b"x" * 200_000).hexdigest()


def test_c1_empty_file(tmp_path):
    f = tmp_path / "empty"
    f.write_bytes(b"")
    assert hash_file_streaming(f) == hashlib.sha256(b"").hexdigest()


def test_c1_other_algo(tmp_path):
    f = tmp_path / "a.bin"
    f.write_bytes(b"abc")
    assert hash_file_streaming(f, algo="sha512") == hashlib.sha512(b"abc").hexdigest()


def test_c1_chunk_boundaries(tmp_path):
    f = tmp_path / "a.bin"
    data = os.urandom(1000)
    f.write_bytes(data)
    for size in (1, 7, 999, 1000, 1001):
        assert hash_file_streaming(f, chunk_size=size) == hashlib.sha256(data).hexdigest()


def test_c1_low_memory(big_file):
    tracemalloc.start()
    hash_file_streaming(big_file)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert peak < 2 * 1024 * 1024, f"peak memory {peak:,} bytes: is the whole file being read?"


# --- Challenge 2 ----------------------------------------------------------------------
def test_c2_finds_duplicates_recursively(tmp_path):
    (tmp_path / "sub" / "deeper").mkdir(parents=True)
    (tmp_path / "a.txt").write_bytes(b"same")
    (tmp_path / "sub" / "b.txt").write_bytes(b"same")
    (tmp_path / "sub" / "deeper" / "c.bin").write_bytes(b"same")
    (tmp_path / "unique.txt").write_bytes(b"different")
    result = find_duplicates(tmp_path)
    digest = hashlib.sha256(b"same").hexdigest()
    assert list(result) == [digest]
    assert result[digest] == sorted(
        [tmp_path / "a.txt", tmp_path / "sub" / "b.txt", tmp_path / "sub" / "deeper" / "c.bin"]
    )


def test_c2_no_duplicates(tmp_path):
    (tmp_path / "a").write_bytes(b"1")
    (tmp_path / "b").write_bytes(b"2")
    assert find_duplicates(tmp_path) == {}


def test_c2_same_name_different_content_is_not_duplicate(tmp_path):
    (tmp_path / "x").mkdir()
    (tmp_path / "y").mkdir()
    (tmp_path / "x" / "report.txt").write_bytes(b"v1")
    (tmp_path / "y" / "report.txt").write_bytes(b"v2")
    assert find_duplicates(tmp_path) == {}


def test_c2_empty_files_are_duplicates_of_each_other(tmp_path):
    (tmp_path / "e1").write_bytes(b"")
    (tmp_path / "e2").write_bytes(b"")
    assert len(find_duplicates(tmp_path)) == 1


# --- Challenge 3 ----------------------------------------------------------------------
@pytest.fixture
def store(tmp_path):
    return BlobStore(root=tmp_path / "store")


def _temp_leftovers(store):
    return [p for p in store.root.rglob("*") if p.is_file() and p.name.startswith(".tmp-")]


def test_c3_same_result_as_put(store, tmp_path):
    f = tmp_path / "in.bin"
    f.write_bytes(os.urandom(300_000))
    d = put_stream(store, f)
    assert d == hashlib.sha256(f.read_bytes()).hexdigest()
    assert store.get(d) == f.read_bytes()
    assert store.path_for(d).is_file()


def test_c3_dedup_leaves_no_temp_files(store, tmp_path):
    f = tmp_path / "in.bin"
    f.write_bytes(b"twice")
    d1 = put_stream(store, f)
    d2 = put_stream(store, f)
    assert d1 == d2
    assert store.stats().blob_count == 1
    assert _temp_leftovers(store) == []


def test_c3_uses_store_algorithm(tmp_path):
    s = BlobStore(root=tmp_path / "s", algo="blake2b")
    f = tmp_path / "in.bin"
    f.write_bytes(b"abc")
    assert put_stream(s, f) == hashlib.blake2b(b"abc").hexdigest()


def test_c3_low_memory(store, big_file):
    tracemalloc.start()
    d = put_stream(store, big_file)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert peak < 2 * 1024 * 1024, f"peak memory {peak:,} bytes: is the whole file being read?"
    assert store.path_for(d).stat().st_size == BIG


def test_c3_failure_cleans_up(store, tmp_path, monkeypatch):
    f = tmp_path / "in.bin"
    f.write_bytes(b"data")

    def boom(*args, **kwargs):
        raise OSError("disk full (simulated)")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError):
        put_stream(store, f)
    assert _temp_leftovers(store) == []
