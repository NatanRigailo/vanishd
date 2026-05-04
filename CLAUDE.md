# CLAUDE.md — `vanishd`

> Generated from the template `git/_templates/CLAUDE-projeto.md`
> This agent runs via **Claude Code** and has access to the filesystem and terminal tools.

---

## What this project is

Zero-knowledge secret sharing with one-time links — the server never sees the plaintext.

**Why it exists:** Demonstrates zero-knowledge architecture with client-side AES-GCM, the one-time token pattern, and a complete DevOps pipeline on top of a real security application.

**DevOps skills demonstrated in this project:**
- Zero-knowledge architecture: client-side crypto with the native Web Crypto API
- Multi-stage CI/CD: lint → SAST → build → scan → release → publish → deploy
- Container scanning with Trivy + SAST with Bandit
- Security hardening: rate limiting, secure headers, atomic delete, safe logging
- End-to-end self-hosted: GHCR + GitHub Actions free tier + deploy via Docker Compose

---

## Application stack

- **Language/runtime:** Python 3.12 / Flask
- **Database:** SQLite (stdlib `sqlite3`, Docker volume for persistence)
- **Server:** Waitress (production)
- **Frontend:** HTML + CSS + vanilla JavaScript — native Web Crypto API, zero external JS dependencies

---

## DevOps stack

- **CI/CD:** GitHub Actions
  - Stages: lint (flake8 + hadolint) → SAST (bandit) → build → scan (Trivy) → release (semver auto-tag) → publish (GHCR) → deploy
- **Registry:** GHCR (`ghcr.io/NatanRigailo/vanishd`)
- **Quality:** SonarCloud
- **Scan:** Trivy (CVEs on the image)
- **Dependencies:** Dependabot (pip weekly + actions weekly)
- **Reverse proxy:** not configured yet (Traefik/Nginx when moving to production)
- **Observability:** only `/healthz` for now — Prometheus+Grafana out of initial scope

---

## How it works — zero-knowledge architecture

### Link mode (key in the fragment)
```
[Sender browser]                       [Server]              [Recipient browser]
   generates AES-256-GCM key
   encrypts the secret (AES-GCM)
   POST /api/secrets {ciphertext} ──► stores encrypted blob
   receives {id}                       never saw the plaintext
   builds URL: /s/{id}#{base64(key)}
                                                              opens the link
                                                              extracts key from #fragment
                                                              GET /api/secrets/{id} ──► returns + deletes
                                                              decrypts locally with the key
                                                              displays the secret
                                                              (link invalid forever)
```

### Password mode (PBKDF2)
- Sender sets a password; JS derives the AES key via PBKDF2 (200k iterations, SHA-256)
- Random salt stored alongside the ciphertext (not a secret)
- Link does not contain the key — recipient types the password to derive and decrypt
- Server stores: `ciphertext + salt` — still never sees the plaintext

---

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | generated at runtime | Flask key for session/CSRF |
| `LOG_LEVEL` | `INFO` | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `MAX_TTL_SECONDS` | `604800` | Maximum allowed TTL (7 days) |
| `RATE_LIMIT_PER_MINUTE` | `20` | Requests per minute per IP on the read endpoint |
| `RATE_LIMIT_POST_PER_MINUTE` | `10` | Requests per minute per IP on the write endpoint |
| `MAX_CONTENT_LENGTH` | `65536` | Maximum request body size (bytes) |
| `CLEANUP_INTERVAL_SECONDS` | `3600` | Interval for the expired secrets cleanup job |
| `DATABASE_PATH` | `/data/vanishd.db` | SQLite file path |

---

## Roadmap

Milestones and issues are managed on GitHub: https://github.com/NatanRigailo/vanishd/milestones

### v0.1 — Foundation
- [ ] Initial project structure (folders, base files)
- [ ] Multi-stage non-root Dockerfile
- [ ] Flask app skeleton with `/healthz` and structured logging
- [ ] Initial SQLite schema

### v0.2 — Core Feature
- [ ] Client-side AES-GCM encryption via Web Crypto API
- [ ] API POST `/api/secrets` — receive and store encrypted blob
- [ ] API GET `/api/secrets/:id` — one-time read with atomic delete
- [ ] Link mode — AES key in the URL fragment
- [ ] Password mode — PBKDF2 derives the AES key from user password
- [ ] Minimal UI — create and view secrets

### v0.3 — CI Pipeline
- [ ] Lint stage (flake8 + hadolint)
- [ ] SAST with bandit
- [ ] Docker image build with cache
- [ ] Container scan with Trivy
- [ ] Dependabot for Python dependencies and Actions
- [ ] SonarCloud quality gate in CI

### v0.4 — Security Hardening
- [ ] Rate limiting on the read endpoint
- [ ] Secure HTTP headers (CSP, HSTS, X-Frame-Options)
- [ ] Cleanup job for expired secrets
- [ ] Access logging without exposing sensitive content

### v0.5 — Release & Deploy
- [ ] Semver auto-tag on merge to main
- [ ] Automatic image publish to GHCR
- [ ] Deploy workflow via docker compose on the host
- [ ] Final README with badges, quick start, and versioned roadmap

---

## Current state

**Version:** v1.1.0 ✅

**Completed milestones:**
- ✅ v0.1 — Foundation: structure, multi-stage non-root Dockerfile, Flask skeleton, SQLite schema
- ✅ v0.2 — Core Feature: AES-256-GCM client-side, POST/GET /api/secrets, link mode + password mode, minimal UI
- ✅ v0.3 — CI Pipeline: lint (flake8+hadolint), SAST (bandit), build+Trivy, SonarCloud, Dependabot, CODEOWNERS
- ✅ v0.4 — Security Hardening: rate limiting, secure headers + CSP without unsafe-inline, cleanup job, safe logging
- ✅ v0.5 — Release & Deploy: semver auto-tag, publish GHCR, deploy Render via webhook, README with badges
- ✅ v0.6 — Quality & Dev Experience: pre-commit hooks, actionlint, JS code smells, tests (97% coverage), /healthz DB check, rate limit POST, log injection sanitization
- ✅ v0.7 — Production Ready: PostgreSQL support via DATABASE_URL (_Conn wrapper, psycopg2-binary), pip-audit, gitleaks, fix libpq5 runtime (Render+Supabase via pooler IPv4 port 6543)
- ✅ v1.0 — UX & Full Pipeline: design system, favicon, local fonts, custom error pages (404/500/413/429), localStorage history with status badges, accessibility (fieldset+legend), DAST OWASP ZAP baseline in CI, CSRF via Content-Type enforcement (SonarCloud S4502), JS tests with Jest + lcov coverage
- ✅ v1.1 — UX Polish: reveal button — secret consumed only upon confirming click (link mode), view.js refactored and tested (15 tests, 100% coverage)

**Upcoming milestones:**
- v1.2 — Deploy Options: Docker Compose (#86) + Helm chart (#87)
- v1.3 — Observability: /metrics Prometheus (#88) + k6 load test (#89)
- v1.4 — Notifications: webhook on read Discord/Slack/Teams (#90)
- v1.5 — i18n: PT-BR / EN language switcher + DEFAULT_LANGUAGE env var (#95)

**Lessons learned:**
- `build-and-scan` needs `if: always() && ... (sast.result == 'success' || sast.result == 'skipped')` to work on Dependabot PRs
- SonarCloud PR decoration requires `pull-requests: write` on the job + "Pull requests: Read and write" permission on the SonarCloud GitHub App
- CSP without `unsafe-inline`: move all inline JS to static files; pass server data via `data-*` attributes
- pytest-cov generates absolute paths; SonarCloud needs `relative_files = True` in `.coveragerc`
- psycopg2-binary has no wheel for Python 3.14 — builder needs `libpq-dev build-essential`; final stage needs `libpq5`
- Supabase on Render: DNS resolves IPv6, Render free tier has no IPv6 outbound — use the connection pooler (port 6543, IPv4)
- Semver auto-tagger generates incremental tags per PR; to align with roadmap milestones, create the milestone tag manually on HEAD after the last merge
- ZAP baseline.py vs full-scan.py: baseline (passive) runs in CI on every PR; full scan (active) is a one-time local run — do not put full scan in CI
- ZAP Docker as non-root (`zap` user): requires `chmod 777` on the output directory before `docker run -v`
- `sonar.tests` does not accept subdirs that cause double-indexing — keep `sonar.tests=tests` and place JS tests inside `tests/js/`

---

## Agent role

This agent is an **executor** — not just an advisor. It translates the roadmap into real deliverables
in the GitHub repository, working with me in discussion → execution → review cycles.

### Standard workflow

1. **Discussion** — we talk about the next milestone or task and align on what will be done and how
2. **Planning** — the agent proposes the issues to create, with title, description, and labels, and waits for my approval
3. **Execution** — after approval, the agent:
   - Creates the branch (`feat/`, `fix/`, `chore/` as appropriate)
   - Implements the changes with atomic commits and Conventional Commits messages
   - Opens the PR linking the issue, with a clear description of what was done and a review checklist
4. **Review** — I review the PR and merge it. The agent never merges.
5. **Update** — after merge, the agent updates the state in CLAUDE.md if necessary

### What the agent does autonomously
- Read the repository state (`git log`, `git status`, `gh issue list`, `gh pr list`)
- Create and switch branches
- Write and edit files
- Make commits (atomic, with Conventional Commits messages)
- Create issues via `gh issue create`
- Open PRs via `gh pr create`
- Run lint, tests, and builds locally to validate before opening the PR

### What the agent asks before doing
- Creating issues in bulk (presents the full list for approval before executing)
- Any change that affects public application contracts (routes, environment variables, schema)
- Architecture choices not anticipated in the roadmap

### What the agent never does
- Merge PRs — always my responsibility
- Push directly to `main`
- Delete remote branches without confirmation
- Modify real secrets, tokens, or credentials

---

## Repository conventions

- **Branches:** `feat/short-description`, `fix/short-description`, `chore/short-description`
- **Commits:** Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `ci:`, `refactor:`)
- **PRs:** title in Conventional Commits format, description with context + checklist
- **Issues:** linked in the PR with `Closes #N`
- **Labels:** `feature`, `bug`, `ci`, `docs`, `security`, `infra`

---

## Environment prerequisites

For the agent to operate correctly via Claude Code:
- `git` configured with repository access
- `gh` CLI authenticated (`gh auth status`)
- Docker available locally (for validation builds)
- Variables from `.env.example` copied to `.env` with dev values

---

## References

- General standards: `../CLAUDE.md`
- Reference project: `../mfa-app`
- Issues: https://github.com/NatanRigailo/vanishd/issues
- Milestones: https://github.com/NatanRigailo/vanishd/milestones
