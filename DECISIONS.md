# DECISIONS

Why the plan looks the way it does. Newest at the bottom. Later sessions must not undo these without a new entry.

## 2026-11-10: Build a cloud, don't just use one
The course builds Nimbus (a mini cloud) instead of only deploying to Azure, because the goal is to understand
how clouds work inside and where their security boundaries are. Azure comes in Phase 8, once every Azure
service maps to something already built by hand.

## 2026-11-10: Same lesson format as the C/C++ course
KNOBS, PREDICT, BUGS, challenges, QUIZ, NOTES, Under the Hood, Boss Fights, and the same tracking files.
One routine across both courses means less overhead per session. "Under the Hood" here means
bytecode (`dis`), syscalls (`strace` / Process Monitor) and packets (Wireshark) instead of assembly.

## 2026-11-10: No separate DSA track
The C course's `libquest/` covers data structures. This course uses the algorithms clouds rely on
(hashing, HMAC, heaps, token buckets, CIDR matching, hash chains) at the moment Nimbus needs them.

## 2026-11-10: Tooling
`uv` (fast, one tool for Python versions, venvs and dependencies, works the same on Windows and Linux),
`pytest`, `ruff`. Standard library first. Vetted libraries only for crypto and password hashing.

## 2026-11-10: Challenge and bug tests are opt-in
Tests marked `challenge` and `bughunt` fail on purpose until solved, so they are excluded from the default
`pytest` run and from CI. This keeps CI green and makes "green" mean "the shipped code works".

## 2026-11-10: Time split with the C/C++ course (PROPOSED, confirm with Quinze)
Total available is about 12 to 14 hours a week. Proposed split:
- Weekdays (Mon to Thu, 45 to 60 min): alternate. Mon/Wed = C review, Tue/Thu = Python review.
- Saturday: C/C++ build session. Sunday: Python build session.
This makes each course roughly half speed (C about 12+ months, Python about 8 months) but both keep moving.
Alternative: finish C Phases 1 and 2 first, then run Python full speed.

## 2026-11-10: The app is "Drop"
A secure file-sharing app for friends. It exercises every Nimbus service (identity, storage, secrets,
logs) and makes the Phase 7 security labs realistic. A JRPG cloud-save endpoint is a stretch goal that links to the C++ course.

## 2026-11-12: Develop on the Ubuntu Server VM only
Quinze already develops on an Ubuntu Server VM through JetBrains over SSH, and keeps language toolchains off
Windows to protect the OS. All setup and lessons target the VM. Windows steps are optional and always say what
they install. GUI tools like Wireshark open capture files copied from the VM.
