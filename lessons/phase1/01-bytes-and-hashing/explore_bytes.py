"""
Lesson 01 warm-up: text vs bytes, encodings, hex, and hashes.

Run:  uv run python explore_bytes.py
Then change the KNOBS and run again. Every section prints what's happening and why.
"""

from __future__ import annotations

import hashlib

# =====================================================================================
# KNOBS
# =====================================================================================
TEXT = "Nimbus ☁ café"  # try plain ASCII, then emoji like "🔥", then Japanese "雲"
ENCODINGS = ["utf-8", "utf-16-le", "latin-1"]  # latin-1 can't encode ☁. Watch what happens.
HASH_ALGOS = ["md5", "sha1", "sha256", "sha512"]
AVALANCHE_A = "transfer $100 to alice"
AVALANCHE_B = "transfer $900 to alice"  # one character different
# =====================================================================================


def section(title: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


def text_vs_bytes() -> None:
    section("1. A str is characters. bytes is numbers 0-255. Encoding turns one into the other.")
    print(f"TEXT = {TEXT!r}")
    print(f"len(TEXT) = {len(TEXT)} characters")
    for enc in ENCODINGS:
        try:
            b = TEXT.encode(enc)
        except UnicodeEncodeError as e:
            print(f"  {enc:<10} -> CAN'T ENCODE {TEXT[e.start]!r} at index {e.start}")
            continue
        print(f"  {enc:<10} -> {len(b):>3} bytes  hex: {b.hex(' ')}")
    print("Same text, different encodings, different bytes. So different hashes, too.")


def characters_up_close() -> None:
    section("2. Each character up close: code point and UTF-8 bytes")
    for ch in TEXT:
        utf8 = ch.encode("utf-8")
        print(f"  {ch!r:<6} U+{ord(ch):04X}  utf-8: {utf8.hex(' '):<12} ({len(utf8)} byte(s))")
    print("ASCII characters take 1 byte in UTF-8. Others take 2 to 4. That's why len() != bytes.")


def hex_is_just_notation() -> None:
    section("3. Hex is just a way to write bytes as text: 2 hex digits per byte")
    b = bytes([0, 15, 16, 127, 128, 255])
    print(f"  bytes : {list(b)}")
    print(f"  hex   : {b.hex()}")
    print(f"  back  : {list(bytes.fromhex(b.hex()))}")
    print(f"  int   : 0xff = {0xFF}, 0b1111_1111 = {0b1111_1111}")


def hashes() -> None:
    section("4. Hash functions: any input, fixed-size output")
    data = TEXT.encode("utf-8")
    for algo in HASH_ALGOS:
        h = hashlib.new(algo, data)
        print(f"  {algo:<7} {h.digest_size * 8:>3} bits  {h.hexdigest()}")
    print("MD5 and SHA-1 are BROKEN for security (collisions can be manufactured).")
    print("They still show up as checksums (S3 ETags use MD5). Use SHA-256 or better for security.")


def avalanche() -> None:
    section("5. Avalanche effect: a tiny change scrambles the whole hash")
    a = hashlib.sha256(AVALANCHE_A.encode()).hexdigest()
    b = hashlib.sha256(AVALANCHE_B.encode()).hexdigest()
    print(f"  {AVALANCHE_A!r}\n    {a}")
    print(f"  {AVALANCHE_B!r}\n    {b}")
    bits = bin(int(a, 16) ^ int(b, 16)).count("1")
    print(f"  {bits} of 256 bits differ (expect about 128).")
    print("This is why a hash proves integrity: you can't nudge the input to keep the hash.")


def newlines() -> None:
    section("6. Line endings: the invisible bytes that break hashes across Windows and Linux")
    linux = b"line one\nline two\n"
    windows = b"line one\r\nline two\r\n"
    print(f"  LF   {linux!r:<28} sha256 {hashlib.sha256(linux).hexdigest()[:16]}...")
    print(f"  CRLF {windows!r:<28} sha256 {hashlib.sha256(windows).hexdigest()[:16]}...")
    print("Identical in an editor. Different bytes, different hash. See bug hunt #1.")


def hash_is_not_encryption() -> None:
    section("7. A hash is NOT encryption")
    print("  Encryption is reversible with a key. A hash is one-way, with no key and no 'decrypt'.")
    print("  But short or guessable inputs CAN be found by guessing. Watch:")
    target = hashlib.sha256(b"1234").hexdigest()
    for guess in range(10_000):
        if hashlib.sha256(str(guess).zfill(4).encode()).hexdigest() == target:
            print(f"  Found the PIN behind {target[:16]}... in {guess + 1} guesses: {guess:04d}")
            break
    print("  This is why passwords need slow, salted hashes (argon2), which is Lesson 13.")


if __name__ == "__main__":
    text_vs_bytes()
    characters_up_close()
    hex_is_just_notation()
    hashes()
    avalanche()
    newlines()
    hash_is_not_encryption()
