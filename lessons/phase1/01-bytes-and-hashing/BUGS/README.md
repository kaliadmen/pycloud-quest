# BUGS: Lesson 01

Three planted bugs. Each file is short. You get the **symptom**, like a real ticket. Finding the cause is your job.

```bash
uv run pytest -m bughunt lessons/phase1/01-bytes-and-hashing     # see them fail
```

How to hunt (practice the method, not just the fix):
1. Read the failing test. What does it expect, and what did it get?
2. Form a hypothesis *before* changing code. Write it in `NOTES.md`.
3. Prove it: set a breakpoint in PyCharm (click the gutter, then right-click the test > Debug), or add a
   temporary `print(repr(x))`. `repr` shows invisible characters that `print(x)` hides.
4. Fix the code, not the test. Re-run until green.
5. In `NOTES.md`, write one line on how this bug would show up in a real cloud.

---

### Bug 1: "The hashes don't match" (`l01_bug1.py`)
> **Ticket:** Uploads from the Windows admin laptop keep failing the integrity check. The server says the hash
> is wrong, but the file is fine. Running `certutil -hashfile` on the laptop gives the same hash the server
> computes, so the server looks right. Files made on the Linux VM upload fine. Oh, and the new logo upload crashed.

### Bug 2: "The blob that wasn't a blob" (`l01_bug2.py`)
> **Ticket (security, high):** A pentester asked our storage service for a blob and received the contents of a
> config file that lives *next to* the store, including a database password.

Fix rule: an invalid digest should raise `ValueError` (or a subclass). Think allow-list, not block-list.
Bonus: after your fix, explain why checking `".." in digest` alone would be a weak fix.

### Bug 3: "Scrub says everything is fine" (`l01_bug3.py`)
> **Ticket:** We ran the `corrupt` lab command on a blob, and `blobstore.py get` refuses it with CorruptBlob,
> so it's definitely corrupted. But the nightly scrub job has reported `0 corrupt` every night for a month.

Bonus: what is the operational risk of a monitoring job that silently checks nothing? (This is a big theme in Phase 5.)

<details>
<summary>Hints, only if stuck for 20+ minutes</summary>

- Bug 1: what does text mode do to `\r\n` when it reads? What happens to bytes that aren't valid UTF-8?
- Bug 2: in a Python shell, try `Path("store") / "ab" / "/etc/passwd"` and `Path("store/ab/cd") / "../../.."`.
  Lesson code already has a function that solves this.
- Bug 3: where do blobs actually live on disk with `SHARD_DEPTH = 2`? What does `glob("*")` look at?
</details>
