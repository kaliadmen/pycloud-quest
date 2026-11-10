# QUIZ: Lesson 01

Answer from memory first, without looking at notes or code. Write your answers under each question, then
check against the answers at the bottom and mark each one right or wrong. Wrong answers go into the review queue.

1. What does `len("café")` return, and what does `len("café".encode("utf-8"))` return? Why do they differ?

2. A SHA-256 digest is how many bytes? How many hex characters? Why exactly twice as many?

3. Name the three things content addressing gives you "for free".

4. Why is MD5 still acceptable for an S3 ETag but not for verifying a software download from an untrusted mirror?

5. List the three steps of an atomic write, and say why the temp file must be in the same folder (filesystem) as the target.

6. A user requests blob `"../../etc/passwd"`. What does the store do, and why is an allow-list better than checking for `".."`?

7. What is scrubbing, and why do clouds run it even though they verify on read?

8. Explain to a coworker in two sentences why a hash is not encryption.

---

<details>
<summary>Answers (only after you've written yours)</summary>

1. 4 and 5. `len` on `str` counts characters. `é` is one character but 2 bytes in UTF-8 (`c3 a9`).
2. 32 bytes, 64 hex characters. Each hex digit holds 4 bits, so one byte (8 bits) needs two.
3. Integrity (re-hash and compare to the name), dedup (same content gives the same name), immutability (new content gives a new name).
4. The ETag only needs to catch *accidental* corruption, and MD5 does that fine. A malicious mirror can craft a file that collides with the expected MD5, so MD5 can't defend against an attacker.
5. Write to a temp file, flush + fsync, then `os.replace` onto the final name. Rename is only atomic within a single filesystem; across filesystems it becomes a copy + delete, which can be interrupted halfway.
6. `validate_digest` rejects it with `InvalidDigest` because it isn't exactly 64 hex characters. A block-list misses variants: absolute paths, backslashes on Windows, URL-encoded `%2e%2e`, and others. An allow-list only accepts the one known-good shape.
7. A background job that re-hashes all stored data to find corruption before anyone reads it. Rarely read data could rot for years unnoticed, and by the time someone reads it, every replica might be bad.
8. Encryption is reversible by anyone with the key. A hash has no key and no reverse, but anyone can hash guesses, so short or predictable inputs can be found by brute force.
</details>
