# PyCloud Quest

Learn Python by building **Nimbus**, your own small cloud platform, from raw sockets up. Then deploy
a real app (**Drop**) on it, watch it through your own logs and detections, attack it in your lab, and harden it.

The point is to understand how clouds are built and where their security boundaries are, by building each piece yourself.

## Where to start
1. `docs/phase0-setup.md`: set up each machine (about an hour).
2. `ROADMAP.md`: the full plan, phases, lessons and milestones.
3. `lessons/phase1/01-bytes-and-hashing/README.md`: your first lesson.

## Repo layout
```
ROADMAP.md        the plan
PROGRESS.md       checklist of where you are
LOG.md            2 to 3 lines per session
DECISIONS.md      why the plan changed, so nobody undoes it by accident
CLAUDE.md         instructions for Claude (teaching style, lesson format, how to review)
docs/             setup guides and architecture notes
lessons/          one folder per lesson, grouped by phase
boss-fights/      from-scratch exercises that close each phase
nimbus/           the cloud itself; finished lesson code graduates into here
app/              Drop, the app that runs on Nimbus (Phase 6)
```

## Commands you'll use
```bash
uv run pytest                  # shipped code (what CI runs)
uv run pytest -m challenge     # your challenge exercises (fail until you solve them)
uv run pytest -m bughunt       # the planted bugs (fail until you fix them)
uv run ruff check .            # lint, including security rules
uv run ruff format .           # auto-format
```

## Continuing in a new chat with Claude
Say: *"Continue my Python cloud course, repo `<your-github-name>/pycloud-quest`."*
Claude reads `CLAUDE.md`, `PROGRESS.md`, the latest `LOG.md` and your recent commits, reviews what you pushed,
and picks up from there.

## Sibling course
**C/C++ Quest** (C, C++, assembly, the Blue Team Toolkit and the JRPG). The courses connect: your C log analyzer
reads Nimbus logs in Lesson 26, and the JRPG can use Nimbus for cloud saves.
