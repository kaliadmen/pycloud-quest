# Phase 0: Setup

Do this once on each machine: Windows 11 (main), the Ubuntu VM, and later the Raspberry Pis.
Expect about an hour the first time and 15 minutes on each extra machine.

## 1. Git and GitHub login
**Windows:** install Git for Windows (`winget install Git.Git`), then the GitHub CLI (`winget install GitHub.cli`).
**Ubuntu / Pi:** `sudo apt update && sudo apt install -y git gh`

Then on every machine:
```bash
git config --global user.name "Quinze"
git config --global user.email "you@example.com"
gh auth login          # choose GitHub.com, HTTPS, login with browser
```

## 2. uv (Python version + virtual environments + dependencies in one tool)
**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
**Ubuntu / Pi:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Open a new terminal and check: `uv --version`.

You do not need to install Python separately. `uv` reads `.python-version` and downloads that Python
for this project only. Your system Python stays untouched.

> **Security note:** piping a script from the internet into your shell trusts that website completely.
> It's the official installer, so it's acceptable here, but notice the pattern. Attackers use exactly
> this trick in fake "install instructions". You can download the script and read it first.

## 3. Clone and run
```bash
gh repo clone <your-github-name>/pycloud-quest
cd pycloud-quest
uv sync               # creates .venv and installs pytest + ruff
uv run pytest         # should end with "passed"
uv run ruff check .   # should say "All checks passed!"
```

## 4. PyCharm
1. Open the `pycloud-quest` folder.
2. Settings > Project > Python Interpreter > Add Interpreter > Add Local > **Select existing** > choose
   `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Linux).
   Newer PyCharm versions can also pick the uv environment automatically.
3. Settings > Tools > Python Integrated Tools > Default test runner: **pytest**.
4. Right-click `lessons/phase1/01-bytes-and-hashing/tests` > Run. All green.

If you'd rather stay in CLion, it can run Python through the Python plugin, but PyCharm's debugger and test
runner are better for this course. JetBrains AI works in both.

## 5. Docker (Ubuntu VM only, needed from Phase 4)
```bash
sudo apt install -y docker.io
sudo usermod -aG docker $USER    # log out and back in after this
docker run --rm hello-world
```
> **Security note:** membership in the `docker` group is effectively root on that machine, because a
> container can mount `/`. Fine on a lab VM. Remember it when we harden Nimbus in Phase 7.

## 6. Wireshark (needed from Phase 2)
**Windows:** `winget install WiresharkFoundation.Wireshark` (accept the Npcap install).
**Ubuntu:** `sudo apt install -y wireshark` and allow non-root capture when asked.

## 7. Daily habit across machines
- **Sit down:** `git pull`
- **Get up:** `git add -A && git commit -m "L01: what I did" && git push`

Whatever machine you're on next is then current. Runtime data (`blobs/`, `*.db`, logs, keys) is in
`.gitignore`, so each machine keeps its own and none of it leaks into GitHub.

## Done when
- `uv run pytest` passes on Windows and the VM.
- The **Actions** tab on GitHub shows a green CI run on Ubuntu and Windows.
- Tick the Phase 0 boxes in `PROGRESS.md` and add your first `LOG.md` entry.
