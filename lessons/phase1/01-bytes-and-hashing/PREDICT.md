# PREDICT: Lesson 01

For each experiment: write your prediction **first**, then change the knob, run, and record what happened.
Being wrong is the useful part, so write down why you were wrong. Reset knobs afterwards, and use
`uv run python blobstore.py wipe` between experiments that change the layout.

---

### 1. `HASH_ALGO = "md5"`, then `"sha512"`, then run `demo`
- Predict the digest length in hex characters for each:
- Predict whether the demo's path traversal check still works, and why:
- **Result:**
- **Why:**

### 2. Change the algorithm WITHOUT wiping, then run `ls` and `get` on an old digest
- Predict:
- **Result:**
- **Why:** (Real systems store the algorithm with the hash, like `sha256:...` in Docker. Why?)

### 3. `SHARD_DEPTH = 0`, then `3`. Run `demo`, look in `blobs/`
- Predict the folder structure for each:
- With depth 3 and width 2, how many possible leaf folders are there?
- **Result:**

### 4. `SHARD_WIDTH = 1` with `SHARD_DEPTH = 2`
- Predict the number of possible leaf folders:
- **Result:**

### 5. In `explore_bytes.py`: `TEXT = "雲 Nimbus 🔥"`
- Predict the UTF-8 byte count for `雲` and for `🔥`:
- Predict which of the three encodings will fail:
- **Result:**

### 6. `VERIFY_ON_READ = False`, run `demo`
- Predict what step 5 prints now:
- **Result:**
- Which is worse for a cloud customer: an error, or silently wrong data? Why?

### 7. `put-text "hello"` twice, then `put-text "hello "` (trailing space), then `stats`
- Predict the blob count:
- **Result:**

### 8. A "Windows" file vs a "Linux" file with the same text
On the VM: `printf 'hello\r\n' > w.txt` (Windows line ending) and `printf 'hello\n' > l.txt` (Linux line ending).
Or create `w.txt` in Notepad on Windows and drag it into the project in PyCharm. Then `put` each.
- Predict whether the digests match:
- **Result:**
- Open both with your `hexview` from the C course (or `xxd w.txt`). What's different?

### 9. `ATOMIC_WRITES = False`. Can you think of a way to *see* the difference?
Hint: what if the program is killed in the middle of a large write? Try: generate a 1 GB file, `put` it,
and press Ctrl+C partway. Then `scrub`. Try again with atomic writes on.
- Predict:
- **Result:**
