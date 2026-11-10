# Lesson 01: Bytes, hashing & a blob store

**You build:** a content-addressed blob store, the storage engine that grows into Nimbus object storage in Lesson 16.
**Python:** `bytes` vs `str`, encodings, hex, `hashlib`, binary file I/O, `pathlib`, exceptions, `dataclass`, `argparse`.
**Cloud:** content addressing, dedup, sharded layouts, atomic writes, integrity checks, scrubbing.
**Security:** hashes vs encryption, broken hashes (MD5/SHA-1), path traversal, timing-safe comparison.

## Session plan
**Weekend build (3 to 4 hours)**
0. Open a terminal in this folder (`cd lessons/phase1/01-bytes-and-hashing`). `uv run` finds the project from here.
1. Read this README (30 min).
2. `uv run python explore_bytes.py`. Read every section's output, then change its KNOBS (20 min).
3. `uv run python blobstore.py demo`. Then open the `blobs/` folder in your file explorer and look at it (10 min).
4. Work through `PREDICT.md`: predict, change a knob, run, record (45 min).
5. Bug hunts in `BUGS/` (45 min).
6. Challenges in `challenges/` (60 min).
7. Write `NOTES.md`, update `PROGRESS.md` and `LOG.md`, commit, push.

**Weekday reviews (45 to 60 min each)**
- Answer `QUIZ.md` from memory, then check.
- Work through `UNDER_THE_HOOD.md` (strace on the VM, Process Monitor on Windows).
- Run your `find_duplicates` on your real Downloads folder.

---

## 1. Text is not bytes
A disk, a network socket and a hash function only understand **bytes**: numbers from 0 to 255.
A Python `str` is a sequence of **characters** (Unicode code points). To get from one to the other you
**encode** (`str` to `bytes`) and **decode** (`bytes` to `str`), and you must pick an **encoding**.

```python
"café".encode("utf-8")  # b'caf\xc3\xa9'   5 bytes, 4 characters
"café".encode("utf-16-le")  # 8 bytes
b"caf\xc3\xa9".decode("utf-8")  # 'café'
```
UTF-8 is the default for the web, Linux, JSON and almost every cloud API. Python 3 refuses to mix the two
types silently (`"a" + b"a"` is a `TypeError`), which is a feature, because silent mixing caused years of
bugs in Python 2. Your C course covers the same ground from below: a C `char*` is just bytes, and the encoding is up to you.

**Rule for this course:** decode at the edges (when bytes come in), work with `str` inside, encode at the edges
(when bytes go out). Hashing, storage and networking happen at the edges, so they use `bytes`.

## 2. Hex is notation, not encryption
`b"\x00\xff".hex()` gives `"00ff"`: each byte written as 2 hex digits. A SHA-256 digest is 32 bytes, so its hex form
is 64 characters. Hex makes binary values safe to print, log, put in URLs and use as file names. It hides nothing.

## 3. Hash functions
A cryptographic hash turns any input into a fixed-size fingerprint, with these properties:

| Property | Meaning | Why the cloud cares |
|---|---|---|
| Deterministic | Same bytes, same hash, on every machine | Two servers can agree on content without sending it |
| Avalanche | One bit changes about half of the output | Tampering can't be hidden by small tweaks |
| Pre-image resistant | Can't work backwards from hash to input | Hashes can be shown publicly |
| Collision resistant | Can't find two inputs with the same hash | A hash can stand in for the content |

**MD5 and SHA-1 have lost collision resistance.** Researchers produce colliding files on purpose (the 2017
"SHAttered" attack made two different PDFs with the same SHA-1). They're still fine for spotting
*accidental* corruption, which is why the S3 ETag of a simple upload is an MD5. Never use them where an attacker
chooses the input. Use SHA-256, SHA-512, SHA-3 or BLAKE2.

**A hash is not encryption.** There's no key and no way back, but anyone can hash guesses and compare.
`explore_bytes.py` cracks a hashed 4-digit PIN in milliseconds. Passwords need slow, salted hashing
(argon2), which is Lesson 13.

## 4. Content addressing
Normal storage: *you* choose the name, and the content can change behind it.
Content-addressed storage: the **name is the hash of the content**. That gives you three things for free:
- **Integrity:** re-hash on read. If it doesn't match the name, the data is corrupt. No separate checksum database.
- **Dedup:** identical content gets an identical name, so it's stored once.
- **Immutability:** change one byte and you have a different object with a different name. Nothing is overwritten.

Where you've already used it without knowing:
- **Git:** every commit, file and folder is stored in `.git/objects/ab/cdef...`, named by its hash (SHA-1, with SHA-256 support added). Look in any repo.
- **Docker/OCI images:** every layer is identified by `sha256:...`. That's why pulling an image skips layers you already have.
- **S3 and Azure Blob Storage:** you choose object names, but both keep content hashes (ETag, Content-MD5, optional SHA-256 checksums) to check uploads and detect corruption.

## 5. Sharding the folder layout
Putting millions of files in one folder makes listing slow and hits limits on some filesystems. So the store
uses the first characters of the hash as folders: `9a/1d/9a1de91f...`. Hashes are uniformly random, so files spread
evenly. With `SHARD_WIDTH = 2` and `SHARD_DEPTH = 2` you get 256 x 256 = 65,536 folders. Git uses depth 1. Try different depths in `PREDICT.md`.

## 6. Atomic writes
If the program crashes halfway through writing a file, a half-written file sits under a valid-looking name.
The fix every serious storage system uses:
1. Write to a temporary file **in the same folder**.
2. `flush()` and `os.fsync()`, so the data really reaches the disk, not just the OS cache.
3. `os.replace(temp, final)`. A rename within one filesystem is atomic: readers see either no file or the whole file.

`UNDER_THE_HOOD.md` shows these steps as real system calls.

## 7. Integrity checks and scrubbing
Disks and memory flip bits silently ("bit rot"). Clouds handle this by:
- **Verify on read** (`VERIFY_ON_READ`): never hand out data that doesn't match its hash.
- **Scrubbing**: a background job re-hashes everything and reports corruption *before* anyone reads it. Real systems then
  repair it from another replica (replication comes later in the course).

## 8. Security: input becomes a path
The digest arrives from a user (an API request in Lesson 16) and becomes part of a file path. Without validation,
`../../secret.txt` or an absolute path escapes the store. That's **path traversal**, one of the most common
vulnerabilities in file-handling services. `validate_digest` uses an **allow-list**: exactly N hex characters,
nothing else. Allow-lists beat block-lists, because you can't forget to block something you never allowed. Bug hunt 2 is this bug.

`hmac.compare_digest` compares in constant time. For a public hash it's habit, but for secrets (HMAC signatures in
Lesson 16, API keys in Lesson 13) a normal `==` stops at the first wrong character, and that timing difference leaks the secret one character at a time.

## Design trade-offs in this store
| Choice | Benefit | Cost |
|---|---|---|
| Content addressing | Free integrity + dedup | Users can't pick names. Lesson 16 adds a name-to-digest index on top, like S3 keys |
| Verify on every read | Never serves corrupt data | Re-hashing costs CPU on every read |
| Atomic write + fsync | Crash-safe | Slower; fsync waits for the disk |
| Whole-file `put(bytes)` | Simple | Needs RAM equal to the file size. Challenge 3 fixes this |
| SHA-256 | Secure, everywhere | Slower than BLAKE2 or non-crypto hashes (xxHash) |

## Done when
- [ ] `uv run pytest lessons/phase1/01-bytes-and-hashing` is green (shipped code)
- [ ] All three bugs fixed: `uv run pytest -m bughunt lessons/phase1/01-bytes-and-hashing`
- [ ] All three challenges pass: `uv run pytest -m challenge lessons/phase1/01-bytes-and-hashing`
- [ ] `PREDICT.md`, `QUIZ.md` and `NOTES.md` filled in and pushed
- [ ] Claude reviewed it, then the store graduates to `nimbus/storage/`
