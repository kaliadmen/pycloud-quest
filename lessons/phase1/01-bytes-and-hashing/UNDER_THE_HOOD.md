# UNDER THE HOOD: Lesson 01

The C course looks below C at assembly. Here you look below Python in two ways:
**bytecode** (what Python compiles your code into) and **system calls** (what your program asks the OS to do).
Security tools such as EDR agents, Sysmon and auditd watch system calls, so this is the view a defender
gets of every program on a machine.

## 1. Bytecode with `dis`
```bash
uv run python -c "import dis, blobstore; dis.dis(blobstore.BlobStore.hash_bytes)"
```
Output on Python 3.13 (other versions differ slightly):
```
101   LOAD_GLOBAL   0 (hashlib)
      LOAD_ATTR     2 (new)
      PUSH_NULL
      LOAD_FAST     0 (self)
      LOAD_ATTR     4 (algo)
      LOAD_FAST     1 (data)
      CALL          2                 <- hashlib.new(self.algo, data)
      LOAD_ATTR     7 (hexdigest ...)
      CALL          0                 <- .hexdigest()
      RETURN_VALUE
```
- CPython runs a **stack machine**: `LOAD_*` pushes values, `CALL n` pops a function and n arguments and pushes the result.
  Compare with the x86 registers you'll see in the C course.
- `LOAD_FAST` (local variable) is cheaper than `LOAD_GLOBAL` (a dictionary lookup). That's why hot loops sometimes copy a global into a local.
- The actual SHA-256 work isn't here at all. `hashlib` is C code (OpenSSL). Python bytecode just calls it.

**Try:** `dis.dis(blobstore.BlobStore.validate_digest)` and find the loop for `any(...)`.

## 2. System calls on Linux (Ubuntu VM) with `strace`
```bash
cd lessons/phase1/01-bytes-and-hashing
strace -f -e trace=openat,write,fsync,rename ../../../.venv/bin/python blobstore.py --root /tmp/st put-text "hello"
```
The important lines (real output, trimmed):
```
openat(AT_FDCWD, "/tmp/st/2c/f2/.tmp-dd1gfeg8", O_RDWR|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC, 0600) = 3
write(3, "hello", 5)                    = 5
fsync(3)                                = 0
rename("/tmp/st/2c/f2/.tmp-dd1gfeg8", "/tmp/st/2c/f2/2cf24dba5fb0a30e...") = 0
```
Read each flag. They're security decisions made by `tempfile.mkstemp` for you:
- `O_CREAT|O_EXCL`: create the file, and **fail if it already exists**. An attacker can't pre-create the temp file.
- `O_NOFOLLOW`: refuse to follow a symlink. Blocks the classic symlink attack on temp files.
- `0600`: only your user can read or write it.
- `rename(...)`: the atomic step from the README. Before it, the final name doesn't exist. After it, the complete file does.

**Try:** run `put-text "hello"` a second time with strace. Why are there no `openat`/`rename` lines for the store this time?

## 3. Same thing on Windows with Process Monitor
1. Install Sysinternals Process Monitor (`winget install Microsoft.Sysinternals.ProcessMonitor`).
2. Filter: *Process Name is python.exe*, then *Path contains blobs*.
3. Run `uv run python blobstore.py put-text "hello windows"`.
4. Find `CreateFile` on the `.tmp-` file, `WriteFile`, `FlushBuffersFile` (Windows' fsync), and `SetRenameInformationFile` (Windows' rename).

Sysmon, which feeds your Wazuh server later in the course, logs these same kinds of events.

## 4. Look at a blob's raw bytes
Use `hexview` from your C course (or `xxd` / `Format-Hex` in PowerShell) on a blob file. Then run
`corrupt` on it and look again. Find the one byte that changed and work out which bit flipped.
