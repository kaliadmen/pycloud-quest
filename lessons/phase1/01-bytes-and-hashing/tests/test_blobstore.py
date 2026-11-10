"""Tests for the shipped blob store. These must always pass (CI runs them).

Read them like documentation: each test name says one thing the store promises.
"""

import hashlib

import pytest
from blobstore import (
    BlobNotFound,
    BlobStore,
    CorruptBlob,
    InvalidDigest,
    corrupt_one_byte,
    main,
)


@pytest.fixture
def store(tmp_path):
    # tmp_path is a fresh empty folder per test, so tests never touch your real blobs/ folder.
    return BlobStore(root=tmp_path / "blobs")


def test_put_returns_sha256_of_content(store):
    assert store.put(b"hello") == hashlib.sha256(b"hello").hexdigest()


def test_round_trip(store):
    data = bytes(range(256)) * 10
    assert store.get(store.put(data)) == data


def test_empty_blob_is_allowed(store):
    assert store.get(store.put(b"")) == b""


def test_same_content_stored_once(store):
    a = store.put(b"same")
    b = store.put(b"same")
    assert a == b
    assert store.stats().blob_count == 1


def test_sharded_path_layout(store):
    d = store.put(b"hello")
    rel = store.path_for(d).relative_to(store.root)
    assert rel.parts == (d[:2], d[2:4], d)


def test_unsharded_layout(tmp_path):
    flat = BlobStore(root=tmp_path, shard_depth=0)
    d = flat.put(b"x")
    assert flat.path_for(d) == tmp_path / d


def test_str_is_rejected_with_helpful_message(store):
    with pytest.raises(TypeError, match="encode"):
        store.put("text is not bytes")


@pytest.mark.parametrize(
    "bad",
    [
        "../../../etc/passwd",
        "..\\..\\windows\\win.ini",
        "abc",
        "g" * 64,
        "a" * 63,
        "a" * 65,
        "",
        "/" + "a" * 63,
    ],
)
def test_invalid_digests_are_rejected(store, bad):
    with pytest.raises(InvalidDigest):
        store.path_for(bad)


def test_uppercase_digest_is_accepted(store):
    d = store.put(b"hello")
    assert store.get(d.upper()) == b"hello"


def test_missing_blob(store):
    with pytest.raises(BlobNotFound):
        store.get("0" * 64)


def test_corruption_is_detected_on_read(store):
    d = store.put(b"important data")
    corrupt_one_byte(store, d)
    with pytest.raises(CorruptBlob):
        store.get(d)


def test_corruption_ignored_when_verification_off(tmp_path):
    lax = BlobStore(root=tmp_path, verify_on_read=False)
    d = lax.put(b"important data")
    corrupt_one_byte(lax, d)
    assert lax.get(d) != b"important data"  # bad data returned silently: why the knob exists


def test_scrub_finds_only_corrupt_blobs(store):
    good = store.put(b"good")
    bad = store.put(b"bad")
    corrupt_one_byte(store, bad)
    assert store.scrub() == [bad]
    assert good not in store.scrub()


def test_atomic_write_leaves_no_temp_files(store):
    for i in range(20):
        store.put(f"blob {i}".encode())
    leftovers = [p for p in store.root.rglob(".tmp-*")]
    assert leftovers == []


def test_non_atomic_mode_still_round_trips(tmp_path):
    s = BlobStore(root=tmp_path, atomic_writes=False)
    assert s.get(s.put(b"x")) == b"x"


def test_list_and_stats(store):
    ds = {store.put(b"a"), store.put(b"bb"), store.put(b"ccc")}
    assert set(store.list_digests()) == ds
    assert store.stats().total_bytes == 6


def test_delete(store):
    d = store.put(b"bye")
    assert store.delete(d) is True
    assert not store.exists(d)
    assert store.delete(d) is False


@pytest.mark.parametrize("algo", ["md5", "sha1", "sha512", "blake2b", "sha3_256"])
def test_other_algorithms(tmp_path, algo):
    s = BlobStore(root=tmp_path, algo=algo)
    d = s.put(b"x")
    assert d == hashlib.new(algo, b"x").hexdigest()
    assert s.get(d) == b"x"


def test_put_file_uses_raw_bytes(store, tmp_path):
    f = tmp_path / "crlf.txt"
    f.write_bytes(b"a\r\nb\r\n")
    assert store.put_file(f) == hashlib.sha256(b"a\r\nb\r\n").hexdigest()


def test_cli_put_get_scrub(tmp_path, capsys):
    root = tmp_path / "cli"
    assert main(["--root", str(root), "put-text", "hi"]) == 0
    digest = capsys.readouterr().out.strip()
    assert main(["--root", str(root), "get", digest]) == 0
    assert capsys.readouterr().out.strip() == "hi"
    assert main(["--root", str(root), "scrub"]) == 0
    assert main(["--root", str(root), "corrupt", digest]) == 0
    assert main(["--root", str(root), "scrub"]) == 1


def test_cli_rejects_traversal(tmp_path, capsys):
    assert main(["--root", str(tmp_path), "get", "../../etc/passwd"]) == 2
    assert "InvalidDigest" in capsys.readouterr().err
