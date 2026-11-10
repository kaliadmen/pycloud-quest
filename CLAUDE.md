# CLAUDE.md: instructions for Claude

This repo is Quinze's **PyCloud Quest** course: learning Python by building **Nimbus**, a small cloud
platform, plus an app (**Drop**) that runs on it. The focus is how clouds are built and how to secure
them. A sibling course, **C/C++ Quest**, covers C, C++, assembly and games, and the two link up
(see `ROADMAP.md`, "Algorithms thread" and Lesson 26).

The repo is the single source of truth. Nothing depends on chat history.

## Starting a session
1. Read `PROGRESS.md` (where he is), the last 3 to 5 entries of `LOG.md`, and `DECISIONS.md`.
2. Check recent commits: `git log --oneline -15`.
3. If a lesson was just finished, review it (see "Reviewing work" below) before starting anything new.
4. Then continue with the next item in `ROADMAP.md`, unless `DECISIONS.md` says otherwise.

## About the learner
- Works in IT application support. Knows C#, some Python, VBA, MS Access, Power Automate, has Azure exposure.
- Goal: security analyst (blue team / SOC), cloud security. Studying CompTIA Network+ / Security+ / CySA+.
- Uses Windows 11 (main), an Ubuntu VM, JetBrains IDEs (CLion, PyCharm), and a home lab with two
  Raspberry Pis plus a 32 GB laptop.
- Time: full-time job. Short weekday review sessions, longer weekend build sessions. He also runs the C/C++ course.
- Uses voice-to-text, so messages may contain transcription errors. Read for intent.

## Teaching style
- Build it by hand first, then use the production tool and compare.
- Explain *why* and the trade-offs, and connect every concept to how Azure/AWS do the same thing.
- Every lesson has a security angle. Offensive content only targets his own lab code (planted bugs, localhost,
  his own Pis). Never real third-party systems.
- Don't skip the learning steps for him. When he's stuck, give hints in increasing strength before full answers.
- Keep prose plain and direct.

## Lesson format (keep it identical across lessons)
```
lessons/phaseN/NN-short-name/
  README.md            concept, how real clouds do it, trade-offs, steps for the session
  <module>.py          main code with a KNOBS block at the top, heavily commented
  PREDICT.md           "change this knob, predict, then run" prompts with blanks to fill
  BUGS/                lNN_bug1.py ... + README.md (symptoms only, never the cause) + test_bugs.py
  challenges/          lNN_challenge.py with TODO functions + test_challenges.py
  tests/               tests for the main module (must pass)
  QUIZ.md              5 to 8 recall questions, answers in a collapsed <details> block at the bottom
  NOTES.md             template the learner fills in, in his own words
  UNDER_THE_HOOD.md    dis / strace / Wireshark / Process Monitor view of the lesson
  conftest.py          puts the lesson folder on sys.path
```

Conventions:
- Module names must be unique across all lessons (pytest imports them by name). Bug and challenge
  modules use the lesson prefix: `l01_bug1.py`, `l01_challenge.py`.
- Test markers: `challenge` (fails until he solves it) and `bughunt` (fails until he fixes the bug).
  Default `uv run pytest` excludes both, so CI stays green. He runs them with `-m challenge` or `-m bughunt`.
- Python 3.12+, `uv` for environments, `ruff` for lint and format, `pytest` for tests. Type hints everywhere.
- Standard library first. Add a dependency only when the lesson is about that library or doing it by hand
  would be unsafe (crypto, password hashing).
- Never write custom crypto. Use `hashlib`, `hmac`, `secrets`, `cryptography`, `argon2-cffi`.
- Cross-platform: code must run on Windows and Linux. Note when a step is Linux-only (nftables, cgroups).
- When a lesson is done, its reusable code graduates into `nimbus/` with tests. Note this in `PROGRESS.md`.

## Reviewing work
When he pushes a finished lesson:
1. Run `uv run pytest`, `uv run pytest -m challenge`, `uv run pytest -m bughunt` and `uv run ruff check`.
2. Read `NOTES.md`: is the explanation correct and in his own words? Point out misconceptions directly.
3. Check `QUIZ.md` answers and `PREDICT.md` predictions. Wrong predictions are good; look at what he learned from them.
4. Read his challenge code for correctness, security issues and Python style. Name one thing done well
   and the most important thing to improve.
5. Update `PROGRESS.md`. Add review items to "Review queue" for weak spots, and bring them back in later
   weekday review sessions (spaced repetition).
6. If he is moving fast, offer to skip or compress. If a Boss Fight goes badly, add a review lesson and log it in `DECISIONS.md`.

## Changing the plan
Any change to the roadmap gets a dated entry in `DECISIONS.md` with the reason, so later sessions don't undo it.
