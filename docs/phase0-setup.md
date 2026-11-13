# Phase 0: Setup

**How this course runs:** all code, Python and tools live on your **Ubuntu Server VM**. JetBrains on Windows
connects to the VM over SSH (Gateway / Remote Development), the same way you already develop.
**Nothing needs to be installed on Windows.** Optional Windows extras are at the end, with what each one touches.

Expect about 30 minutes.

## 1. On the VM: Git and GitHub login
SSH into the VM (or use the JetBrains terminal once connected), then:
```bash
sudo apt update && sudo apt install -y git gh curl
git config --global user.name "Quinze"
git config --global user.email "<your GitHub email>"
gh auth login        # GitHub.com > HTTPS > "Login with a web browser"
```
`gh` prints a one-time code and a URL. Open the URL in your Windows browser, enter the code, and the VM is logged in.

## 2. On the VM: uv (manages Python for this project)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc     # or log out and back in
uv --version
```
`uv` installs into your home folder, not system-wide. It never touches the Ubuntu system Python, so it
can't break the server's own tools. To remove it later, delete `~/.local/bin/uv` and `~/.local/share/uv`.

> **Security note:** piping a script from the internet into your shell trusts that website completely.
> This is the official installer, so it's acceptable here. But attackers use exactly this pattern in fake
> install instructions. You can download the script with `curl -LsSf https://astral.sh/uv/install.sh -o uv.sh`
> and read it first.

## 3. On the VM: clone and test
```bash
mkdir -p ~/dev && cd ~/dev
gh repo clone kaliadmen/pycloud-quest
cd pycloud-quest
uv sync              # downloads the project's Python, creates .venv, installs pytest + ruff
uv run pytest        # should end with "34 passed"
uv run ruff check .  # should say "All checks passed!"
```

## 4. On Windows: open it in JetBrains over SSH
1. Open **JetBrains Gateway** (or Toolbox > Remote Development).
2. Use your existing SSH connection to the VM, choose **PyCharm** as the IDE, and set the project folder to
   `~/dev/pycloud-quest`.
3. Once it opens: Settings > Project > Python Interpreter > Add Interpreter > Add Local Interpreter >
   **Select existing** > `~/dev/pycloud-quest/.venv/bin/python`. (Newer versions may detect the uv environment automatically.)
4. Settings > Tools > Python Integrated Tools > Default test runner: **pytest**.
5. Right-click `lessons/phase1/01-bytes-and-hashing/tests` > Run. All green.

If you don't have a PyCharm license, CLion's Python plugin works in the same remote setup. PyCharm's
debugger is nicer for this course, and JetBrains AI works in both.

## 5. On the VM: Docker (not needed until Phase 4)
```bash
sudo apt install -y docker.io
sudo usermod -aG docker $USER    # log out and back in
docker run --rm hello-world
```
> **Security note:** being in the `docker` group is effectively root on that machine, because a container
> can mount `/`. Fine on a lab VM. We revisit it when hardening Nimbus in Phase 7.

## 6. Packet capture (not needed until Phase 2)
The VM has no desktop, so capture packets there and look at them in Wireshark later:
```bash
sudo apt install -y tcpdump tshark
sudo tcpdump -i lo -w capture.pcap port 8080    # capture, Ctrl+C to stop
tshark -r capture.pcap                          # read it in the terminal
```
To look at a `.pcap` in the Wireshark GUI on Windows, see the optional section below.

## 7. Daily habit
- **Sit down:** `git pull`
- **Get up:** `git add -A && git commit -m "L01: what I did" && git push`

Runtime data (`blobs/`, `*.db`, logs, keys) is in `.gitignore`, so it never leaks into GitHub.

## Done when
- [ ] `uv run pytest` passes on the VM.
- [ ] PyCharm (remote) runs the Lesson 01 tests green.
- [ ] The **Actions** tab on GitHub shows a green CI run.
- [ ] Phase 0 boxes ticked in `PROGRESS.md`, first `LOG.md` entry pushed.

---

## Optional Windows extras (and what each one touches)
None are required. Listed from lowest to highest risk.

| Tool | Used for | What it touches |
|---|---|---|
| **Sysinternals Process Monitor** | Lesson 01 Under the Hood (watch file system calls on Windows) | Microsoft-signed. Runs from a downloaded folder with no installer. Loads a monitoring driver only while it's open |
| **Wireshark without Npcap** | Opening `.pcap` files copied from the VM | Normal app. In the installer, **untick Npcap**: you only lose live capture on Windows, which you don't need |
| **Wireshark with Npcap** | Live capture on Windows itself | Npcap is a network driver. It's widely used and safe, but it's the only item here that adds a kernel driver |

Ordinary programming tools such as Python, uv and Git are user-mode programs. They don't install drivers, so
they can't blue-screen Windows. If you ever install anything on Windows and want a safety net, create a restore
point first: Start > "Create a restore point" > Create.
