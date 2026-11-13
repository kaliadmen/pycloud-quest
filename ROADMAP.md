# ROADMAP: PyCloud Quest

**Goal:** learn Python by building **Nimbus**, a small but real cloud platform, from raw sockets up,
then deploy your own app on it, watch everything through logs, attack it, and harden it.

By the end you will understand, because you built them, the pieces every cloud (Azure, AWS, GCP) is made of:
an API front door, identity and IAM, a control plane and data plane, object storage, compute, virtual
networking and firewalls, a secrets manager, audit logging, and monitoring and detection.

> **Rule of the course:** first build the thing by hand so you understand it, then use the
> production library and see what it was doing for you. Raw socket HTTP server, then FastAPI.
> A hand-written policy engine, then Azure RBAC.

---

## The thing you are building

```
                         you / your app users
                                  |
                         [ Load balancer + TLS ]          <- Phase 6
                                  |
     +----------------------- CONTROL PLANE (Pi or laptop) ----------------------+
     |  Nimbus API (FastAPI)  ->  IAM policy engine  ->  Audit log (hash chain)   |  <- Phase 3
     |        |                                                                  |
     |   Scheduler / job queue  ------------------------------+                  |  <- Phase 4
     +--------|------------------------------------------------|-----------------+
              |                                                |
     +--------v--------- DATA PLANE ----------------+   +------v--------------+
     | Node agent (each Raspberry Pi / VM)          |   | Object storage      |  <- Phase 4
     |  - runs containers as "instances"            |   | (Lesson 01's blob   |
     |  - security groups -> nftables rules         |   |  store grows up)    |
     |  - heartbeats + metrics                      |   +---------------------+
     +----------------------------------------------+
              |  every service ships JSON logs + metrics
     +--------v---------- OBSERVABILITY ------------------------------------------+
     | Log aggregator -> detection rules -> alerts -> Wazuh (home lab)            |  <- Phase 5
     | Metrics store -> dashboard                                                  |
     +-----------------------------------------------------------------------------+
```

It runs on your home lab hardware: the 32 GB laptop or Ubuntu VM as the control plane, and the
two Raspberry Pis as compute nodes. Everything also runs on a single machine for development.

---

## How every lesson works

Same format as the C/C++ course, so your brain already knows the routine.

| Part | What it is | Why it works |
|---|---|---|
| `README.md` | Concept, how real clouds do it, design trade-offs | Builds the mental model first |
| Code with a `KNOBS` block | Constants at the top you change to see what happens | Learning by poking the system |
| `PREDICT.md` | Write your prediction *before* running a knob change | Exposes wrong mental models fast |
| `BUGS/` | Copies of the code with planted bugs, plus failing tests | Debugging is half of security work |
| `challenges/` | Functions marked `TODO` with tests you make pass | You write real code, and the tests grade it |
| `QUIZ.md` | 5 to 8 questions answered from memory | Recall cements knowledge better than rereading |
| `NOTES.md` | Your own explanation, which Claude reviews | Shows what actually stuck |
| `UNDER_THE_HOOD.md` | The same code seen from below: bytecode (`dis`), syscalls (`strace`), packets (Wireshark) | The Python version of the C course's assembly thread |

Every phase ends with a **Boss Fight**: build a small thing from scratch, no notes. Pass it and the
phase is done. Struggle and we know exactly what to review.

Every lesson's code **graduates** into the `nimbus/` package when the lesson is done, so the cloud
grows one lesson at a time and old code keeps getting reused (built-in spaced review).

---

## Phases

### Phase 0: Setup (one session)
Everything on the Ubuntu Server VM: Git, `uv` (which brings Python), Docker, tcpdump/tshark. PyCharm on Windows
connects over SSH. Nothing has to be installed on Windows. Repo cloned and `uv run pytest` passing on every machine.
**Milestone:** green CI run on GitHub.

### Phase 1: Python for infrastructure code
You already know some Python and C#. This phase fills gaps fast and points everything at infrastructure.

| # | Lesson | Python concepts | Cloud / security concepts |
|---|---|---|---|
| 01 | **Bytes, hashing & a blob store** | `bytes` vs `str`, encodings, hex, `hashlib`, binary files, `pathlib`, `argparse` | Content addressing (S3 ETags, Git, Docker layers), integrity checks, atomic writes, hash is not encryption |
| 02 | **Structured logging** | `logging` module, JSON, `datetime`/UTC, context vars | Why clouds log JSON, correlation IDs, log levels, never log secrets |
| 03 | **Modeling cloud resources** | `dataclasses`, type hints, `Enum`, `__repr__`, validation | Resource IDs, ARNs and Azure resource IDs, state machines (pending to running to stopped) |
| 04 | **Errors, context managers & testing** | exceptions, `with`, `pytest` fixtures, `tmp_path` | Fail closed vs fail open, cleanup on failure |
| 05 | **Config & secrets hygiene** | env vars, TOML, `pydantic-settings` | 12-factor config, `.env` leaks, secret scanning |

**Milestone:** `nimbus-log`, a structured logger plus a CLI that queries JSON logs (`--since 1h --level ERROR --user alice`).
**Boss Fight 1:** a file-integrity snapshot tool, written from scratch.

### Phase 2: Networking from the bottom: how cloud services talk
| # | Lesson | What you build |
|---|---|---|
| 06 | **Sockets** | TCP echo server and client. Watch the 3-way handshake in Wireshark |
| 07 | **HTTP by hand** | An HTTP/1.1 server on raw sockets. Parse untrusted input safely: size limits, malformed requests |
| 08 | **Concurrency** | Threads vs `asyncio`. Then slow-client (slowloris-style) protection for *your own* server |
| 09 | **TLS & your own CA** | Create a Nimbus certificate authority, issue server certs, add HTTPS to the hand-built server |
| 10 | **DNS** | A tiny DNS server so `api.nimbus.lab` resolves in your home lab |

**Milestone:** a hand-built HTTPS server plus internal DNS.
**Boss Fight 2:** a TCP chat server with multiple clients, from scratch.

### Phase 3: The control plane: the cloud's brain
| # | Lesson | What you build |
|---|---|---|
| 11 | **REST API with FastAPI** | The Nimbus API. You now know what FastAPI does for you because you did it by hand in Lesson 07 |
| 12 | **Databases** | SQLite with raw SQL, then SQLAlchemy. A SQL injection lab against *your own* planted bug |
| 13 | **Identity** | Users, password hashing (argon2, a vetted library), API keys, tokens, sessions, MFA (TOTP) |
| 14 | **IAM policy engine** | JSON policy documents with Allow/Deny, wildcards, explicit-deny-wins. Same logic as AWS IAM and close to Azure RBAC |
| 15 | **Audit trail** | Every API call logged as who/what/when/where, made tamper-evident with a hash chain (like CloudTrail and Azure Activity Log) |

**Milestone:** Nimbus Control Plane v1, with an API, IAM and an audit trail.
**Boss Fight 3:** a policy evaluator for a new set of rules, from scratch.

### Phase 4: Services: what clouds actually sell
| # | Lesson | What you build |
|---|---|---|
| 16 | **Object storage** | Buckets, keys, metadata, presigned URLs (HMAC). Lesson 01's blob store becomes the engine. Path traversal lab |
| 17 | **Compute** | Containers as "instances" through the Docker SDK. CPU and memory limits, and how namespaces and cgroups isolate tenants |
| 18 | **Node agent & scheduler** | An agent on each Raspberry Pi that heartbeats to the control plane. The scheduler picks a node (`heapq`). Control plane vs data plane |
| 19 | **Virtual networking** | Security groups compiled into nftables rules, CIDR matching, port mapping |
| 20 | **Secrets manager / KMS** | Encryption at rest with `cryptography` (AES-GCM), envelope encryption, key rotation |
| 21 | **Async jobs** | A job queue and workers. Why provisioning in real clouds says "Creating..." |

**Milestone:** a `nimbus` CLI that creates a bucket, launches an instance on a Pi, and stores a secret.
**Boss Fight 4:** a presigned-URL service, from scratch.

### Phase 5: Observability: logs, metrics, detection
| # | Lesson | What you build |
|---|---|---|
| 22 | **Log pipeline** | Every service ships JSON logs to a central aggregator with retention and search |
| 23 | **Metrics** | Counters, gauges and histograms on a `/metrics` endpoint, a tiny time-series store |
| 24 | **Dashboard** | A web dashboard: node health, instances, request rates, error rates |
| 25 | **Detection rules** | Detections on your own audit logs: brute force, privilege escalation, enumeration. Sigma-style rules |
| 26 | **Ship to Wazuh** | Forward Nimbus logs to the Wazuh server in your home lab, and also run your C log analyzer on them |

**Milestone:** the observability stack with working alerts.
**Boss Fight 5:** a detection rule plus test logs for a new attack, from scratch.

### Phase 6: The app: deploy something real on your cloud
| # | Lesson | What you build |
|---|---|---|
| 27 | **The app: Drop** | A secure file-sharing web app for friends. Accounts, uploads into Nimbus storage, share links, and secrets from the Nimbus secrets manager |
| 28 | **Deploy manifests** | `nimbus deploy app.yaml`, which is infrastructure as code against your own API |
| 29 | **Load balancer** | An L7 reverse proxy with TLS termination, health checks and rate limiting (token bucket) |
| 30 | **CI/CD & supply chain** | GitHub Actions running tests, `ruff`, `bandit`, `pip-audit` and secret scanning on every push |

**Milestone:** Drop running on your Pi cluster, reachable from your devices (LAN or Tailscale).
**Stretch:** a cloud save and leaderboard endpoint for your JRPG from the C++ course.

### Phase 7: Break it, then harden it (purple team on your own cloud)
Everything in this phase targets your own lab only.

| # | Lesson | What you do |
|---|---|---|
| 31 | **Threat model** | STRIDE threat model of Nimbus, attack surface map |
| 32 | **OWASP lab** | A planted-vulnerability branch of Drop: IDOR, injection, broken auth, file upload abuse. Find, exploit, fix |
| 33 | **SSRF + metadata service** | Build an instance metadata service, then see how SSRF steals credentials from it (the Capital One breach pattern), then build the IMDSv2-style fix |
| 34 | **Hardening** | Least privilege everywhere, mTLS between services, container hardening, secret rotation |
| 35 | **Incident response** | Replay an attack, catch it using only your logs and detections, write an incident report |

**Milestone:** a security assessment report plus the hardened Nimbus v2. This is the main portfolio piece.

### Phase 8: Map it to the real cloud (Azure)
| # | Lesson | What you do |
|---|---|---|
| 36 | **Concept map** | Nimbus to Azure: Entra ID, RBAC, Blob Storage, Container Apps/VMs, NSGs, Key Vault, Monitor, Log Analytics, Sentinel |
| 37 | **Deploy to Azure** | Deploy Drop with the Azure SDK for Python, ship logs to Log Analytics, write KQL detections (the language Sentinel SOC analysts use daily) |

**Final project:** Nimbus 1.0 + Drop + the security write-up. It shows employers and clients that you
know how a cloud works from the inside, not just how to click through a portal.

---

## Algorithms thread
The C course builds data structures in `libquest/`. This course does not repeat that. Instead it uses
the algorithms clouds actually depend on, at the moment the cloud needs them:

| Algorithm / structure | Where Nimbus needs it |
|---|---|
| Hashing, content addressing | Blob store (L01), dedup |
| Hash chain / Merkle idea | Tamper-evident audit log (L15) |
| HMAC | Presigned URLs (L16), signed tokens (L13) |
| Heap / priority queue (`heapq`) | Scheduler picks the least-loaded node (L18) |
| Ring buffer (`collections.deque`) | Live log tail, recent-metrics window (L22, L23) |
| CIDR / prefix matching | Security group rules (L19) |
| Token bucket | Rate limiting in the load balancer (L29) |
| Consistent hashing | Spreading objects across storage nodes (L16 stretch) |
| LRU cache (`functools.lru_cache`, then your own) | Caching IAM decisions (L14) |

When a structure exists in both courses, the lesson compares your C version with Python's built-in.

---

## Cert and career tie-ins
- **Network+:** Phase 2 (TCP, HTTP, TLS, DNS) is Network+ material you see in Wireshark.
- **Security+:** IAM, crypto, hashing, PKI, logging, incident response (Phases 1, 3, 5, 7).
- **CySA+:** detection rules, log analysis, threat modeling, incident reports (Phases 5, 7).
- **Microsoft:** Phase 8 maps directly to AZ-900 / SC-900 concepts and the Sentinel/KQL work of a SOC analyst.

## Pace
Roughly 37 lessons plus 5 Boss Fights. At about 5 hours a week alongside the C/C++ course, plan on
7 to 9 months. See `DECISIONS.md` for how the time is split between the courses.
